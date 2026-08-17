# S3 & Multi-Tenant Patterns

Patterns for S3-backed infra in `infra/`, and for parameterizing a construct
per client (first used by "Pipeline-in-a-Box": `LandingBucketConstruct`,
`TransformLambdaConstruct`, `ClientPipelineConstruct`, `ClientPipelineConfig`
in `infra/infra/constructs/`).

## Landing bucket defaults

`LandingBucketConstruct` (`infra/infra/constructs/landing_bucket.py`) is the
reference for any S3 bucket meant to receive external/client data. Defaults
chosen deliberately for a productized service handling other people's data:

- `block_public_access=s3.BlockPublicAccess.BLOCK_ALL` and `enforce_ssl=True`
  — always, not optional.
- `versioned=True` — protects against a bad re-upload silently clobbering
  data before it's been loaded.
- `encryption=s3.BucketEncryption.S3_MANAGED` — SSE-S3, no extra KMS key
  management for a baseline; revisit if a client ever requires
  customer-managed keys.
- `removal_policy=RemovalPolicy.RETAIN` (default, overridable) — raw client
  data should never disappear because a stack got updated/deleted. This is
  stricter than `DatabaseConstruct`'s `RemovalPolicy.SNAPSHOT` — a bucket has
  no snapshot equivalent, so RETAIN is the closest "don't lose this" option.
- Bucket name: left unset (`bucket_name=None`) by default so CDK
  auto-generates a globally-unique physical name. Only set an explicit name
  (via `ClientPipelineConfig.bucket_name_prefix`) if a predictable bucket
  name is actually needed — S3 names are a single global namespace across
  *all* of AWS, not just this account, so collisions are a real risk with a
  hand-picked name.

## S3 access from isolated subnets: Gateway endpoint, not NAT

`NetworkConstruct` (`infra/infra/constructs/network.py`) adds an S3 Gateway
VPC Endpoint (`ec2.GatewayVpcEndpointAwsService.S3` via
`vpc.add_gateway_endpoint(...)`). This is what lets a Lambda in
`PRIVATE_ISOLATED` subnets (no NAT gateway, no route to the internet — see
`decisions.md` "Network: no NAT gateway") reach S3 at all.

**Why this doesn't break the "no NAT gateway" cost decision:** Gateway VPC
endpoints (S3 and DynamoDB only) have **no hourly charge**, unlike Interface
endpoints (~$0.01/hr per AZ, i.e. real money) and unlike NAT gateways. They
work by adding a route table entry, not a metered ENI. Safe to add freely for
S3/DynamoDB; treat any other AWS service's *Interface* endpoint as a real
cost decision, not a default.

**Known gap this does NOT fix:** the transform Lambda (and the pre-existing
`ExampleLambdaConstruct`) also calls Secrets Manager
(`secrets_client.get_secret_value`) to read the DB credential, and Secrets
Manager has no Gateway endpoint option — only a paid Interface endpoint, or a
NAT gateway, gets an isolated-subnet Lambda to it. **This has not been fixed
and is not yet caught by anything**, because nothing in this repo has been
deployed for real yet (see `setup-checklist.md`). It will surface as a
timeout the first time either Lambda actually runs post-deploy. See "Open
questions" below and in `decisions.md`.

## Multi-tenant parameterization (2026-08-16)

**Decision:** one config object (`ClientPipelineConfig`, a dataclass in
`infra/infra/constructs/client_config.py`) feeds one reusable construct
(`ClientPipelineConstruct`), instantiated once per client from a `clients:
list[ClientPipelineConfig]` argument on `DataAiBaselineStack`. Real client
onboarding is meant to look like:

```python
ClientPipelineConstruct(
    self, "ClientPipelineAcmeCo",
    vpc=network.vpc, db_secret=database.secret, db_name="app",
    config=ClientPipelineConfig(client_id="acme-co"),
)
```

not a new stack and not a copy-pasted construct file. See `decisions.md` for
the full rationale (why a construct instead of a stack subclass, why one
config object instead of many keyword args) — this file just documents the
resulting shape and how to extend it.

`ClientPipelineConfig` fields and what they drive:

| Field | Drives | Default |
|---|---|---|
| `client_id` | S3 key prefix, Postgres table name, part of bucket name if set | required; validated `^[a-z0-9][a-z0-9-]{0,48}$` |
| `bucket_name_prefix` | explicit landing bucket name (`<prefix>-<client_id>-landing`) | `None` → CDK auto-generates a name |
| `target_schema` | Postgres schema loaded rows land in | `"public"` |
| `target_table` | Postgres table loaded rows land in | `f"{client_id}_raw"` (hyphens → underscores) |
| `source_prefix` | S3 key prefix that must match to trigger the transform Lambda | `f"{client_id}/"` |
| `file_suffixes` | file extensions that trigger the transform Lambda | `(".csv", ".json")` |

All of `client_id`/`target_schema`/`target_table` are validated in
`ClientPipelineConfig.__post_init__` (fails at `cdk synth` time, not deploy
time) before being used to build S3 names or interpolated into SQL DDL/DML in
the Lambda handler.

**One construct instance per client, not one bucket/Lambda shared across
clients.** Each client gets their own bucket and their own Lambda function
(sharing the same VPC and Aurora cluster). Simpler IAM (no cross-client S3
prefix-scoped policies to get right), simpler blast radius if one client's
data is malformed, and avoids one client's `add_event_notification` filter
rules interfering with another's. Revisit only if the per-client resource
count becomes a real AWS soft-limit concern (unlikely at small-business
client counts).

## S3-event trigger, not scheduled batch (2026-08-16)

**Decision:** the transform Lambda is triggered directly by S3
`OBJECT_CREATED` events (via `bucket.add_event_notification`, one
notification rule per `file_suffixes` entry — S3 filters AND a prefix+suffix
within one rule, they don't OR across multiple suffixes), not by an
EventBridge schedule that periodically scans for "recently landed" files.
**Why:** a schedule-based "load recent files" pattern needs its own
bookmarking/dedup state (which files were already processed) to avoid
double-loading on every run — extra state to design and get right for no
benefit at this stage. Direct S3 events are simpler (no missed-file window,
no dedup bookkeeping) and near-real-time, which also reads better for a
client-facing product ("upload it and it just shows up"). **Revisit if:** a
future client's extract process lands many small files in bursts and
per-object Lambda invocations become noisy/costly, or if a client wants
batched/windowed loads instead of per-file loads.

## Open questions

- Secrets Manager reachability from isolated subnets (see "Known gap" above)
  — not fixed. Needs a decision (NAT gateway, Secrets Manager Interface VPC
  endpoint, or some other approach) before the first real deploy of anything
  that reads a DB secret from a Lambda, not just Pipeline-in-a-Box.
- SSL/TLS to Aurora isn't enforced yet from `transform_handler`'s pg8000
  connection (see that handler's `_get_db_connection` docstring) — pg8000's
  exact SSL parameter shape wasn't verified against a real deploy, left as an
  explicit TODO rather than guessed at.
- No bucket lifecycle/retention policy beyond aborting incomplete multipart
  uploads after 7 days — real per-client data retention requirements are
  unknown until a real client exists.
- `transform_handler`'s `load()` lands everything into a generic
  `(client_id, source_key, ingested_at, payload JSONB)` table via a
  `CREATE TABLE IF NOT EXISTS` at runtime — a stand-in for real migration
  tooling (see `sql-patterns.md`, migration tool still not chosen). Fine for
  a scaffold; revisit once schema ownership moves to a real migration tool.
