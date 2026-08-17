-- Pipeline-in-a-Box -- target Aurora Postgres schema (BI-consumption star schema)
--
-- Vertical demonstrated: small auto-repair shop. This schema is the REUSABLE part of
-- the template -- it does not change per client. What changes per client is described
-- in ../README.md ("Onboarding a real client").
--
-- Grain decisions (make these explicit before anyone writes a query against this):
--   fact_repair_order : one row per repair order / job / ticket (the shop's invoice
--                        line for a single vehicle visit). This is the "jobs" fact --
--                        drives job volume and invoiced revenue.
--   fact_payment       : one row per payment transaction. A repair order can have zero
--                        (not yet paid), one, or many payments (deposits/partials). This
--                        is the cash-flow-proxy fact -- drives "cash actually collected"
--                        as distinct from "revenue invoiced", and days-to-pay.
--   dim_customer       : one row per customer (SCD Type 1 -- latest values win on
--                        reload; see README for the SCD2 upgrade note).
--   dim_vehicle        : one row per vehicle, owned by exactly one customer.
--   dim_date           : one row per calendar day, pre-populated for a wide range.
--   Star schema, not 3NF: dimensions are intentionally denormalized/wide, facts are
--   narrow (FKs + measures). This trades storage for join-simplicity, which is what a
--   BI tool wants -- see the sql-data-engineering skill's "Star schema" section.
--
-- Idempotent load target: every table has a UNIQUE natural/business key from the
-- source system (source_customer_id, source_vehicle_id, source_ro_number,
-- source_payment_id) so load.py can upsert (INSERT ... ON CONFLICT DO UPDATE) safely
-- on reprocessing -- see the ETL note on delivery guarantees in etl/load.py.

-- =====================================================================================
-- DIMENSION: dim_date
-- =====================================================================================
-- Standard BI date dimension. Populate once via the generate_series block at the
-- bottom of this file (or an equivalent) -- every date-intelligence measure in the
-- eventual Power BI model (YoY, MTD, rolling windows) depends on this table existing
-- and being marked as the model's Date Table.

CREATE TABLE IF NOT EXISTS dim_date (
    date_key       INTEGER      PRIMARY KEY,           -- YYYYMMDD, e.g. 20260615
    full_date      DATE         NOT NULL UNIQUE,
    day_of_month   SMALLINT     NOT NULL,
    day_name       TEXT         NOT NULL,
    day_of_week    SMALLINT     NOT NULL,               -- 1=Monday .. 7=Sunday (ISO)
    is_weekend     BOOLEAN      NOT NULL,
    week_of_year   SMALLINT     NOT NULL,
    month_number   SMALLINT     NOT NULL,
    month_name     TEXT         NOT NULL,
    quarter_number SMALLINT     NOT NULL,
    year_number    SMALLINT     NOT NULL,
    year_month     TEXT         NOT NULL                -- '2026-06', convenient sort/group key
);

-- =====================================================================================
-- DIMENSION: dim_customer
-- =====================================================================================

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key        SERIAL       PRIMARY KEY,                        -- surrogate key
    source_customer_id  TEXT         NOT NULL UNIQUE,                    -- natural key from client export
    first_name           TEXT         NOT NULL,
    last_name             TEXT         NOT NULL,
    full_name             TEXT         NOT NULL,
    email                 TEXT,
    phone                 TEXT,
    address_line1        TEXT,
    city                  TEXT,
    state                 TEXT,
    postal_code           TEXT,
    customer_since_date  DATE,                                           -- first appeared in source (their CRM's created date)
    source_system        TEXT         NOT NULL DEFAULT 'shop_management_export',
    load_timestamp       TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- =====================================================================================
-- DIMENSION: dim_vehicle
-- =====================================================================================

CREATE TABLE IF NOT EXISTS dim_vehicle (
    vehicle_key        SERIAL       PRIMARY KEY,
    source_vehicle_id  TEXT         NOT NULL UNIQUE,                     -- VIN, or source system's vehicle id
    customer_key       INTEGER      NOT NULL REFERENCES dim_customer (customer_key),
    vehicle_year       SMALLINT,
    vehicle_make       TEXT,
    vehicle_model      TEXT,
    load_timestamp     TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_dim_vehicle_customer_key ON dim_vehicle (customer_key);

-- =====================================================================================
-- FACT: fact_repair_order  (grain: one row per repair order / job / ticket)
-- =====================================================================================

CREATE TABLE IF NOT EXISTS fact_repair_order (
    repair_order_key  SERIAL         PRIMARY KEY,                        -- surrogate key
    source_ro_number  TEXT           NOT NULL UNIQUE,                    -- natural key: the RO# on the client's invoice
    customer_key      INTEGER        NOT NULL REFERENCES dim_customer (customer_key),
    vehicle_key       INTEGER        NOT NULL REFERENCES dim_vehicle (vehicle_key),
    open_date_key     INTEGER        NOT NULL REFERENCES dim_date (date_key),
    close_date_key    INTEGER        REFERENCES dim_date (date_key),     -- NULL while still open
    status            TEXT           NOT NULL,                           -- 'open' | 'closed' | 'cancelled'
    technician        TEXT,
    labor_amount      NUMERIC(10, 2) NOT NULL DEFAULT 0,
    parts_amount      NUMERIC(10, 2) NOT NULL DEFAULT 0,
    tax_amount        NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_amount      NUMERIC(10, 2) NOT NULL DEFAULT 0,                 -- invoiced revenue for this job
    days_to_close     INTEGER,                                           -- close_date - open_date, NULL while open
    load_timestamp    TIMESTAMPTZ    NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_fro_customer_key   ON fact_repair_order (customer_key);
CREATE INDEX IF NOT EXISTS ix_fro_vehicle_key    ON fact_repair_order (vehicle_key);
CREATE INDEX IF NOT EXISTS ix_fro_open_date_key  ON fact_repair_order (open_date_key);
CREATE INDEX IF NOT EXISTS ix_fro_close_date_key ON fact_repair_order (close_date_key);
CREATE INDEX IF NOT EXISTS ix_fro_status         ON fact_repair_order (status);

-- =====================================================================================
-- FACT: fact_payment  (grain: one row per payment transaction -- the cash-flow proxy)
-- =====================================================================================
-- customer_key is intentionally denormalized onto this fact (in addition to the
-- repair_order_key FK) -- a common, deliberate star-schema convenience so Power BI
-- can filter/slice payments by customer without forcing a join through
-- fact_repair_order for every visual.

CREATE TABLE IF NOT EXISTS fact_payment (
    payment_key        SERIAL         PRIMARY KEY,
    source_payment_id  TEXT           NOT NULL UNIQUE,                   -- natural key from payment processor / source export
    repair_order_key   INTEGER        NOT NULL REFERENCES fact_repair_order (repair_order_key),
    customer_key        INTEGER        NOT NULL REFERENCES dim_customer (customer_key),
    payment_date_key   INTEGER        NOT NULL REFERENCES dim_date (date_key),
    payment_amount     NUMERIC(10, 2) NOT NULL,
    payment_method     TEXT,                                             -- 'card' | 'cash' | 'check' | 'financing'
    load_timestamp     TIMESTAMPTZ    NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_fp_repair_order_key ON fact_payment (repair_order_key);
CREATE INDEX IF NOT EXISTS ix_fp_customer_key      ON fact_payment (customer_key);
CREATE INDEX IF NOT EXISTS ix_fp_payment_date_key  ON fact_payment (payment_date_key);

-- =====================================================================================
-- dim_date population
-- =====================================================================================
-- Run once (or re-run -- it's idempotent via the unique full_date + ON CONFLICT) to
-- populate a wide-enough range to cover any client's history plus runway. Widen the
-- range per client if their historical export goes back further than 2023.

INSERT INTO dim_date (
    date_key, full_date, day_of_month, day_name, day_of_week, is_weekend,
    week_of_year, month_number, month_name, quarter_number, year_number, year_month
)
SELECT
    (to_char(d, 'YYYYMMDD'))::INTEGER,
    d,
    EXTRACT(DAY FROM d)::SMALLINT,
    to_char(d, 'Day'),
    EXTRACT(ISODOW FROM d)::SMALLINT,
    EXTRACT(ISODOW FROM d) IN (6, 7),
    EXTRACT(WEEK FROM d)::SMALLINT,
    EXTRACT(MONTH FROM d)::SMALLINT,
    to_char(d, 'Month'),
    EXTRACT(QUARTER FROM d)::SMALLINT,
    EXTRACT(YEAR FROM d)::SMALLINT,
    to_char(d, 'YYYY-MM')
FROM generate_series('2023-01-01'::DATE, '2028-12-31'::DATE, INTERVAL '1 day') AS d
ON CONFLICT (full_date) DO NOTHING;
