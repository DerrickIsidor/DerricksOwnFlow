import aws_cdk as core
import aws_cdk.assertions as assertions

from infra.infra_stack import DataAiBaselineStack


def _synth_template():
    app = core.App()
    stack = DataAiBaselineStack(app, "TestStack")
    return assertions.Template.from_stack(stack)


def test_vpc_created_with_no_nat_gateways():
    template = _synth_template()
    template.resource_count_is("AWS::EC2::VPC", 1)
    template.resource_count_is("AWS::EC2::NatGateway", 0)


def test_aurora_serverless_v2_cluster_created():
    template = _synth_template()
    template.has_resource_properties(
        "AWS::RDS::DBCluster",
        {
            "Engine": "aurora-postgresql",
        },
    )


def test_example_lambda_created_in_vpc():
    template = _synth_template()
    template.resource_count_is("AWS::Lambda::Function", 1)
