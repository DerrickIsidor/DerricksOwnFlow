import csv
import io
import json
import os
import re

import boto3
import pg8000.dbapi

s3_client = boto3.client("s3")
secrets_client = boto3.client("secretsmanager")

# Defense in depth: TARGET_SCHEMA/TARGET_TABLE come from this Lambda's own
# environment (operator-set ClientPipelineConfig, not raw client file
# content) -- but they still get validated before being interpolated into SQL
# rather than trusted outright. See ClientPipelineConfig in
# infra/constructs/client_config.py, which validates the same pattern at
# synth time; this is a second, independent check at runtime.
_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _safe_identifier(name: str) -> str:
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(f"Unsafe SQL identifier: {name!r}")
    return name


def _get_db_connection():
    """Same secret-ARN-via-env-var pattern as example_handler -- see
    ../../.claude/skills/cdk-data-ai-stack/references/lambda-patterns.md.
    Unlike example_handler, this actually opens the Postgres connection
    (pg8000, pure Python, no Docker bundling needed -- see requirements.txt).
    """
    secret_arn = os.environ["DB_SECRET_ARN"]
    secret = secrets_client.get_secret_value(SecretId=secret_arn)
    creds = json.loads(secret["SecretString"])
    return pg8000.dbapi.connect(
        host=creds["host"],
        port=int(creds.get("port", 5432)),
        database=os.environ["DB_NAME"],
        user=creds["username"],
        password=creds["password"],
        # NOTE: no SSL enforced yet -- Aurora accepts unencrypted connections
        # by default over the private VPC link, but enforcing TLS is a good
        # next step before a real client's data flows through this. Left as
        # an open item, see setup-checklist.md / decisions.md, rather than
        # guessing at pg8000's ssl_context parameter shape without a real
        # deploy to test it against.
    )


def extract(bucket: str, key: str) -> str:
    """Extract: pull the raw object body out of the landing bucket as text.

    Real files could be large enough to warrant streaming instead of reading
    fully into memory -- fine for the file sizes a small-business client's
    exports are expected to be, revisit if that assumption breaks.
    """
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8")


def transform(raw_text: str, source_key: str) -> list[dict]:
    """TODO(real client onboarding): replace this generic stub with the real
    per-client transform logic once a real client's data shape is known.

    See lab/pipeline-in-a-box/engineering/etl-template/ for the
    extract/transform/load reference implementation being designed in
    parallel against synthetic sample data -- port the real transform logic
    from there into this function once there's an actual client. (Lambda
    packaging in this repo is self-contained per lambda_src/<name>/, so that
    module doesn't get imported directly here -- copy the logic in, or
    promote shared pieces into this Lambda's own requirements.txt / a Lambda
    layer if it grows, see lambda-patterns.md "Open".)

    Placeholder behavior: sniffs CSV vs JSON by file extension and returns a
    list of plain dicts, one per row/record, with no business-specific field
    mapping or type coercion. Good enough to prove extract -> transform ->
    load wiring end to end; not good enough for a real client's schema.
    """
    if source_key.lower().endswith(".json"):
        data = json.loads(raw_text)
        return data if isinstance(data, list) else [data]

    reader = csv.DictReader(io.StringIO(raw_text))
    return list(reader)


def load(
    rows: list[dict],
    connection,
    *,
    client_id: str,
    schema: str,
    table: str,
    source_key: str,
) -> int:
    """Load rows into a generic, schema-agnostic per-client landing table:
    (id, client_id, source_key, ingested_at, payload JSONB).

    Deliberately does NOT build a dynamic INSERT column list from client file
    headers -- that would mean interpolating untrusted content into SQL. Real
    typed columns per client come later: either from transform() once it's
    filled in with real per-client logic, or downstream (dbt/SQL) unpacking
    `payload`.

    Creates the table if missing (idempotent) as a stand-in for real
    migration tooling, which hasn't been chosen yet -- see sql-patterns.md.
    Fine for a scaffold; revisit once alembic (or whatever's chosen) owns
    schema for real.
    """
    schema = _safe_identifier(schema)
    table = _safe_identifier(table)

    cursor = connection.cursor()
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            id BIGSERIAL PRIMARY KEY,
            client_id TEXT NOT NULL,
            source_key TEXT NOT NULL,
            ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            payload JSONB NOT NULL
        )
        """
    )
    for row in rows:
        cursor.execute(
            f"INSERT INTO {schema}.{table} (client_id, source_key, payload) "
            "VALUES (%s, %s, %s)",
            (client_id, source_key, json.dumps(row)),
        )
    connection.commit()
    cursor.close()
    return len(rows)


def handler(event, context):
    """Transform Lambda: triggered by S3 ObjectCreated events on a client's
    landing bucket (see TransformLambdaConstruct / ClientPipelineConstruct in
    infra/constructs/). Follows an extract -> transform -> load shape:

      1. extract() -- read the new object out of S3.
      2. transform() -- STUB, see its docstring; real per-client logic lands
         here once a real client's data shape is known.
      3. load()    -- write normalized rows into Aurora Postgres via pg8000,
         using the DB secret ARN injected as an env var (never raw
         credentials -- see lambda-patterns.md).

    CLIENT_ID / TARGET_SCHEMA / TARGET_TABLE come from ClientPipelineConfig
    via the Lambda's environment (set in TransformLambdaConstruct), so this
    same handler code runs unmodified for every client -- only the config
    differs.
    """
    client_id = os.environ["CLIENT_ID"]
    schema = os.environ.get("TARGET_SCHEMA", "public")
    table = os.environ["TARGET_TABLE"]

    connection = _get_db_connection()
    processed = []
    try:
        for record in event.get("Records", []):
            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]

            raw_text = extract(bucket, key)
            rows = transform(raw_text, key)
            rows_loaded = load(
                rows,
                connection,
                client_id=client_id,
                schema=schema,
                table=table,
                source_key=key,
            )
            processed.append({"source_key": key, "rows_loaded": rows_loaded})
    finally:
        connection.close()

    return {
        "statusCode": 200,
        "body": json.dumps({"client_id": client_id, "files_processed": processed}),
    }
