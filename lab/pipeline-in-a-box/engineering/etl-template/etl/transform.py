"""TRANSFORM -- clean, normalize, and reshape extracted records into rows ready to
load, using the field-mapping config in config/field_mapping.json.

Design intent for reuse across clients:
  * These functions never hardcode a client's raw column names. Every raw-field
    lookup goes through `apply_field_map`, driven by config/field_mapping.json. A new
    client with differently-named export columns is a NEW field_mapping.json, not a
    code change here. See ../README.md, "Onboarding a real client".
  * Functions are pure: (records, mapping) in -> (clean records, warnings) out. No
    file I/O, no DB, no globals. This is what keeps them portable into a Lambda
    transform step and directly unit-testable.
  * `TransformResult` carries both the clean rows AND any data-quality warnings
    (skipped rows, amount mismatches) instead of silently dropping problems -- a
    real client's first export WILL have messier data than this synthetic sample;
    the pipeline should surface that, not hide it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any


@dataclass
class TransformResult:
    rows: list[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)


def apply_field_map(row: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    """Rename a raw row's keys from source names to this pipeline's canonical names.

    `mapping` is {canonical_name: source_name}. A canonical field missing from the
    mapping or absent in the row comes back as None rather than raising -- transform
    functions decide per-field whether a missing value is fatal (skip the row) or
    just left null.
    """
    return {canonical: row.get(source_name) for canonical, source_name in mapping.items()}


def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _parse_date(value: Any) -> date | None:
    value = _clean_str(value)
    if not value:
        return None
    # Extend this list if a client's export uses a different date format
    # (e.g. "%m/%d/%Y") -- keep the parsing centralized here, not per-transform-fn.
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_amount(value: Any) -> Decimal:
    value = _clean_str(value)
    if not value:
        return Decimal("0.00")
    # Strip common currency formatting a client's export might include ("$1,234.50").
    value = value.replace("$", "").replace(",", "")
    try:
        return Decimal(value).quantize(Decimal("0.01"))
    except InvalidOperation:
        return Decimal("0.00")


def transform_customers(
    raw_customers: list[dict[str, Any]], mapping: dict[str, str]
) -> TransformResult:
    """-> rows shaped for dim_customer (minus surrogate key / load_timestamp)."""
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []

    for raw in raw_customers:
        mapped = apply_field_map(raw, mapping)
        source_id = _clean_str(mapped.get("source_customer_id"))
        if not source_id:
            warnings.append(f"customers: skipped row with no source_customer_id: {raw!r}")
            continue

        first_name = _clean_str(mapped.get("first_name")) or ""
        last_name = _clean_str(mapped.get("last_name")) or ""
        email = _clean_str(mapped.get("email"))

        rows.append(
            {
                "source_customer_id": source_id,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}".strip(),
                "email": email.lower() if email else None,
                "phone": _clean_str(mapped.get("phone")),
                "address_line1": _clean_str(mapped.get("address_line1")),
                "city": _clean_str(mapped.get("city")),
                "state": _clean_str(mapped.get("state")),
                "postal_code": _clean_str(mapped.get("postal_code")),
                "customer_since_date": _parse_date(mapped.get("customer_since_date")),
            }
        )

    return TransformResult(rows=rows, warnings=warnings)


def transform_vehicles(
    raw_repair_orders: list[dict[str, Any]], mapping: dict[str, str]
) -> TransformResult:
    """-> distinct rows shaped for dim_vehicle, derived from the repair-order export.

    Most small-shop exports don't have a separate vehicle master file -- vehicle
    attributes ride along on every repair-order row instead. Dedup by
    source_vehicle_id (VIN, or the source system's vehicle id) here so dim_vehicle
    gets exactly one row per vehicle even though the source has one row per visit.
    """
    seen: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []

    for raw in raw_repair_orders:
        mapped = apply_field_map(raw, mapping)
        vehicle_id = _clean_str(mapped.get("source_vehicle_id"))
        customer_id = _clean_str(mapped.get("source_customer_id"))
        if not vehicle_id or not customer_id:
            warnings.append(f"vehicles: skipped row missing vehicle/customer id: {raw!r}")
            continue

        if vehicle_id not in seen:
            year_raw = _clean_str(mapped.get("vehicle_year"))
            seen[vehicle_id] = {
                "source_vehicle_id": vehicle_id,
                "source_customer_id": customer_id,
                "vehicle_year": int(year_raw) if year_raw and year_raw.isdigit() else None,
                "vehicle_make": _clean_str(mapped.get("vehicle_make")),
                "vehicle_model": _clean_str(mapped.get("vehicle_model")),
            }

    return TransformResult(rows=list(seen.values()), warnings=warnings)


def transform_repair_orders(
    raw_repair_orders: list[dict[str, Any]], mapping: dict[str, str]
) -> TransformResult:
    """-> rows shaped for fact_repair_order (minus surrogate keys, which load.py
    resolves via the natural keys on dim_customer / dim_vehicle / dim_date)."""
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []

    for raw in raw_repair_orders:
        mapped = apply_field_map(raw, mapping)
        ro_number = _clean_str(mapped.get("source_ro_number"))
        customer_id = _clean_str(mapped.get("source_customer_id"))
        vehicle_id = _clean_str(mapped.get("source_vehicle_id"))
        open_date = _parse_date(mapped.get("open_date"))

        if not ro_number or not customer_id or not vehicle_id or not open_date:
            warnings.append(f"repair_orders: skipped incomplete row: {raw!r}")
            continue

        close_date = _parse_date(mapped.get("close_date"))
        status = (_clean_str(mapped.get("status")) or "open").lower()

        labor = _parse_amount(mapped.get("labor_amount"))
        parts = _parse_amount(mapped.get("parts_amount"))
        tax = _parse_amount(mapped.get("tax_amount"))
        total = _parse_amount(mapped.get("total_amount"))

        expected_total = (labor + parts + tax).quantize(Decimal("0.01"))
        if expected_total != total:
            warnings.append(
                f"repair_orders: {ro_number} total_amount ({total}) does not equal "
                f"labor+parts+tax ({expected_total}) -- loaded as-is, source total wins"
            )

        days_to_close = (close_date - open_date).days if close_date else None

        rows.append(
            {
                "source_ro_number": ro_number,
                "source_customer_id": customer_id,
                "source_vehicle_id": vehicle_id,
                "open_date": open_date,
                "close_date": close_date,
                "status": status,
                "technician": _clean_str(mapped.get("technician")),
                "labor_amount": labor,
                "parts_amount": parts,
                "tax_amount": tax,
                "total_amount": total,
                "days_to_close": days_to_close,
            }
        )

    return TransformResult(rows=rows, warnings=warnings)


def transform_payments(
    raw_payments: list[dict[str, Any]], mapping: dict[str, str]
) -> TransformResult:
    """-> rows shaped for fact_payment."""
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []

    for raw in raw_payments:
        mapped = apply_field_map(raw, mapping)
        payment_id = _clean_str(mapped.get("source_payment_id"))
        ro_number = _clean_str(mapped.get("source_ro_number"))
        payment_date = _parse_date(mapped.get("payment_date"))

        if not payment_id or not ro_number or not payment_date:
            warnings.append(f"payments: skipped incomplete row: {raw!r}")
            continue

        amount = _parse_amount(mapped.get("payment_amount"))
        if amount <= 0:
            warnings.append(f"payments: {payment_id} has non-positive amount ({amount})")

        method = _clean_str(mapped.get("payment_method"))

        rows.append(
            {
                "source_payment_id": payment_id,
                "source_ro_number": ro_number,
                "payment_date": payment_date,
                "payment_amount": amount,
                "payment_method": method.lower() if method else None,
            }
        )

    return TransformResult(rows=rows, warnings=warnings)
