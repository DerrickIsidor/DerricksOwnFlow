# SQL / Database Patterns

## Current baseline: Aurora Serverless v2 Postgres

`DatabaseConstruct` (`infra/infra/constructs/database.py`) provisions a single-writer
Aurora Serverless v2 Postgres cluster, `min_capacity=0.5` / `max_capacity=2`, in
isolated subnets, with a Secrets Manager-generated credential (`rds.Credentials.
from_generated_secret`) — never a hardcoded password.

**This has an open cost tradeoff — see `decisions.md`, "Database: Aurora Serverless
v2 Postgres".** Decide (and update this file + the construct) before the first real
deploy:
- **Keep Serverless v2** if you want it to handle load spikes without thinking about
  instance sizing, and the ~$40-50/mo floor is acceptable.
- **Switch to a plain `rds.DatabaseInstance`** (e.g. `db.t4g.micro`, Postgres) if
  minimizing cost matters more right now — free-tier eligible for 12 months on a new
  AWS account. Swap `writer=rds.ClusterInstance.serverless_v2(...)` and
  `DatabaseCluster` for `rds.DatabaseInstance` with an equivalent engine/credentials
  setup; the secret-injection and Lambda-wiring pattern in `lambda-patterns.md` stays
  the same either way.

## Schema / migrations

Not yet set up. No migration tool chosen. `alembic` (pairs naturally with
`psycopg2`/`pg8000` + Python) is the likely default if/when this is needed — record
the actual decision here once made, don't assume this note is a decision.

## Connecting from a Lambda

`lambda_src/example_handler/handler.py` still only proves it can read the DB secret
from Secrets Manager — it doesn't open a connection.

`lambda_src/transform_handler/handler.py` (Pipeline-in-a-Box's transform Lambda, see
`s3-patterns.md`) is the first Lambda in this repo to actually open a `pg8000`
connection and run queries: `pg8000.dbapi.connect(host=..., port=..., database=...,
user=..., password=...)` using the DB-API 2.0 interface (`%s` placeholders,
`cursor.execute(sql, params)`), reading host/user/password out of the same
Secrets Manager secret JSON as `example_handler`. It lands rows into a generic
`(client_id, source_key, ingested_at, payload JSONB)` table via a runtime
`CREATE TABLE IF NOT EXISTS` — explicitly a stand-in for real migration tooling
(see below), not a real schema design. **Not yet done:** SSL/TLS is not enforced on
this connection — pg8000's exact `ssl_context`/`ssl` parameter shape wasn't verified
against a real deploy, so it was left as an explicit TODO in the handler rather than
guessed at (see `s3-patterns.md` "Open questions").

Still open: whether to use RDS Proxy for connection pooling if concurrent Lambda
invocations become a concern (not needed at low traffic — plain per-invocation
connections are fine to start).

## Open questions

- Serverless v2 vs. plain instance — see above, decide before first deploy.
- No migration tooling chosen yet.
- No RDS Proxy — not needed until connection-count pressure is an actual, observed
  problem, not a hypothetical one.
