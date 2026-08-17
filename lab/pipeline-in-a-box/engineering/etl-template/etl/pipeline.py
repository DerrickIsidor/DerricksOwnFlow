"""Orchestration: wires extract -> transform -> load together in the shape that
should get ported into the Lambda transform step almost unchanged.

`run_pipeline()` is the function to port. It takes already-read file CONTENTS (str)
plus a field-mapping config dict and an open DB connection -- it does not know or
care whether those strings came from `Path.read_text()` (this local CLI) or an S3
`get_object()` body (the real Lambda). That's the whole point of keeping extract.py
pure: the Lambda handler becomes a thin adapter that fetches three S3 objects, loads
the client's field_mapping.json (e.g. from S3 or bundled per-client config), opens a
pg8000 connection via load.get_connection(), and calls this same function.

`main()` below is the local-only piece -- reads sample files from disk, reads DB
connection info from environment variables, and is NOT what gets ported. Keeping it
isolated at the bottom of this file (and behind `if __name__ == "__main__"`) is what
keeps the reusable part reusable.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from etl import extract, load, transform

logger = logging.getLogger("pipeline_in_a_box.etl")


@dataclass
class PipelineResult:
    counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def load_field_mapping(config_path: Path) -> dict[str, dict[str, str]]:
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    raw.pop("_comment", None)
    return raw


def run_pipeline(
    *,
    customers_raw: str,
    repair_orders_raw: str,
    payments_raw: str,
    field_mapping: dict[str, dict[str, str]],
    conn: load.NativeConnection,
) -> PipelineResult:
    """Run one full extract -> transform -> load cycle for one client file drop.

    Loads inside a single transaction: dims and facts for this file either all land
    or none do, so a mid-batch failure never leaves fact rows referencing
    dimension rows that weren't actually committed.
    """
    result = PipelineResult()

    # EXTRACT
    raw_customers = extract.extract_customers(customers_raw)
    raw_repair_orders = extract.extract_repair_orders(repair_orders_raw)
    raw_payments = extract.extract_payments(payments_raw)

    # TRANSFORM
    customers = transform.transform_customers(raw_customers, field_mapping["customers"])
    vehicles = transform.transform_vehicles(raw_repair_orders, field_mapping["repair_orders"])
    repair_orders = transform.transform_repair_orders(
        raw_repair_orders, field_mapping["repair_orders"]
    )
    payments = transform.transform_payments(raw_payments, field_mapping["payments"])

    for t in (customers, vehicles, repair_orders, payments):
        result.warnings.extend(t.warnings)
    for w in result.warnings:
        logger.warning(w)

    # LOAD -- one transaction, dims before facts
    conn.run("BEGIN")
    try:
        result.counts["dim_customer"] = load.load_customers(conn, customers.rows)
        result.counts["dim_vehicle"] = load.load_vehicles(conn, vehicles.rows)
        result.counts["fact_repair_order"] = load.load_repair_orders(conn, repair_orders.rows)
        result.counts["fact_payment"] = load.load_payments(conn, payments.rows)
        conn.run("COMMIT")
    except Exception:
        conn.run("ROLLBACK")
        logger.exception("Load failed -- transaction rolled back, nothing partially committed")
        raise

    return result


def _local_secret_from_env() -> dict[str, Any]:
    """Local/dev convenience only -- builds the same shape dict get_connection()
    expects from Secrets Manager, but from plain env vars. NOT how the Lambda gets
    its credentials (it reads the actual secret via boto3 -- see
    ../../../.claude/skills/cdk-data-ai-stack/references/lambda-patterns.md)."""
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": os.environ.get("DB_PORT", "5432"),
        "username": os.environ.get("DB_USER", "dbadmin"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "dbname": os.environ.get("DB_NAME", "app"),
    }


def main() -> None:
    """Local CLI entry point -- runs the pipeline once against the synthetic sample
    files in data/raw/ and a local/dev Postgres. Requires DB_HOST/DB_USER/etc. env
    vars pointed at a real reachable Postgres; this repo's Aurora instance is inside
    an isolated VPC subnet by design (see infra/README.md) so this is meant for a
    local Postgres or an SSH/port-forward tunnel, not a direct connection from a dev
    machine to the deployed Aurora cluster."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    project_root = Path(__file__).resolve().parent.parent
    raw_dir = project_root / "data" / "raw"
    config_path = project_root / "config" / "field_mapping.json"

    field_mapping = load_field_mapping(config_path)
    conn = load.get_connection(_local_secret_from_env())

    result = run_pipeline(
        customers_raw=(raw_dir / "customers.csv").read_text(encoding="utf-8"),
        repair_orders_raw=(raw_dir / "repair_orders.csv").read_text(encoding="utf-8"),
        payments_raw=(raw_dir / "payments.json").read_text(encoding="utf-8"),
        field_mapping=field_mapping,
        conn=conn,
    )

    logger.info("Load complete: %s", result.counts)
    if result.warnings:
        logger.warning("%d data-quality warnings -- see log above", len(result.warnings))


if __name__ == "__main__":
    main()
