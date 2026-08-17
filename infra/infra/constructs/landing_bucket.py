from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_s3 as s3
from constructs import Construct

from .client_config import ClientPipelineConfig


class LandingBucketConstruct(Construct):
    """Per-client S3 landing bucket: where a client's raw extracted files
    (CSV/JSON exports) arrive before the transform Lambda picks them up. One
    instance per client -- see `ClientPipelineConstruct`, which is the
    parameterized unit real client onboarding actually instantiates; this
    construct is rarely used standalone.

    Defaults are deliberately conservative for a productized service handling
    client data: versioned, private (all public access blocked), encrypted,
    SSL-only, and RETAINed on stack delete/update -- raw client data should
    never disappear just because a CDK stack got torn down or updated. See
    ../../.claude/skills/cdk-data-ai-stack/references/decisions.md
    ("Multi-tenant parameterization").
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        config: ClientPipelineConfig,
        removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
    ) -> None:
        super().__init__(scope, construct_id)

        self.config = config

        bucket_name = None
        if config.bucket_name_prefix:
            # Caller's responsibility that this is globally unique across ALL
            # of S3, not just this account -- S3 bucket names are a single
            # global namespace. Left unset (None) by default so CDK
            # auto-generates a unique physical name instead.
            bucket_name = f"{config.bucket_name_prefix}-{config.client_id}-landing".lower()

        self.bucket = s3.Bucket(
            self,
            "Bucket",
            bucket_name=bucket_name,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=removal_policy,
            lifecycle_rules=[
                # Cheap hygiene default, not a full lifecycle policy -- no
                # expiration/transition rules yet since raw client data
                # retention needs are unknown until a real client exists.
                s3.LifecycleRule(
                    abort_incomplete_multipart_upload_after=Duration.days(7),
                ),
            ],
        )
