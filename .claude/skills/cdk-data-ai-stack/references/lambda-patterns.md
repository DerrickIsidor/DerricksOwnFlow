# Lambda Patterns

Patterns for Lambda functions in `infra/`. See `ExampleLambdaConstruct`
(`infra/infra/constructs/example_lambda.py`) and `lambda_src/example_handler/` for
the reference implementation these patterns describe.

**S3-triggered Lambda:** see `TransformLambdaConstruct`
(`infra/infra/constructs/transform_lambda.py`) and
`lambda_src/transform_handler/` for the pattern of a Lambda that follows the
baseline VPC/secret wiring below *plus* an S3 event trigger and S3 read
access. Full rationale (trigger choice, per-client parameterization) is in
`references/s3-patterns.md`, not duplicated here.

## The baseline pattern

A Lambda that needs the database:
1. Gets placed in the same VPC, in `PRIVATE_ISOLATED` subnets (no internet access —
   see `conventions.md`).
2. Gets the DB secret ARN injected as an environment variable, not the credentials
   directly.
3. Gets `db_secret.grant_read(function)` for IAM access to that secret.
4. Gets `database.connections.allow_default_port_from(function)` on the *stack* side
   (not inside the construct) so the security group rule shows up where the two
   resources are wired together — see `infra_stack.py`.

Copy `ExampleLambdaConstruct` for a new Lambda that follows this shape rather than
writing the VPC/secret/SG wiring from scratch each time.

## Dependency packaging

- **Pure-Python deps (no C extensions)** — e.g. `pg8000`, most small utility
  libraries: put them in that Lambda's own `lambda_src/<name>/requirements.txt`, and
  before packaging run `pip install -r requirements.txt -t .` in that folder. No
  Docker needed. `cdk synth` does NOT do this automatically — it's a manual (or
  CI-scripted) pre-deploy step until this is automated.
- **Compiled deps (e.g. `psycopg2-binary`, `numpy`, `pandas`)** — need CDK's Docker
  asset bundling (`_lambda.Code.from_asset(path, bundling=...)`) to build for the
  Lambda's Linux runtime, since this dev machine is Windows. Docker is installed and
  available here. Not yet set up as a pattern in this repo — first Lambda that needs
  a compiled dependency should add it and record the pattern here.
- Never commit installed dependencies into `lambda_src/` in git — they're
  install/build artifacts, add the specific `lambda_src/*/` vendored-deps path to
  `.gitignore` if this pattern gets used.

## Open

- No Lambda layer pattern yet for deps shared across multiple functions — revisit
  once there's a second Lambda that needs the same dependency.
- No structured logging / observability pattern yet (e.g. Powertools for AWS Lambda).
  Worth adding once there's more than the one example function.
