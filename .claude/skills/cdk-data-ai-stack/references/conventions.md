# Conventions

How `infra/` is organized and the rules for adding to it. Update this file when a
convention changes or a new one gets established — don't let it drift from reality.

## Layout

```
infra/
├── app.py                        entry point, instantiates the stack(s)
├── cdk.json                      CDK app config
├── requirements.txt              CDK app's own deps (aws-cdk-lib, constructs, boto3, awscli)
├── requirements-dev.txt          test-only deps (pytest)
├── infra/
│   ├── infra_stack.py            top-level stack, wires constructs together
│   └── constructs/
│       ├── network.py            NetworkConstruct — VPC (+ S3 gateway endpoint)
│       ├── database.py           DatabaseConstruct — Aurora Serverless v2 Postgres
│       ├── example_lambda.py     ExampleLambdaConstruct — Lambda pattern
│       ├── client_config.py      ClientPipelineConfig — per-client config dataclass (not a construct)
│       ├── landing_bucket.py     LandingBucketConstruct — per-client S3 landing bucket
│       ├── transform_lambda.py   TransformLambdaConstruct — S3-triggered ETL Lambda
│       └── client_pipeline.py    ClientPipelineConstruct — composes the two above per client
├── lambda_src/
│   └── <function_name>/
│       ├── handler.py
│       └── requirements.txt      that function's OWN runtime deps, separate from infra/requirements.txt
└── tests/unit/                   pytest + aws_cdk.assertions, no live AWS calls
```

## Rules

- **One construct, one file, under `infra/infra/constructs/`.** A construct is a
  reusable unit (a VPC, a database, a Lambda pattern) — not a whole stack. Stacks
  compose constructs; keep `infra_stack.py` itself thin (wiring, not resource detail).
- **One Lambda, one folder under `lambda_src/`,** named after the function, with its
  own `requirements.txt` for runtime deps. Never put a Lambda's runtime deps in the
  top-level `infra/requirements.txt` — that file is for the CDK app itself (which
  runs on the dev machine / CI, not in the Lambda runtime).
- **No hardcoded AWS account IDs or regions** in stack code. Either leave the stack
  environment-agnostic (default) or pull account/region from `CDK_DEFAULT_ACCOUNT` /
  `CDK_DEFAULT_REGION` env vars — see `references/setup-checklist.md`.
- **New pattern, new construct file + a `lambda-patterns.md` or `sql-patterns.md`
  entry.** Copying an existing construct and adapting it is expected and good; when
  you do, add a line to the relevant reference file so the next copy doesn't
  rediscover the same tradeoffs.
- **A plain config object shared by a family of related constructs** (e.g.
  `ClientPipelineConfig`, used by `LandingBucketConstruct`,
  `TransformLambdaConstruct`, and `ClientPipelineConstruct`) gets its own small
  module under `constructs/` too, even though it isn't itself a construct —
  this avoids circular imports between the constructs that all depend on it.
  Keep it a plain dataclass with validation in `__post_init__`, not a construct
  subclass.
- Tests use `aws_cdk.assertions.Template` against a synthesized stack — no real AWS
  calls, no `cdk deploy` in CI/test runs.

## Multiple projects on this baseline

`DataAiBaselineStack` in `infra_stack.py` is the starting template, not a singleton
you're stuck extending forever. When a `lab/` project needs its own infra that
diverges meaningfully (different DB engine, no VPC needed, etc.), copy the constructs
that still apply and give the new stack its own class/file rather than overloading
one stack with unrelated resources. Record that split as a decision in
`decisions.md` when it happens.
