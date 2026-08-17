---
name: sql-data-engineering
description: Use whenever the task involves SQL (writing or reviewing queries, schema design, joins, window functions, CTEs), ETL/ELT pipeline design, data warehousing (fact/dimension tables, star schema, OLTP vs OLAP), choosing between streaming and batch processing, or deciding whether a project actually needs "big data" tooling at all. Make sure to reach for this skill any time the user mentions databases, pipelines, data modeling, Postgres/Aurora, Hive/Spark/Hadoop, or "how should I structure this data" — even if they don't say "data engineering" explicitly. Pairs with cdk-data-ai-stack for this repo's actual AWS/Postgres implementation.
---

# SQL & Data Engineering

Practical data-plumbing knowledge for Derrick's stack: Python + SQL + AWS (Aurora
Serverless v2 Postgres, see `infra/`). This skill is the general "how data pipelines and
databases work" reference. For how *this repo's* infra is actually built, load
`cdk-data-ai-stack` instead — it has the real conventions, decisions, and SQL patterns
for `infra/`. Use both together when a task touches both.

## Core SQL — the patterns that come up constantly

```sql
-- Joins: pick the one that matches what you actually want kept
SELECT a.*, b.col FROM a INNER JOIN b ON a.id = b.a_id;   -- only matching rows
SELECT a.*, b.col FROM a LEFT JOIN b ON a.id = b.a_id;    -- all of a, matched b or NULL
-- FULL OUTER JOIN, CROSS JOIN exist too — reach for them rarely, they're usually a modeling smell

-- Aggregation
SELECT customer_id, COUNT(*) AS orders, SUM(total) AS revenue
FROM orders
GROUP BY customer_id
HAVING SUM(total) > 1000;   -- filters groups, not rows — WHERE can't do this

-- Window functions — the thing people under-use. Solves "top N per group",
-- running totals, and period-over-period without a self-join.
SELECT customer_id, order_date, total,
       SUM(total) OVER (PARTITION BY customer_id ORDER BY order_date) AS running_total,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
FROM orders;
-- rn = 1 gives you "most recent order per customer" without a subquery+MAX dance

-- CTEs for readability — prefer these over nested subqueries once a query has
-- more than one layer of transformation
WITH monthly AS (
  SELECT date_trunc('month', order_date) AS mon, SUM(total) AS revenue
  FROM orders GROUP BY 1
)
SELECT mon, revenue, revenue - LAG(revenue) OVER (ORDER BY mon) AS mom_change
FROM monthly;
```

Constraints and keys: always give tables a `PRIMARY KEY`; use `FOREIGN KEY` to make
relationships explicit and let the database enforce them instead of trusting application
code. Index columns that show up in `WHERE`/`JOIN`/`ORDER BY` on large tables — but don't
index everything, each index costs write performance and storage.

## ETL vs ELT

- **ETL** (Extract, Transform, Load): transform data *before* it lands in the warehouse.
  Classic pattern, still right when the destination is weak at transforms or the source
  needs heavy cleaning/PII-scrubbing before it's allowed to land anywhere.
- **ELT** (Extract, Load, Transform): load raw data first, transform in place with SQL
  (dbt is the standard tool for this). Preferred on modern cloud warehouses because
  storage is cheap and the warehouse's own compute is usually faster than a separate
  transform layer. Default to this unless there's a specific reason not to.

## Data warehousing fundamentals

**OLTP vs OLAP** — don't confuse the two:
- OLTP (Postgres/Aurora running the app): optimized for many small, fast read/write
  transactions. Normalized schema (3NF) to avoid update anomalies.
- OLAP (a warehouse for analytics): optimized for large aggregate scans over historical
  data. Denormalized on purpose — a star schema trades storage for query simplicity/speed.

**Star schema** — the standard shape for analytics:
- **Fact table**: one row per event/transaction (a sale, a page view). Mostly foreign
  keys + measures (amounts, counts). This is the big table.
- **Dimension tables**: descriptive context (customer, product, date). Small, wide,
  denormalized. A **Date/Calendar dimension** with one row per day (and precomputed
  Year/Quarter/Month/FiscalYear columns) is worth building once, always — every BI tool's
  time-intelligence functions depend on having one (see `powerbi-dax-excel` for the DAX
  side of this).
- Classify every new table as fact or dimension before writing DDL — it drives whether it
  should be wide/denormalized (dimension) or narrow/append-heavy (fact).

**Data warehouse vs data lake**: a warehouse stores structured, schema-on-write data for
known analytics questions. A lake stores raw data (any format) schema-on-read, for
questions you haven't thought of yet or don't want to pre-clean for. Most real platforms
end up with both — land raw in a lake/blob store, curate into a warehouse for BI.

## Batch vs streaming — and why it matters more than the buzzword

Three delivery guarantees, and getting this wrong is expensive:
- **At-least-once**: a message may be processed more than once, never dropped. Fine when
  reprocessing is idempotent (e.g., a GPS ping keyed by timestamp — reprocessing just
  overwrites with the same value).
- **At-most-once**: may drop a message, never double-processes. Fine when a duplicate
  would be actively wrong (e.g., counting a discrete event twice) and occasional loss is
  tolerable.
- **Exactly-once**: never drop, never duplicate. Required for anything involving money —
  and is genuinely hard to implement; don't promise it casually.

Decide which guarantee a pipeline needs *before* picking a tool — not every streaming
tool supports all three, and retrofitting exactly-once semantics onto an at-least-once
pipeline is a rewrite, not a config change.

**Lambda architecture**: run both a batch layer (recomputes the full historical picture
periodically, high latency, complete accuracy) and a speed/streaming layer (low-latency
partial view of very recent data) side by side, merging views at query time. Reach for
this only when you actually need sub-minute freshness on top of a reliable historical
batch pipeline — it doubles the pipelines you maintain.

## Should this even use "big data" tools?

Most projects shouldn't. A single well-tuned Postgres/Aurora instance (Derrick's actual
stack — see `infra/`) comfortably handles up to tens of millions of rows and gigabytes of
data with correct indexing. Reach for Hadoop/Spark/a distributed warehouse only when:
- A single database server, scaled up (more CPU/RAM/faster disk), genuinely can't keep
  up with query or ingestion volume — not "might someday."
- The team can afford the *operational* cost: a real Hadoop cluster needs 5+ servers to
  be viable, plus the maintenance overhead, on top of the analytics tooling itself.

Planning for "catastrophic success" (exponential growth outpacing the platform) is worth
doing on paper before it happens — but don't pre-build big-data infrastructure for
traffic that doesn't exist yet. Scale up before you scale out.

## When building this repo's actual pipelines

Load `cdk-data-ai-stack`'s `references/sql-patterns.md` before writing schema or
migrations in `infra/` — it has this repo's real conventions (naming, migration style,
what's already decided) rather than generic advice. This skill is the "how SQL/ETL/
warehousing works" layer; that skill is the "how *this* stack does it" layer.
