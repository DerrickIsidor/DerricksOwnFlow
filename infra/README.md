# infra — AWS CDK (Python)

Derrick's baseline AWS CDK stack for data/AI projects: a VPC, an Aurora Serverless v2
Postgres database, and one example Lambda wired to it (`DataAiBaselineStack`).
Separate from `lab/` (which doesn't deploy anywhere) and from the website (which
deploys via GitHub Pages, not CDK).

This is a **starting point that's meant to grow**. The conventions, decisions, and
patterns behind the code here live in
[`.claude/skills/cdk-data-ai-stack/`](../.claude/skills/cdk-data-ai-stack/SKILL.md) —
read that before extending this, and add to it when you learn something new. The
`cdk-engineer` agent (`.claude/agents/cdk-engineer.md`) knows to do this automatically.

## Quickstart

```bash
cd infra
source .venv/Scripts/activate      # Windows/git-bash; .venv already exists with deps installed
pytest tests/ -q                   # unit tests, no AWS calls, no credentials needed
cdk synth                          # renders CloudFormation, no AWS calls needed
```

Both of the above already pass/succeed as of this writing — see
`.claude/skills/cdk-data-ai-stack/references/setup-checklist.md` for exactly what's
done vs. what still needs you (AWS credentials, `cdk bootstrap`, and a real
`cdk deploy` — none of which have happened yet).

## Structure

See `.claude/skills/cdk-data-ai-stack/references/conventions.md` for the full layout
and rules. Short version: one construct per file under `infra/infra/constructs/`,
one Lambda per folder under `lambda_src/`, `infra_stack.py` just wires them together.

## Pipeline-in-a-Box

`DataAiBaselineStack` also hosts zero or more per-client ETL pipelines (S3 landing
bucket → S3-triggered transform Lambda → Aurora Postgres), reusing this stack's
existing VPC/database rather than standing up a new one per client. Onboarding a
client is "instantiate `ClientPipelineConfig(client_id=...)` and pass it into
`DataAiBaselineStack(..., clients=[...])`" — see `app.py` and
`.claude/skills/cdk-data-ai-stack/references/s3-patterns.md` for the full
parameterization shape and open items (no real client onboarded yet).

Design docs for two more Pipeline-in-a-Box pieces live in
`lab/pipeline-in-a-box/engineering/` (not built yet): the weekly insight-note
orchestrator (`orchestrator-design.md`), and a remote Slack command/notification layer
(`slack-command-center-design.md`) whose email piece (AWS SES domain identity/DKIM/IAM)
becomes `infra/` work once AWS credentials are connected.

## Useful commands

- `cdk ls` — list stacks in the app
- `cdk synth` — render CloudFormation (no AWS calls)
- `cdk diff` — compare against what's deployed (needs credentials + a prior deploy)
- `cdk deploy` — deploy to AWS (needs credentials + `cdk bootstrap`; **confirm before
  running, real billed resources**)
