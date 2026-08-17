from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from .client_config import ClientPipelineConfig
from .landing_bucket import LandingBucketConstruct
from .transform_lambda import TransformLambdaConstruct


class ClientPipelineConstruct(Construct):
    """One client's whole Pipeline-in-a-Box pipeline: a landing bucket + the
    transform Lambda wired to it, both driven by a single
    `ClientPipelineConfig`. This is the reusable unit real client onboarding
    instantiates -- see
    ../../.claude/skills/cdk-data-ai-stack/references/decisions.md
    ("Multi-tenant parameterization").

    Reuses the CALLER's existing VPC and database (pass in
    `network.vpc` / `database.secret` from the baseline stack) -- it does not
    stand up its own VPC or Aurora cluster. Onboarding a new client is meant
    to look like this, inside `DataAiBaselineStack` (or wherever the shared
    Network/Database constructs live) -- NOT a new stack, NOT a copy-pasted
    construct file:

        ClientPipelineConstruct(
            self,
            "ClientPipelineAcmeCo",
            vpc=network.vpc,
            db_secret=database.secret,
            db_name="app",
            config=ClientPipelineConfig(client_id="acme-co"),
        )

    Callers still need to do one thing at the stack level after constructing
    this: `database.connections.allow_default_port_from(pipeline.function)` --
    same as every other DB-connected Lambda in this repo, see
    lambda-patterns.md for why that stays out of the construct itself.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.Vpc,
        db_secret,
        db_name: str,
        config: ClientPipelineConfig,
    ) -> None:
        super().__init__(scope, construct_id)

        self.config = config

        self.landing = LandingBucketConstruct(self, "Landing", config=config)

        self.transform = TransformLambdaConstruct(
            self,
            "Transform",
            vpc=vpc,
            db_secret=db_secret,
            db_name=db_name,
            landing_bucket=self.landing.bucket,
            config=config,
        )

    @property
    def function(self):
        return self.transform.function

    @property
    def bucket(self):
        return self.landing.bucket
