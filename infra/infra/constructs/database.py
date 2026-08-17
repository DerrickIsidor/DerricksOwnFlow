from aws_cdk import RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from constructs import Construct


class DatabaseConstruct(Construct):
    """Aurora Serverless v2 Postgres, single writer instance, isolated subnets.

    Cost note: Serverless v2 has an always-on capacity floor -- it does not
    scale to zero the way Aurora Serverless v1 could. min_capacity below is
    the cheapest floor AWS allows. A plain db.t4g.micro RDS instance (free-tier
    eligible for 12 months) is the cheaper alternative for a low-traffic personal
    project; this tradeoff is open, see
    ../../.claude/skills/cdk-data-ai-stack/references/decisions.md and
    references/sql-patterns.md.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.Vpc,
        database_name: str = "app",
    ) -> None:
        super().__init__(scope, construct_id)

        self.cluster = rds.DatabaseCluster(
            self,
            "Cluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_16_4
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            writer=rds.ClusterInstance.serverless_v2("Writer"),
            serverless_v2_min_capacity=0.5,
            serverless_v2_max_capacity=2,
            default_database_name=database_name,
            credentials=rds.Credentials.from_generated_secret("dbadmin"),
            removal_policy=RemovalPolicy.SNAPSHOT,
        )

    @property
    def secret(self):
        return self.cluster.secret

    @property
    def connections(self):
        return self.cluster.connections
