from aws_cdk import Duration
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_notifications as s3n
from constructs import Construct

from .client_config import ClientPipelineConfig


class TransformLambdaConstruct(Construct):
    """Per-client transform Lambda: triggered by S3 ObjectCreated events on
    that client's landing bucket, reads the new object, transforms it, and
    loads rows into Aurora Postgres. Follows the same VPC/secret wiring shape
    as `ExampleLambdaConstruct` -- see
    ../../.claude/skills/cdk-data-ai-stack/references/lambda-patterns.md --
    plus S3 read access and an event trigger on top.

    Trigger choice (S3 event, not a schedule): see
    references/decisions.md ("S3-event trigger, not scheduled batch") for why.

    Like `ExampleLambdaConstruct`, this construct does NOT call
    `database.connections.allow_default_port_from(function)` -- that stays on
    the stack side, where the two resources are wired together, per
    lambda-patterns.md.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.Vpc,
        db_secret,
        db_name: str,
        landing_bucket: s3.Bucket,
        config: ClientPipelineConfig,
    ) -> None:
        super().__init__(scope, construct_id)

        self.config = config

        self.function = _lambda.Function(
            self,
            "Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("lambda_src/transform_handler"),
            timeout=Duration.seconds(60),
            memory_size=512,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            environment={
                "DB_SECRET_ARN": db_secret.secret_arn,
                "DB_NAME": db_name,
                "CLIENT_ID": config.client_id,
                "TARGET_SCHEMA": config.target_schema,
                "TARGET_TABLE": config.target_table,
            },
        )
        db_secret.grant_read(self.function)
        landing_bucket.grant_read(self.function)

        # One notification rule per suffix -- S3 filters AND prefix+suffix
        # within a single rule, they don't OR across multiple suffixes. See
        # ClientPipelineConfig.file_suffixes docstring.
        for suffix in config.file_suffixes:
            landing_bucket.add_event_notification(
                s3.EventType.OBJECT_CREATED,
                s3n.LambdaDestination(self.function),
                s3.NotificationKeyFilter(prefix=config.source_prefix, suffix=suffix),
            )
