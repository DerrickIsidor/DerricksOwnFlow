# Setup Checklist: Scaffolded → Actually Deployed

Status as of 2026-08-13. Update the checkboxes/status as steps get done — this file
should always reflect where the repo actually is, not where it was when written.

## Done

- [x] AWS CLI installed (`pip install --user awscli`, v1.46.0). **Not on PATH** —
      invoke via `python -m awscli`, or use the one inside `infra/.venv/Scripts/`
      once that venv is activated. Fixing PATH properly is a manual step (add
      `%APPDATA%\Python\Python311\Scripts` on Windows), not done automatically.
- [x] AWS CDK CLI installed globally via npm (`npm install -g aws-cdk`, v2.1136.0).
- [x] `infra/` scaffolded: `cdk init app --language python`, customized with
      `DataAiBaselineStack` (VPC + Aurora Serverless v2 Postgres + example Lambda).
- [x] Dependencies installed into `infra/.venv`, unit tests pass
      (`pytest tests/` — 3/3 passing), `cdk synth` succeeds and produces a valid
      CloudFormation template with the expected VPC/RDS/Lambda resources.

## Not done — needs you

- [ ] **AWS account + credentials.** No AWS account details or credentials exist in
      this repo or environment. Configure via `aws configure` (or
      `aws configure sso` for SSO) once you have an account/IAM user ready. Never
      commit credentials to this repo — `.env` and `*.key` are already gitignored,
      but double-check before any commit that touches `infra/`.
- [ ] **`cdk bootstrap`.** One-time per AWS account+region — creates the S3
      bucket/IAM roles CDK needs to deploy. Real AWS resources, has a small ongoing
      cost (the S3 bucket). Run this yourself after credentials are configured:
      `cdk bootstrap aws://<ACCOUNT_ID>/<REGION>`.
- [ ] **Decide Aurora Serverless v2 vs. plain RDS instance** — see `decisions.md` and
      `sql-patterns.md`. Cost tradeoff, not yet resolved.
- [ ] **First `cdk deploy`.** Do not run this without confirming with the user first
      (same bar as `git push`) — it creates real, billed AWS resources.
- [ ] **Node.js upgrade.** `cdk synth`/`cdk deploy` currently warn loudly that Node
      v19.3.0 (installed on this machine) is end-of-life; CDK CLI support for it
      ends soon. Works today but should move to Node 22 or 24 before it becomes a
      hard blocker. Not fixed as part of this setup — flagged here and in
      `docs/bungi/GAPS.md`.

## Quick reference

```bash
cd infra
# activate the venv (Windows / git bash)
source .venv/Scripts/activate

pytest tests/ -q          # run unit tests, no AWS calls
cdk synth                 # render CloudFormation, no AWS calls, no credentials needed
cdk diff                  # needs credentials + prior deploy to compare against
cdk deploy                # needs credentials + bootstrap; real AWS changes, confirm first
```
