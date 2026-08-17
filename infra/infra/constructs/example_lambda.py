from aws_cdk import Duration
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class ExampleLambdaConstruct(Construct):
    """Baseline pattern: a Lambda in the same VPC as the database, with the
    DB secret ARN injected via environment variable and read access granted.
    Copy this pattern for new data/AI Lambdas rather than starting from
    scratch -- see ../../.claude/skills/cdk-data-ai-stack/references/lambda-patterns.md.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.Vpc,
        db_secret,
        db_name: str,
    ) -> None:
        super().__init__(scope, construct_id)

        self.function = _lambda.Function(
            self,
            "Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("lambda_src/example_handler"),
            timeout=Duration.seconds(30),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            environment={
                "DB_SECRET_ARN": db_secret.secret_arn,
                "DB_NAME": db_name,
            },
        )
        db_secret.grant_read(self.function)
