#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infra.infra_stack import DataAiBaselineStack

# Pipeline-in-a-Box: no real client exists yet (week 1 scaffold), so `clients`
# stays empty below. Once a real client is ready to onboard, add an entry
# here (or wherever this app gets its client list from -- e.g. a config file
# read before app.py runs) -- see
# .claude/skills/cdk-data-ai-stack/references/decisions.md
# ("Multi-tenant parameterization") for the shape:
#
#   from infra.constructs.client_config import ClientPipelineConfig
#   clients = [ClientPipelineConfig(client_id="acme-co")]
#
# then pass `clients=clients` to DataAiBaselineStack below.

app = cdk.App()
DataAiBaselineStack(app, "DataAiBaselineStack",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

app.synth()
