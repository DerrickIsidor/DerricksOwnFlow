import json
import os

import boto3

secrets_client = boto3.client("secretsmanager")


def handler(event, context):
    """Baseline example: prove the Lambda can reach its DB credentials.

    This does not open a database connection yet -- it only demonstrates the
    wiring (VPC placement, Secrets Manager access, IAM grant). Add a Postgres
    driver (pg8000 is in requirements.txt -- pure Python, no Docker bundling
    needed) and the actual query once there's a real schema to query. See
    ../../../.claude/skills/cdk-data-ai-stack/references/lambda-patterns.md.
    """
    secret_arn = os.environ["DB_SECRET_ARN"]
    secret = secrets_client.get_secret_value(SecretId=secret_arn)
    creds = json.loads(secret["SecretString"])

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "DB credentials reachable",
                "db_host": creds.get("host"),
                "db_name": os.environ.get("DB_NAME"),
            }
        ),
    }
