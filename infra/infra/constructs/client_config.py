"""Not a construct -- a plain dataclass, kept in its own module so both
landing_bucket.py and transform_lambda.py can import it without a circular
import through client_pipeline.py (which imports both of those). See
../../.claude/skills/cdk-data-ai-stack/references/conventions.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
_CLIENT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,48}$")


@dataclass
class ClientPipelineConfig:
    """Per-client parameters for a Pipeline-in-a-Box onboarding.

    This is the whole parameterization surface: instantiate one of these per
    client and pass it to `ClientPipelineConstruct` -- see
    ../../.claude/skills/cdk-data-ai-stack/references/decisions.md
    ("Multi-tenant parameterization") for why this shape (a config object fed
    to one reusable construct) was chosen over a stack-per-client or a
    copy-pasted stack subclass.

    Fields:
        client_id: short slug identifying the client. Used to derive the S3
            key prefix, the Postgres table name, and (optionally) part of the
            bucket name -- so it's constrained to what's safe in all three:
            lowercase letters/digits/hyphens, starting with a letter or
            digit, <=49 chars. Raises ValueError at construction time
            (synth time, not deploy time) if it doesn't match.
        bucket_name_prefix: optional explicit prefix for the landing bucket's
            S3 name (e.g. a product/company prefix). S3 bucket names are
            globally unique across ALL of AWS, not just this account --
            picking a name that won't collide is the caller's
            responsibility. Leave unset (default) to let CDK auto-generate a
            unique physical name instead -- recommended unless a predictable
            bucket name is actually needed (e.g. for a client to reference).
        target_schema / target_table: where loaded rows land in Aurora
            Postgres. `target_table` defaults to "<client_id>_raw" with
            hyphens converted to underscores (Postgres identifiers can't
            contain hyphens unquoted).
        source_prefix: S3 key prefix a client's extract files must land under
            to trigger the transform Lambda. Defaults to "<client_id>/" so
            each client gets a folder-like namespace even if a future change
            ever shares one bucket across clients (not done today -- current
            baseline is one bucket per client, see decisions.md).
        file_suffixes: file extensions that trigger the transform Lambda.
            Each suffix becomes its own S3 event notification rule -- S3
            notification filters AND a prefix+suffix together within one
            rule, they don't OR across multiple suffixes, so multiple
            suffixes need multiple rules (handled in TransformLambdaConstruct).
    """

    client_id: str
    bucket_name_prefix: str | None = None
    target_schema: str = "public"
    target_table: str | None = None
    source_prefix: str | None = None
    file_suffixes: tuple[str, ...] = (".csv", ".json")

    def __post_init__(self) -> None:
        if not _CLIENT_ID_RE.match(self.client_id):
            raise ValueError(
                f"client_id {self.client_id!r} must be lowercase "
                "alphanumeric/hyphens, start with a letter or digit, "
                "<=49 chars (it's reused as an S3 prefix and part of a SQL "
                "identifier)."
            )
        if self.target_table is None:
            self.target_table = f"{self.client_id.replace('-', '_')}_raw"
        if not _IDENTIFIER_RE.match(self.target_schema):
            raise ValueError(
                f"target_schema {self.target_schema!r} is not a valid SQL "
                "identifier."
            )
        if not _IDENTIFIER_RE.match(self.target_table):
            raise ValueError(
                f"target_table {self.target_table!r} is not a valid SQL "
                "identifier."
            )
        if self.source_prefix is None:
            self.source_prefix = f"{self.client_id}/"
