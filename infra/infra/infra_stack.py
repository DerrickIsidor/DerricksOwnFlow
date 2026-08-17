from aws_cdk import Stack
from constructs import Construct

from .constructs.client_config import ClientPipelineConfig
from .constructs.client_pipeline import ClientPipelineConstruct
from .constructs.database import DatabaseConstruct
from .constructs.example_lambda import ExampleLambdaConstruct
from .constructs.network import NetworkConstruct


class DataAiBaselineStack(Stack):
    """Baseline data/AI stack: VPC + Aurora Serverless v2 Postgres + one example
    Lambda wired to it. Starting point to copy/extend per project, not meant to
    be deployed as-is forever -- see
    .claude/skills/cdk-data-ai-stack/references/conventions.md.

    Also hosts zero or more Pipeline-in-a-Box client pipelines (a landing S3
    bucket + transform Lambda per client, see `ClientPipelineConstruct`), each
    sharing this stack's VPC/database rather than standing up their own -- see
    .claude/skills/cdk-data-ai-stack/references/decisions.md
    ("Multi-tenant parameterization"). Pass `clients=[ClientPipelineConfig(...),
    ...]` to onboard one; empty by default so this stack still synths to just
    the original baseline when no client exists yet.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        clients: list[ClientPipelineConfig] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        network = NetworkConstruct(self, "Network")

        database = DatabaseConstruct(self, "Database", vpc=network.vpc)

        lambda_construct = ExampleLambdaConstruct(
            self,
            "ExampleLambda",
            vpc=network.vpc,
            db_secret=database.secret,
            db_name="app",
        )
        database.connections.allow_default_port_from(lambda_construct.function)

        # Pipeline-in-a-Box: one ClientPipelineConstruct per onboarded client.
        # Construct ID is derived from client_id (CDK construct IDs must be
        # alphanumeric); the config itself already validates client_id is a
        # safe slug, see client_config.py.
        self.client_pipelines: dict[str, ClientPipelineConstruct] = {}
        for client_config in clients or []:
            construct_id_suffix = client_config.client_id.title().replace("-", "")
            pipeline = ClientPipelineConstruct(
                self,
                f"ClientPipeline{construct_id_suffix}",
                vpc=network.vpc,
                db_secret=database.secret,
                db_name="app",
                config=client_config,
            )
            database.connections.allow_default_port_from(pipeline.function)
            self.client_pipelines[client_config.client_id] = pipeline
