"""Static verification of load.py's SQL against a real Postgres grammar and
against the actual DDL in sql/schema.sql -- WITHOUT a live database.

No live Postgres was available to run these queries end-to-end against (see
../README.md, "What's still open" -- this is the honest gap). This test is the
next-best verification: it parses every INSERT in load.py with `pglast` (a real
libpg_query-based Postgres parser, not a guess) to confirm they are syntactically
valid Postgres, and cross-checks every INSERT's target column list against the
actual columns `sql/schema.sql` creates -- so a typo'd or renamed column would fail
this test even though it can't fail against a real database here.

pg8000's `:name` client-side placeholder syntax isn't valid raw Postgres SQL (the
wire protocol only understands positional `$1, $2, ...`) -- pg8000 rewrites it
internally before sending to the server. So placeholders are substituted with NULL
literals before parsing; this validates SQL *structure* (clauses, column names,
join shape), not placeholder wiring, which is exercised by pg8000's own test suite,
not this project's.

Run with: python -m pytest tests/ -v   (from this project's root)
"""
import re
from pathlib import Path

import pglast
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOAD_PY = PROJECT_ROOT / "etl" / "load.py"
SCHEMA_SQL = PROJECT_ROOT / "sql" / "schema.sql"


def _schema_columns() -> dict[str, set[str]]:
    """table_name -> set(column_name) as actually declared in sql/schema.sql."""
    sql = SCHEMA_SQL.read_text(encoding="utf-8")
    stmts = pglast.parse_sql(sql)
    tables: dict[str, set[str]] = {}
    for stmt in stmts:
        node = stmt.stmt
        if type(node).__name__ == "CreateStmt":
            cols = {c.colname for c in node.tableElts if type(c).__name__ == "ColumnDef"}
            tables[node.relation.relname] = cols
    return tables


def _load_py_insert_statements() -> list[tuple[str, str]]:
    """Return (sql_text, sql_text_with_placeholders_as_NULL) for every triple-quoted
    `sql = ...` block in load.py (one per load_* function)."""
    src = LOAD_PY.read_text(encoding="utf-8")
    raw_blocks = re.findall(r'sql = """(.*?)"""', src, re.S)
    return [(block, re.sub(r":([a-zA-Z_][a-zA-Z0-9_]*)", "NULL", block)) for block in raw_blocks]


def test_schema_sql_itself_parses():
    """sql/schema.sql as a whole is valid Postgres DDL."""
    sql = SCHEMA_SQL.read_text(encoding="utf-8")
    stmts = pglast.parse_sql(sql)
    assert len(stmts) > 0


def test_schema_has_expected_tables():
    tables = _schema_columns()
    assert set(tables) == {
        "dim_date",
        "dim_customer",
        "dim_vehicle",
        "fact_repair_order",
        "fact_payment",
    }


def test_load_py_has_four_insert_blocks():
    blocks = _load_py_insert_statements()
    assert len(blocks) == 4


def test_every_load_py_insert_parses_as_valid_postgres():
    for original, parseable in _load_py_insert_statements():
        try:
            pglast.parse_sql(parseable)
        except Exception as e:  # pragma: no cover - failure path
            pytest.fail(f"Invalid SQL in load.py:\n{original}\n\nError: {e}")


def test_every_load_py_insert_column_matches_schema():
    tables = _schema_columns()
    for original, parseable in _load_py_insert_statements():
        stmt = pglast.parse_sql(parseable)[0].stmt
        assert type(stmt).__name__ == "InsertStmt"
        table_name = stmt.relation.relname
        assert table_name in tables, f"load.py inserts into unknown table {table_name!r}"
        insert_cols = {c.name for c in stmt.cols}
        unknown = insert_cols - tables[table_name]
        assert not unknown, (
            f"load.py's INSERT into {table_name} references column(s) {unknown} "
            f"that don't exist in sql/schema.sql"
        )
