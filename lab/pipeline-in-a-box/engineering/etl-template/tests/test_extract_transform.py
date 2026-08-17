"""Unit tests for extract.py / transform.py against the synthetic sample data.

Deliberately does NOT require a live Postgres -- extract/transform are pure
functions, this is exactly the kind of test that's supposed to be cheap to run.
load.py's SQL is separately verified against a real Postgres grammar in
test_load_sql_parses.py (parse-only, since no live Postgres is available in this
sandbox -- see ../README.md "What's still open" for the real-DB verification gap).

Run with: python -m pytest tests/ -v   (from this project's root)
"""
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CONFIG_PATH = PROJECT_ROOT / "config" / "field_mapping.json"

import sys

sys.path.insert(0, str(PROJECT_ROOT))

from etl import extract, transform  # noqa: E402


@pytest.fixture(scope="module")
def field_mapping():
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    raw.pop("_comment", None)
    return raw


@pytest.fixture(scope="module")
def raw_data():
    return extract.read_raw_files(RAW_DIR)


def test_extract_customers_parses_all_rows(raw_data):
    assert len(raw_data["customers"]) == 15
    assert raw_data["customers"][0]["customer_id"] == "CUST-0001"


def test_extract_repair_orders_parses_all_rows(raw_data):
    assert len(raw_data["repair_orders"]) == 30


def test_extract_payments_parses_array(raw_data):
    assert len(raw_data["payments"]) == 27
    assert raw_data["payments"][0]["ro_number"] == "RO-00001"


def test_transform_customers_shapes_and_cleans(raw_data, field_mapping):
    result = transform.transform_customers(raw_data["customers"], field_mapping["customers"])
    assert not result.warnings
    assert len(result.rows) == 15
    row = next(r for r in result.rows if r["source_customer_id"] == "CUST-0001")
    assert row["full_name"] == "James Turner"
    assert row["email"] == "james.turner@example.com"  # lowercased
    assert row["customer_since_date"] is not None  # date parsed, not left as string


def test_transform_vehicles_dedupes_by_vin(raw_data, field_mapping):
    result = transform.transform_vehicles(
        raw_data["repair_orders"], field_mapping["repair_orders"]
    )
    assert not result.warnings
    # every repair order in the synthetic data has a unique VIN, so vehicle count
    # should equal repair-order count here -- this assertion would catch a dedup
    # bug (over- or under-collapsing) if the sample data changes to reuse a VIN.
    vin_set = {ro["vehicle_vin"] for ro in raw_data["repair_orders"]}
    assert len(result.rows) == len(vin_set)


def test_transform_repair_orders_computes_days_to_close(raw_data, field_mapping):
    result = transform.transform_repair_orders(
        raw_data["repair_orders"], field_mapping["repair_orders"]
    )
    assert not result.warnings, result.warnings
    closed = [r for r in result.rows if r["status"] == "closed"]
    opened = [r for r in result.rows if r["status"] == "open"]
    assert closed and opened  # synthetic data has both -- sanity check the fixture itself
    for row in closed:
        assert row["days_to_close"] is not None
        assert row["days_to_close"] >= 0
    for row in opened:
        assert row["close_date"] is None
        assert row["days_to_close"] is None


def test_transform_repair_orders_total_matches_components(raw_data, field_mapping):
    # The generator computed total_amount = labor + parts + tax exactly, so a clean
    # run should produce zero "total doesn't match components" warnings. If this
    # ever fails, either the sample data generator or the amount-reconciliation
    # check in transform.py has drifted.
    result = transform.transform_repair_orders(
        raw_data["repair_orders"], field_mapping["repair_orders"]
    )
    mismatch_warnings = [w for w in result.warnings if "does not equal" in w]
    assert mismatch_warnings == []


def test_transform_payments_shapes_amounts(raw_data, field_mapping):
    result = transform.transform_payments(raw_data["payments"], field_mapping["payments"])
    assert not result.warnings
    assert len(result.rows) == 27
    for row in result.rows:
        assert row["payment_amount"] > 0
        assert row["payment_method"] in {"card", "cash", "check", "financing"}


def test_open_repair_orders_have_no_payments(raw_data, field_mapping):
    """Cash-flow-proxy sanity check: every payment's ro_number must reference a
    CLOSED repair order in the sample data (an open job hasn't been invoiced yet,
    so it shouldn't have a payment against it) -- catches a broken fixture, and
    documents the invariant the star schema is designed to represent."""
    ro_status = {
        ro["ro_number"]: ro["status"] for ro in raw_data["repair_orders"]
    }
    for payment in raw_data["payments"]:
        assert ro_status[payment["ro_number"]] == "closed"
