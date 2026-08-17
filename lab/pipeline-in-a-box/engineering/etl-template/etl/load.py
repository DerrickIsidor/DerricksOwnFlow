"""LOAD -- upsert clean, transformed rows into the target Aurora Postgres schema
(sql/schema.sql).

Driver choice: pg8000, not psycopg2 -- matching this repo's existing decision for
`infra/lambda_src/example_handler` (see
../../../.claude/skills/cdk-data-ai-stack/references/decisions.md, "Lambda DB
driver: pg8000, not psycopg2"). pg8000 is pure Python, so it installs straight into
a Lambda deployment package (`pip install -t .`) with no Docker/Linux-compiled-build
step -- important once this logic is ported into the Lambda transform step.

Uses pg8000's *native* API (`pg8000.native.Connection.run(sql, **params)`, `:name`
placeholders), not its DB-API surface -- pg8000's DB-API paramstyle is positional
`%s` only, which doesn't fit named-column upserts as legibly. Verified against the
installed pg8000 1.31.5 (`pip show pg8000`) rather than assumed from memory.

Delivery guarantee this load layer is designed for: BATCH, AT-LEAST-ONCE.
  * A client's raw export lands periodically (daily/weekly file drop to S3 in the
    real pipeline), not a continuous stream -- batch, not streaming.
  * S3 event notifications / Lambda retries can redeliver the same file more than
    once. Every load_* function below is an idempotent UPSERT keyed on the natural
    business key from the source system (source_customer_id, source_vehicle_id,
    source_ro_number, source_payment_id), each declared UNIQUE in sql/schema.sql --
    so reprocessing the same file is safe: rows get overwritten with the same
    values, not duplicated.
  * Exactly-once is NOT required here and is not implemented -- this pipeline
    reports on money that has already moved elsewhere (the shop's own systems), it
    doesn't move money itself. At-least-once + idempotent upsert gives the same
    practical result (no duplicate rows) without the cost of building true
    exactly-once semantics. See the sql-data-engineering skill's "Batch vs
    streaming" section for why that distinction matters.

Transaction control lives in the CALLER (pipeline.py), not in these functions --
one client file should load as a single all-or-nothing transaction (dims and facts
together), not table-by-table, so a failure partway through never leaves the
warehouse with facts pointing at dimension rows that didn't make it in. See
`run_pipeline` in pipeline.py for the BEGIN/COMMIT/ROLLBACK wrapper.

Load order matters -- dimensions before the facts that reference them:
  dim_customer -> dim_vehicle -> fact_repair_order -> fact_payment
"""
from __future__ import annotations

from datetime import date
from typing import Any, Protocol


class NativeConnection(Protocol):
    """Structural type for pg8000.native.Connection -- lets tests pass a fake
    object with a matching .run() instead of requiring pg8000 to be installed
    just to unit-test transform/load call shape."""

    def run(self, sql: str, **params: Any) -> list[list[Any]]: ...


def get_connection(secret: dict[str, Any], dbname: str | None = None) -> NativeConnection:
    """Open a pg8000 native connection from a Secrets Manager-shaped credential dict.

    `secret` is the shape `rds.Credentials.from_generated_secret(...)` produces
    (host, port, username, password, dbname) -- i.e. exactly what the Lambda will
    get back from `secretsmanager.get_secret_value` per
    ../../../.claude/skills/cdk-data-ai-stack/references/lambda-patterns.md. Kept as
    a thin wrapper so the Lambda handler and local runs both go through one place.
    """
    import pg8000.native  # local import: keeps this module importable for unit
    # tests (transform/extract) without pg8000 installed in that environment.

    return pg8000.native.Connection(
        user=secret["username"],
        password=secret["password"],
        host=secret["host"],
        port=int(secret.get("port", 5432)),
        database=dbname or secret.get("dbname", "app"),
    )


def _date_key(d: date | None) -> int | None:
    return int(d.strftime("%Y%m%d")) if d else None


def load_customers(conn: NativeConnection, rows: list[dict[str, Any]]) -> int:
    """Upsert dim_customer rows. Returns the number of rows submitted."""
    sql = """
        INSERT INTO dim_customer (
            source_customer_id, first_name, last_name, full_name, email, phone,
            address_line1, city, state, postal_code, customer_since_date
        ) VALUES (
            :source_customer_id, :first_name, :last_name, :full_name, :email, :phone,
            :address_line1, :city, :state, :postal_code, :customer_since_date
        )
        ON CONFLICT (source_customer_id) DO UPDATE SET
            first_name          = EXCLUDED.first_name,
            last_name           = EXCLUDED.last_name,
            full_name           = EXCLUDED.full_name,
            email                = EXCLUDED.email,
            phone                = EXCLUDED.phone,
            address_line1       = EXCLUDED.address_line1,
            city                 = EXCLUDED.city,
            state                = EXCLUDED.state,
            postal_code          = EXCLUDED.postal_code,
            customer_since_date = EXCLUDED.customer_since_date,
            load_timestamp       = now()
    """
    for row in rows:
        conn.run(sql, **row)
    return len(rows)


def load_vehicles(conn: NativeConnection, rows: list[dict[str, Any]]) -> int:
    """Upsert dim_vehicle rows. Resolves customer_key from dim_customer via the
    natural key (source_customer_id) rather than requiring the caller to already
    know the surrogate key -- the surrogate key is a database-internal detail the
    transform stage should never need to see."""
    sql = """
        INSERT INTO dim_vehicle (
            source_vehicle_id, customer_key, vehicle_year, vehicle_make, vehicle_model
        )
        SELECT :source_vehicle_id, c.customer_key, :vehicle_year, :vehicle_make, :vehicle_model
        FROM dim_customer c
        WHERE c.source_customer_id = :source_customer_id
        ON CONFLICT (source_vehicle_id) DO UPDATE SET
            customer_key   = EXCLUDED.customer_key,
            vehicle_year   = EXCLUDED.vehicle_year,
            vehicle_make   = EXCLUDED.vehicle_make,
            vehicle_model  = EXCLUDED.vehicle_model,
            load_timestamp = now()
    """
    for row in rows:
        conn.run(
            sql,
            source_vehicle_id=row["source_vehicle_id"],
            source_customer_id=row["source_customer_id"],
            vehicle_year=row["vehicle_year"],
            vehicle_make=row["vehicle_make"],
            vehicle_model=row["vehicle_model"],
        )
    return len(rows)


def load_repair_orders(conn: NativeConnection, rows: list[dict[str, Any]]) -> int:
    """Upsert fact_repair_order rows. Resolves customer_key / vehicle_key via
    natural keys, and open/close date_key via dim_date -- the date dimension must
    already be populated (sql/schema.sql's generate_series block) wide enough to
    cover every date in this file."""
    sql = """
        INSERT INTO fact_repair_order (
            source_ro_number, customer_key, vehicle_key, open_date_key, close_date_key,
            status, technician, labor_amount, parts_amount, tax_amount, total_amount,
            days_to_close
        )
        SELECT
            :source_ro_number, c.customer_key, v.vehicle_key,
            :open_date_key, :close_date_key,
            :status, :technician, :labor_amount, :parts_amount, :tax_amount,
            :total_amount, :days_to_close
        FROM dim_customer c
        JOIN dim_vehicle v ON v.source_vehicle_id = :source_vehicle_id
        WHERE c.source_customer_id = :source_customer_id
        ON CONFLICT (source_ro_number) DO UPDATE SET
            customer_key    = EXCLUDED.customer_key,
            vehicle_key     = EXCLUDED.vehicle_key,
            open_date_key   = EXCLUDED.open_date_key,
            close_date_key  = EXCLUDED.close_date_key,
            status          = EXCLUDED.status,
            technician      = EXCLUDED.technician,
            labor_amount    = EXCLUDED.labor_amount,
            parts_amount    = EXCLUDED.parts_amount,
            tax_amount      = EXCLUDED.tax_amount,
            total_amount    = EXCLUDED.total_amount,
            days_to_close   = EXCLUDED.days_to_close,
            load_timestamp  = now()
    """
    for row in rows:
        conn.run(
            sql,
            source_ro_number=row["source_ro_number"],
            source_customer_id=row["source_customer_id"],
            source_vehicle_id=row["source_vehicle_id"],
            open_date_key=_date_key(row["open_date"]),
            close_date_key=_date_key(row["close_date"]),
            status=row["status"],
            technician=row["technician"],
            labor_amount=row["labor_amount"],
            parts_amount=row["parts_amount"],
            tax_amount=row["tax_amount"],
            total_amount=row["total_amount"],
            days_to_close=row["days_to_close"],
        )
    return len(rows)


def load_payments(conn: NativeConnection, rows: list[dict[str, Any]]) -> int:
    """Upsert fact_payment rows. customer_key is resolved by joining through
    fact_repair_order rather than trusting the payment record to carry the shop's
    internal customer id -- real payment-processor exports (Square/Stripe/etc.)
    typically only reference the invoice/RO number, not the shop's own customer id."""
    sql = """
        INSERT INTO fact_payment (
            source_payment_id, repair_order_key, customer_key, payment_date_key,
            payment_amount, payment_method
        )
        SELECT
            :source_payment_id, fro.repair_order_key, fro.customer_key,
            :payment_date_key, :payment_amount, :payment_method
        FROM fact_repair_order fro
        WHERE fro.source_ro_number = :source_ro_number
        ON CONFLICT (source_payment_id) DO UPDATE SET
            repair_order_key = EXCLUDED.repair_order_key,
            customer_key      = EXCLUDED.customer_key,
            payment_date_key = EXCLUDED.payment_date_key,
            payment_amount   = EXCLUDED.payment_amount,
            payment_method   = EXCLUDED.payment_method,
            load_timestamp   = now()
    """
    for row in rows:
        conn.run(
            sql,
            source_payment_id=row["source_payment_id"],
            source_ro_number=row["source_ro_number"],
            payment_date_key=_date_key(row["payment_date"]),
            payment_amount=row["payment_amount"],
            payment_method=row["payment_method"],
        )
    return len(rows)
