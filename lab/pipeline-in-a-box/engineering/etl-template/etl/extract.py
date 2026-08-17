"""EXTRACT -- turn raw source bytes/text into plain Python records.

Every function here takes the *content* of a file (a str), not a file path or an S3
key. That's deliberate: it's the seam where this template gets ported into the
Lambda transform step (cdk-engineer's side of this build). Locally, `read_raw_files`
below reads from disk. In the Lambda, the equivalent caller will instead do
`s3.get_object(Bucket=..., Key=...)["Body"].read().decode("utf-8")` and pass that
string into the same `extract_*` function -- nothing in these functions needs to
change to make that swap.

No transformation or validation happens here beyond structural parsing (CSV -> list
of dicts, JSON -> list of dicts). Business rules (type coercion, trimming, dedup,
computed fields) belong in transform.py, not here -- keeps each stage testable in
isolation and keeps this stage a thin, reliable parser.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any


def extract_customers(csv_text: str) -> list[dict[str, Any]]:
    """Parse a customer-list CSV export into a list of raw row dicts."""
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def extract_repair_orders(csv_text: str) -> list[dict[str, Any]]:
    """Parse a repair-order / job / invoice CSV export into a list of raw row dicts."""
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def extract_payments(json_text: str) -> list[dict[str, Any]]:
    """Parse a payments JSON export (array of payment objects) into a list of dicts.

    Real payment-processor exports (Square, Stripe, etc.) vary in shape -- some are a
    bare array like the synthetic sample here, some wrap it in {"payments": [...]}.
    Handle both without changing the function's contract to callers.
    """
    payload = json.loads(json_text)
    if isinstance(payload, dict):
        payload = payload.get("payments", payload.get("data", []))
    if not isinstance(payload, list):
        raise ValueError("Expected payments export to parse to a list of payment records")
    return payload


def read_raw_files(raw_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """Local/dev convenience: read the three raw files from disk and extract them.

    This function is the ONLY thing that changes shape when this pattern moves into
    the Lambda -- there, "reading the raw file" means an S3 GetObject call per
    EventBridge/S3-notification event instead of a local directory read. The three
    `extract_*` functions above stay identical either way.
    """
    customers_csv = (raw_dir / "customers.csv").read_text(encoding="utf-8")
    repair_orders_csv = (raw_dir / "repair_orders.csv").read_text(encoding="utf-8")
    payments_json = (raw_dir / "payments.json").read_text(encoding="utf-8")

    return {
        "customers": extract_customers(customers_csv),
        "repair_orders": extract_repair_orders(repair_orders_csv),
        "payments": extract_payments(payments_json),
    }
