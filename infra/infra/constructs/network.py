from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class NetworkConstruct(Construct):
    """Baseline VPC: isolated subnets only, no NAT gateway.

    No NAT gateway keeps this near-zero cost when idle -- NAT gateways bill
    hourly plus per-GB processed even at rest. Isolated subnets can still reach
    AWS services via VPC endpoints if something in here needs S3/Secrets Manager
    without a public route. See ../../.claude/skills/cdk-data-ai-stack/references/decisions.md.

    Includes an S3 Gateway VPC Endpoint -- unlike an Interface endpoint, S3 (and
    DynamoDB) Gateway endpoints have no hourly charge, so this is "free" the
    same way isolated-subnets-only is: it lets anything in this VPC (e.g. the
    Pipeline-in-a-Box transform Lambda) reach S3 without a NAT gateway. See
    decisions.md ("S3 access from isolated subnets: Gateway endpoint, not NAT").
    """

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.vpc = ec2.Vpc(
            self,
            "Vpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        self.s3_gateway_endpoint = self.vpc.add_gateway_endpoint(
            "S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
        )
