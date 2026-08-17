# Decisions

Append-only architecture decision log. Newest first. Don't edit past entries when a
decision changes — add a new dated entry that supersedes it and say so; the history
of *why* is the point.

---

## 2026-08-16 — Pipeline-in-a-Box plugs into the existing baseline stack, not a new one

**Decision:** the S3 landing bucket + transform Lambda pattern
(`LandingBucketConstruct`, `TransformLambdaConstruct`, `ClientPipelineConstruct`)
gets composed inside `DataAiBaselineStack` itself — via a new `clients:
list[ClientPipelineConfig]` constructor argument that instantiates one
`ClientPipelineConstruct` per client — rather than a separate
`PipelineInABoxStack` with its own `NetworkConstruct`/`DatabaseConstruct`.
**Why:** the whole point is one shared VPC + one shared Aurora cluster serving
every client's pipeline, not a second VPC/Aurora cluster per product line. A
separate stack would mean either duplicating Network/Database (defeats the
purpose, doubles Aurora's cost floor per `decisions.md`'s open Serverless v2
question) or cross-stack references (adds CloudFormation export/import
complexity for no real benefit at this stage, since nothing is deployed yet
and there's exactly one environment). Revisit if Pipeline-in-a-Box ever needs
genuinely different infra (different DB engine, its own VPC) — at that point
`conventions.md`'s "Multiple projects on this baseline" split applies and it
should get its own stack/file, same as any other diverging `lab/` project.
**See also:** `s3-patterns.md` for the full config shape and the two
sub-decisions this depended on (why a construct not a stack subclass for
per-client parameterization, why S3-event trigger not scheduled batch).

## 2026-08-16 — Multi-tenant parameterization: one config dataclass, one construct

**Decision:** a single `ClientPipelineConfig` dataclass
(`infra/infra/constructs/client_config.py`) is the entire parameterization
surface for onboarding a client — `client_id` plus optional overrides
(`bucket_name_prefix`, `target_schema`, `target_table`, `source_prefix`,
`file_suffixes`) — fed into one reusable `ClientPipelineConstruct`. Real
onboarding is "construct a config, instantiate the construct," not "copy a
stack file and hand-edit it."
**Why a construct, not a stack subclass:** a `Stack` subclass per client would
mean either a separate `cdk deploy` per client (operationally heavier for
what's meant to be a repeatable, low-friction product) or importing shared
VPC/DB across stacks (cross-stack references — same cost/complexity argument
as the entry above). A construct composes into the *existing* stack for free.
**Why one config dataclass instead of many constructor kwargs spread across
`LandingBucketConstruct`/`TransformLambdaConstruct`/`ClientPipelineConstruct`:**
keeps the three constructs' signatures stable as fields get added later (add a
field to `ClientPipelineConfig`, not to three constructor signatures), and
gives `cloud-engineer`/`data-engineer` collaborators building the actual ETL
logic (`lab/pipeline-in-a-box/engineering/etl-template/`) exactly one object
to know about. Validation (`client_id`/`target_schema`/`target_table` must be
safe S3-prefix/SQL-identifier characters) lives in the dataclass's
`__post_init__`, so a bad client_id fails at `cdk synth` time, not
mid-deploy or (worse) inside the Lambda at runtime.
**Not yet decided:** whether a second onboarding surface (e.g. a small CLI or
a config file the app reads instead of hand-editing `app.py`) is worth adding
— open until there's a second real client to onboard and a sense of how
annoying `app.py` edits actually are in practice.

## 2026-08-13 — Language: Python

**Decision:** CDK app written in Python, not TypeScript.
**Why:** matches the language used for Lambda handlers and SQL tooling
(SQLAlchemy/alembic, if adopted later) — one language across infra and application
code, rather than TypeScript for infra + Python for everything data/AI touches.
**Tradeoff accepted:** CDK's most mature docs/examples skew TypeScript; Python
support is solid but occasionally lags new construct APIs by a release or two.

## 2026-08-13 — Location: top-level `infra/`, not under `lab/`

**Decision:** infra lives in `infra/` at repo root, separate from `lab/`.
**Why:** it has a different deploy lifecycle (`cdk deploy` to AWS) than everything
else in this repo (the site deploys via GitHub Pages on push; `lab/` projects don't
deploy at all by default). Treating it as a `lab/` entry would blur that.
**How to apply:** future `lab/` projects that need AWS infra reference/extend
`infra/`, they don't get their own independent CDK app unless they diverge enough to
warrant it (see `conventions.md`, "Multiple projects on this baseline").

## 2026-08-13 — Network: no NAT gateway

**Decision:** baseline VPC uses isolated subnets only, `nat_gateways=0`.
**Why:** NAT gateways bill hourly regardless of traffic (~$32-35/mo alone as of last
check) — not worth it for a low-traffic personal project's baseline. Nothing in the
baseline needs outbound internet access from the VPC yet.
**Revisit when:** something in the VPC needs to call an external API (not an AWS
service reachable via VPC endpoint). At that point, either add a NAT gateway
(cost) or a VPC endpoint for the specific AWS service needed (cheaper, if it's AWS).

## 2026-08-13 — Database: Aurora Serverless v2 Postgres (open tradeoff, not final)

**Decision:** baseline database construct uses Aurora Serverless v2 Postgres,
min capacity 0.5 ACU.
**Why:** "modern" CDK+Lambda+SQL baselines commonly reach for this; scales with load
without manual instance sizing.
**Known tradeoff — NOT fully resolved:** Serverless v2 has an always-on capacity
floor (roughly $40-50/mo minimum as of last check, unlike Serverless v1 which could
pause to $0). A plain `db.t4g.micro` RDS Postgres instance is free-tier eligible for
12 months and may be cheaper for a low-traffic personal project. **This has not been
deployed or paid for yet** — decide before the first real `cdk deploy` whether
Serverless v2's operational simplicity is worth the cost floor, or switch the
`DatabaseConstruct` to a plain `rds.DatabaseInstance`. See `sql-patterns.md`.

## 2026-08-13 — Lambda DB driver: pg8000, not psycopg2

**Decision:** `lambda_src/example_handler/requirements.txt` specifies `pg8000`, not
`psycopg2-binary`.
**Why:** pg8000 is pure Python with no compiled C extensions, so it can be installed
straight into the Lambda asset folder (`pip install -t .`) without Docker bundling.
psycopg2 needs a Linux-compatible compiled build, which means CDK's Docker asset
bundling (Docker is available on this machine, but it adds a build step / slower
`cdk synth`-adjacent packaging and a dependency on Docker actually running).
**Not yet done:** the handler doesn't import pg8000 yet — it only proves the wiring
(VPC + Secrets Manager). Adding the real query is the next step once there's a schema.

## Open questions

- Serverless v2 vs. plain RDS instance for cost — see entry above. Decide before
  first deploy.
- No CI/CD for `infra/` yet (no GitHub Actions running `cdk diff`/`cdk deploy`) —
  deploys are manual (`cdk deploy` from a dev machine) until this is set up.
- No multi-environment story yet (dev/prod). Currently one environment-agnostic
  stack. Revisit once there's a reason to need two.
- **Secrets Manager is unreachable from `PRIVATE_ISOLATED` subnets** — every
  Lambda that reads the DB secret (`ExampleLambdaConstruct`, and now
  `TransformLambdaConstruct`) calls `secretsmanager:GetSecretValue` over the
  network, but there's no NAT gateway and no Secrets Manager VPC endpoint.
  This has not been caught because nothing has been deployed for real yet —
  it will surface as a Lambda timeout on first real invocation post-deploy.
  Fix options: a Secrets Manager Interface VPC endpoint (real hourly cost,
  ~$7-10/mo per AZ) or a NAT gateway (the cost this repo has specifically
  avoided so far, see "Network: no NAT gateway" above). Decide before the
  first Lambda that reads a DB secret actually gets invoked for real. See
  `s3-patterns.md` for where this was (re-)surfaced.
