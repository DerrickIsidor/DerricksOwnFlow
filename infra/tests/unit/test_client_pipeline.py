import aws_cdk as core
import aws_cdk.assertions as assertions
import pytest

from infra.constructs.client_config import ClientPipelineConfig
from infra.infra_stack import DataAiBaselineStack


def _synth_template(clients=None):
    app = core.App()
    stack = DataAiBaselineStack(app, "TestStack", clients=clients)
    return assertions.Template.from_stack(stack)


# --- ClientPipelineConfig: parameterization surface itself ---


def test_config_derives_defaults_from_client_id():
    config = ClientPipelineConfig(client_id="acme-co")
    assert config.target_schema == "public"
    assert config.target_table == "acme_co_raw"
    assert config.source_prefix == "acme-co/"
    assert config.file_suffixes == (".csv", ".json")


def test_config_respects_explicit_overrides():
    config = ClientPipelineConfig(
        client_id="acme-co",
        target_schema="raw",
        target_table="acme_extracts",
        source_prefix="incoming/acme/",
        file_suffixes=(".csv",),
    )
    assert config.target_schema == "raw"
    assert config.target_table == "acme_extracts"
    assert config.source_prefix == "incoming/acme/"
    assert config.file_suffixes == (".csv",)


@pytest.mark.parametrize(
    "bad_client_id",
    ["Not Valid!", "UPPERCASE", "-leading-hyphen", "has spaces", ""],
)
def test_config_rejects_unsafe_client_id(bad_client_id):
    with pytest.raises(ValueError):
        ClientPipelineConfig(client_id=bad_client_id)


@pytest.mark.parametrize("bad_schema", ["not-valid", "1leadingdigit", "has space"])
def test_config_rejects_unsafe_target_schema(bad_schema):
    with pytest.raises(ValueError):
        ClientPipelineConfig(client_id="acme-co", target_schema=bad_schema)


# --- Stack-level wiring: baseline stays intact with zero clients ---


def test_zero_clients_leaves_baseline_unchanged():
    template = _synth_template()
    template.resource_count_is("AWS::S3::Bucket", 0)
    template.resource_count_is("AWS::Lambda::Function", 1)  # just ExampleLambda
    template.resource_count_is("AWS::EC2::VPC", 1)
    template.resource_count_is("AWS::RDS::DBCluster", 1)


# --- Stack-level wiring: one client onboarded ---


def test_single_client_creates_landing_bucket_and_transform_lambda():
    template = _synth_template(clients=[ClientPipelineConfig(client_id="acme-co")])
    template.resource_count_is("AWS::S3::Bucket", 1)
    # ExampleLambda + this client's transform Lambda + CDK's shared
    # BucketNotificationsHandler custom-resource Lambda (only appears once a
    # bucket has an event notification wired to it).
    template.resource_count_is("AWS::Lambda::Function", 3)
    template.resource_count_is("Custom::S3BucketNotifications", 1)


def test_landing_bucket_blocks_public_access_and_is_encrypted():
    template = _synth_template(clients=[ClientPipelineConfig(client_id="acme-co")])
    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True,
            },
            "BucketEncryption": {
                "ServerSideEncryptionConfiguration": [
                    {
                        "ServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256",
                        }
                    }
                ]
            },
        },
    )


def test_transform_lambda_env_carries_client_config():
    template = _synth_template(
        clients=[
            ClientPipelineConfig(
                client_id="acme-co",
                target_schema="raw",
                target_table="acme_extracts",
            )
        ]
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Environment": {
                "Variables": {
                    "CLIENT_ID": "acme-co",
                    "TARGET_SCHEMA": "raw",
                    "TARGET_TABLE": "acme_extracts",
                    "DB_NAME": "app",
                }
            }
        },
    )


# --- Stack-level wiring: multiple clients get isolated resources ---


def test_multiple_clients_get_isolated_resources():
    configs = [
        ClientPipelineConfig(client_id="acme-co"),
        ClientPipelineConfig(client_id="widgets-inc"),
    ]
    template = _synth_template(clients=configs)
    template.resource_count_is("AWS::S3::Bucket", 2)
    # ExampleLambda + 2 transform Lambdas + 1 shared notifications handler
    # (CDK reuses one handler across all bucket notifications in a stack).
    template.resource_count_is("AWS::Lambda::Function", 4)
    template.resource_count_is("Custom::S3BucketNotifications", 2)
    # Only one VPC/database regardless of client count -- the whole point of
    # this pattern is NOT standing up a second VPC/Aurora cluster per client.
    template.resource_count_is("AWS::EC2::VPC", 1)
    template.resource_count_is("AWS::RDS::DBCluster", 1)
