# Pipeline-in-a-Box -- ETL Template

The reusable extract/transform/load pattern every real client's pipeline will follow.
No real client exists yet -- this is scaffolded against realistic **synthetic** data for
a small auto-repair shop, one of the verticals already being scouted in
`../../business/02-icp-prospecting.md`.

This is the source-of-truth pattern. A `cloud-engineer`/`cdk-engineer` build happening in
parallel wires the AWS side (S3 landing bucket -> Lambda -> Aurora Postgres, reusing
`infra/`'s `DataAiBaselineStack`); this logic is written so it can be ported into that
Lambda's transform step close to as-is.

## What a small auto-repair shop's raw exports look like

Three files, in `data/raw/` -- chosen because they're what most shop-management
software (Tekmetric, Shopmonkey, Mitchell1, etc.) can actually export without asking the
shop to do anything unusual:

| File | Format | What it is |
|---|---|---|
| `customers.csv` | CSV | Customer list -- name, contact info, when they first showed up |
| `repair_orders.csv` | CSV | One row per repair order / job / ticket, vehicle info inline, dates + $ amounts |
| `payments.json` | JSON array | Payment transactions, from a payment processor export (Square/Stripe-shaped) |

15 customers, 30 repair orders (8 still open), 27 payments -- small enough to eyeball,
big enough to exercise every join in the schema (repeat customers, an open job with no
payment yet, a few multi-payment jobs). Regenerate with the script embedded in this
project's build history, or hand-edit the sample files directly for more test cases.

## The pipeline: extract -> transform -> load

```
etl/extract.py    Parses raw file CONTENTS (str) into plain dicts. No business rules,
                   no I/O beyond reading what it's handed. This is the seam that
                   changes shape in the Lambda -- there, "read the raw file" means an
                   S3 GetObject instead of Path.read_text(). Nothing else changes.

etl/transform.py  Cleans, type-coerces, and reshapes records using
                   config/field_mapping.json -- never a hardcoded column name. Pure
                   functions: (records, mapping) -> (clean records, warnings). Derives
                   dim_vehicle rows (deduped by VIN) from the repair-order export, since
                   most shops don't have a separate vehicle master file.

etl/load.py       Upserts clean rows into the target Postgres schema via pg8000 (see
                   "Driver choice" below). Every upsert is keyed on a natural/business
                   key, not the surrogate key -- see "Delivery guarantee" below.

etl/pipeline.py   run_pipeline() wires the three stages together in one DB transaction
                   per file drop (all dims+facts commit together or not at all). This
                   is the function to port into the Lambda handler. main() is the
                   local-only CLI entry point -- reads data/raw/, reads DB connection
                   info from env vars, and is explicitly NOT what gets ported (see its
                   docstring).
```

### Run it locally

```bash
pip install -r requirements.txt -r requirements-dev.txt

# point at any reachable Postgres 16 -- e.g. a throwaway Docker container:
docker run -d --name pib-test-pg -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_USER=dbadmin -e POSTGRES_DB=app -p 15432:5432 postgres:16-alpine
docker cp sql/schema.sql pib-test-pg:/schema.sql
docker exec pib-test-pg psql -U dbadmin -d app -f /schema.sql

DB_HOST=localhost DB_PORT=15432 DB_USER=dbadmin DB_PASSWORD=testpass DB_NAME=app \
  python -m etl.pipeline
```

This exact sequence was run during this build (Postgres 16-alpine in Docker) -- the DDL
applies cleanly, the pipeline loads all 15/30/30/27 rows with zero data-quality
warnings, a second run is a no-op (idempotent upsert verified), and revenue/job-volume/
retention/cash-flow-proxy queries against the loaded data all return sane numbers. See
"What's still open" for what that verification does and doesn't cover.

### Run the tests

```bash
python -m pytest tests/ -v
```

14 tests, no live database required:
- `test_extract_transform.py` -- extract/transform against the real synthetic sample
  files (row counts, cleaning, date parsing, the vehicle-dedup logic, the
  total-amount-reconciliation warning path, an invariant check that every payment
  references a *closed* repair order).
- `test_load_sql.py` -- parses `sql/schema.sql` and every `load.py` INSERT with
  `pglast` (a real `libpg_query`-based Postgres parser) and cross-checks that every
  column `load.py` inserts into actually exists in the schema. Catches a typo'd or
  renamed column even without a live database.

## Target schema (`sql/schema.sql`)

Star schema, designed for direct Power BI consumption -- a `bi-analyst` agent builds the
data model + DAX directly against this.

**Grain decisions (made explicit, not implied):**

| Table | Type | Grain |
|---|---|---|
| `dim_date` | dimension | one row per calendar day |
| `dim_customer` | dimension | one row per customer (SCD Type 1 -- see below) |
| `dim_vehicle` | dimension | one row per vehicle, FK to the owning customer |
| `fact_repair_order` | fact | one row per repair order / job / ticket |
| `fact_payment` | fact | one row per payment transaction |

**Why two fact tables, not one:** `fact_repair_order` is invoiced revenue and job
volume (what the shop billed). `fact_payment` is what actually got collected, and when
-- a repair order can have zero, one, or several payments against it. Keeping them
separate, joined through `repair_order_key`, is what lets a cash-flow-proxy measure
exist at all (`SUM(invoiced) - SUM(collected)`, or days between `close_date` and
`payment_date`) instead of collapsing "billed" and "paid" into one number.

**Keys:** every table has a `SERIAL` surrogate primary key for BI-friendly joins, plus a
`UNIQUE` natural/business key (`source_customer_id`, `source_vehicle_id`,
`source_ro_number`, `source_payment_id`) carried over from the client's source system.
The natural keys are what `load.py` upserts on -- see "Delivery guarantee" below.
Foreign keys are enforced (`REFERENCES ...`), not just implied by naming convention.

**Indexes:** every FK column on both fact tables, plus `status` on
`fact_repair_order` (used constantly for open-vs-closed filtering). Nothing else --
these are small tables for a single small business, not a place that needs aggressive
indexing.

**Verified against real Postgres 16**, not just pattern-matched: see "Run it locally"
above and the pglast-based static checks in `tests/test_load_sql.py`.

## Delivery guarantee: batch, at-least-once, idempotent upsert

Decided up front, not an afterthought:

- **Batch, not streaming.** A client's export is a periodic file drop (daily/weekly),
  not a continuous event stream. Nothing about this business needs sub-minute
  freshness, and building streaming infrastructure for a periodic file would be the
  exact "big data tooling nobody needs yet" mistake the `sql-data-engineering` skill
  warns against.
- **At-least-once, not exactly-once.** S3 event notifications and Lambda retries can
  redeliver the same file. This pipeline reports on money that already moved
  elsewhere (the shop's own POS/payment processor) -- it doesn't move money itself --
  so exactly-once isn't required. What IS required is that redelivery never produces
  duplicate rows, which is why every `load_*` function in `load.py` is an
  `INSERT ... ON CONFLICT (<natural key>) DO UPDATE`, not a plain `INSERT`. Verified
  by actually running the pipeline twice against a real database (see above) and
  confirming row counts didn't change.
- **One transaction per file.** `run_pipeline()` wraps all four loads (dims then
  facts) in a single `BEGIN`/`COMMIT`, with `ROLLBACK` on any failure -- a partial
  load never leaves a fact row pointing at a dimension row that didn't actually land.

## Driver choice: pg8000, not psycopg2

Matches this repo's existing decision for `infra/lambda_src/example_handler` (see
`.claude/skills/cdk-data-ai-stack/references/decisions.md`, "Lambda DB driver: pg8000,
not psycopg2"). pg8000 is pure Python -- no compiled C extensions -- so it installs
straight into a Lambda deployment package with `pip install -r requirements.txt -t .`,
no Docker asset bundling required. Uses pg8000's *native* API
(`Connection.run(sql, **params)`, `:name` placeholders) rather than its DB-API surface,
since the DB-API's paramstyle is positional-only (`%s`), which doesn't fit named-column
upserts as legibly.

## Onboarding a real client -- what changes, what doesn't

This is the point of building a template instead of a one-off script.

**Changes per client (the only things that should need to change):**
1. **Raw file shapes** -- a real client's export almost certainly has different column
   names, maybe a different format (Excel instead of CSV, a different JSON shape for
   payments). `extract.py`'s three `extract_*` functions may need a fourth format
   handler if a client's export isn't CSV/JSON at all (e.g. `extract_customers_xlsx`),
   but the *contract* (raw content in, list of dicts out) doesn't change.
2. **`config/field_mapping.json`** -- this is the whole point of the mapping-config
   layer. A new client = a new mapping file (`{canonical_field: their_column_name}`),
   not a code change. `transform.py` never hardcodes a source column name.
3. **Vertical-specific fields**, if the next client isn't an auto shop -- e.g. a salon
   might have "service" instead of "repair order" and "stylist" instead of
   "technician". The *shape* (a job/ticket fact with a date, a customer, an amount; a
   payment fact) is general enough to hold, but table/column naming may want a
   lighter-touch rename per vertical rather than forcing every vertical into
   auto-shop vocabulary. Decide this the first time a non-auto-shop client actually
   signs -- don't generalize further speculatively before that happens.

**Does NOT change:**
- `extract.py` / `transform.py` / `load.py` / `pipeline.py` function signatures and
  control flow.
- `sql/schema.sql`'s star-schema shape (dims + two facts, same grain).
- The delivery-guarantee design (batch, at-least-once, idempotent upsert, one
  transaction per file).
- The driver (pg8000) and the Lambda-portability constraint (dependency-light,
  pure-Python).

## What's still open (explicit, not glossed over)

- **No live AWS/Aurora verification yet.** Everything above was verified against a
  local throwaway Postgres 16 container (Docker), not the actual Aurora Serverless v2
  cluster `infra/` provisions. The SQL is standard Postgres (nothing Aurora-specific
  used), so this should transfer directly, but "should" isn't "did" -- worth a real
  `cdk deploy` + one live pipeline run before calling this production-ready.
- **Lambda porting itself hasn't happened.** This is Python code structured to be
  portable into `infra/lambda_src/`'s pattern, but no actual Lambda handler wraps
  `run_pipeline()` yet -- that's `cdk-engineer`'s parallel-track work
  (`infra/lambda_src/`), and then wiring `extract.py`'s file-reading seam to
  `s3.get_object()` instead of `Path.read_text()`.
- **`config/field_mapping.json` is a single hardcoded file**, not yet parameterized
  per client (e.g. loaded from S3 per client, or keyed by client ID). Fine for a
  single demo client; needs a real "which client is this file for" resolution
  mechanism (probably: S3 key prefix -> client ID -> which mapping config to load)
  once there's more than one client running through the same Lambda.
- **`dim_customer` is SCD Type 1 (overwrite on change).** If a client ever needs to
  answer "what was this customer's address as of the invoice date" (an SCD Type 2
  question), this schema doesn't support it yet -- not needed for the revenue/
  volume/retention/cash-flow dashboard this template targets, but worth flagging
  before assuming customer attributes are point-in-time-accurate.
- **No vertical besides auto-repair has been tried.** See "Onboarding a real client"
  above -- the schema shape should generalize, but that's a claim, not something
  tested against a second vertical yet.
- **No CI running these tests automatically.** `python -m pytest tests/` is a manual
  step right now, matching the rest of this repo's current state (`infra/` also has
  no CI yet, per its own decisions log).
