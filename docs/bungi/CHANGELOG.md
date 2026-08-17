# Changelog

Maintained by the `bungi` agent (`.claude/agents/bungi.md`). Reverse-chronological.
Each entry: what changed, why, what it affects.

---

## 2026-08-16 — Pipeline-in-a-Box launched: business docs, reusable multi-tenant CDK pipeline, verified ETL template, two homelab design docs

Derrick's first productized service business, launched today, split across a business
track and an engineering track, both under `lab/pipeline-in-a-box/`. Business/day-job
status unchanged — this is a nights/weekends build alongside his airline job (per
`lab/pipeline-in-a-box/README.md:5-6`), week 1 day 1 of a stated 6-week challenge, no
segment locked yet.

**Business track** (`lab/pipeline-in-a-box/business/`, 11 numbered docs, verified by
reading each): `01-pitch-positioning.md` (pitch/two-tier positioning), `02-icp-
prospecting.md` (4 segments — general aviation ops, auto repair, home health/elder
care, accounting/tax prep — each with named real directories, e.g. AOPA Airports
Directory, NATA), `03-outreach-templates.md`, `04-linkedin-post-1.md`, `05-pricing-
sanity-check.md` (current pricing: Starter $750 setup + $300/mo, Growth $2,000 setup +
$750/mo; verdict — setup fees well-calibrated, monthly retainers underpriced vs. market
on purpose or not), `06-business-plan.md`, `07-financial-model.md` (real inputs cited
by source and date — AWS cost floor ≈$44.60/mo from `cloud-engineer` reading `infra/
infra/constructs/database.py` directly, onboarding/maintenance hours from `data-
engineer`/`bi-analyst` reading the actual ETL template and star schema, all dated
2026-08-16, explicitly "revisit once client #1 produces real numbers — nothing below is
measured yet"), `08-org-chart.md` (maps the real `.claude/agents/*.md` roster to
corporate roles; explicitly not a legal org chart — Derrick is the only human/legal
person), `09-advisory-board.md` (6 thinker-inspired decision lenses — Ravikant,
Buffett, Graham, Drucker, Gawande, Collins — with an explicit disclaimer that nothing
attributed to them is a real quote or endorsement), `10-operating-rhythm.md` (Mon/Wed/
Fri cadence extending the 6-week challenge's pattern; names a near-term durable-
notification bridge, a new `lab/pipeline-in-a-box/business/ops-log.md` file, as "usable
starting this week" — **not yet created**, see Gaps), `11-legal-financial-foundation.md`
(GA LLC formation steps with real Sec-of-State fees as of Aug 2026 — $110 formation +
$60/yr annual registration — MSA/SOW/NDA starter contract templates, and an explicit
HIPAA/BAA flag for any home-health client, §6).

**Engineering track:**
- `infra/infra/constructs/client_pipeline.py`, `client_config.py`, `landing_bucket.py`,
  `transform_lambda.py` — a new reusable multi-tenant pattern: `ClientPipelineConfig`
  (validated dataclass, `client_id`/`target_schema`/`target_table`/`source_prefix`
  checked against safe-identifier regexes at construct time) feeds one
  `ClientPipelineConstruct` (S3 landing bucket + S3-event-triggered transform Lambda)
  per client, composed into the existing `DataAiBaselineStack` via a new `clients:
  list[ClientPipelineConfig]` constructor arg (`infra/infra/infra_stack.py:26-65`) —
  no new stack, no new VPC/Aurora per client. `infra/lambda_src/transform_handler/
  handler.py` exists as the Lambda entry point. Decisions recorded in
  `.claude/skills/cdk-data-ai-stack/references/decisions.md` (2026-08-16 entries).
  Verified: `pytest tests/ -q` inside `infra/.venv` — **18 passed** (3 prior baseline
  tests, per the 2026-08-13 entry below, + 15 new in `tests/unit/test_client_pipeline.py`
  covering config validation — including 8 parametrized bad-input cases — zero/one/
  multi-client stack synth, bucket public-access/encryption properties, and Lambda
  env-var wiring).
- `lab/pipeline-in-a-box/engineering/etl-template/` — a full extract/transform/load
  template (`etl/extract.py`, `transform.py`, `load.py`, `pipeline.py`) against
  synthetic auto-repair-shop data (15 customers/30 repair orders/27 payments,
  `data/raw/`), a star schema (`sql/schema.sql`: 3 dims + 2 facts, natural-key upserts,
  one transaction per file), pg8000 driver (matches `infra/`'s existing Lambda driver
  choice). Verified, not just written: `python -m pytest tests/ -v` — **14 passed**
  (`test_extract_transform.py`, and `test_load_sql.py` which parses `sql/schema.sql`
  and every `load.py` INSERT with `pglast`, a real Postgres-grammar parser, to catch
  column-name drift without a live DB). README also documents an end-to-end run against
  a real throwaway Postgres 16 Docker container (all rows loaded, idempotent re-run
  verified, zero data-quality warnings) — that run isn't independently re-verified by
  this Bungi pass, only the doc's own account of it and the two committed test files.
- `lab/pipeline-in-a-box/engineering/orchestrator-design.md` — design-only doc (no
  build, explicitly gated) for a weekly insight-note generator running on Derrick's
  TrueNAS homelab. §2 leaves the Aurora data-access path from an outside-AWS homelab box
  explicitly undecided (3 options weighed — a narrow authenticated read Lambda, a
  scheduled S3 export, or a VPN tunnel — recommendation is Option A but "revisit in week
  3, not locked in now").
- `lab/pipeline-in-a-box/engineering/slack-command-center-design.md` — design-only doc
  for a Slack-to-local-subagent bridge (Socket Mode, Derrick-only allowlist by Slack
  user ID, hardcoded command allowlist excluding `cdk deploy`/`destroy`/`bootstrap` in
  phase 1) plus AWS SES email delivery. Explicitly rules out Anthropic's own Claude Tag
  for Slack (§0 — can't reach a local repo or trigger this repo's local subagents).
- `infra/README.md` already updated with a "Pipeline-in-a-Box" section pointing at the
  above (`infra/README.md:34-48`) — confirmed current, no separate doc update needed.

**Not done, confirmed by reading each doc's own "what's still open" section, not
inferred:** no AWS deploy (`infra/README.md:23-26`, `orchestrator-design.md:6`,
`slack-command-center-design.md:7`), no AWS credentials connected in this environment
(`slack-command-center-design.md:6`), the Aurora-from-homelab data-access decision is
open (`orchestrator-design.md` §2, §7), no Slack app/workspace exists yet
(`slack-command-center-design.md` §10 Phase 0 not started), no SES domain verification
done (`slack-command-center-design.md` §8), no LLC filed and no attorney/accountant
review of any contract template (`11-legal-financial-foundation.md` §7), no real client
has been contacted yet (`README.md:57`, "letting the first real yes set the
direction"). Full prioritized next-work backlog logged in `GAPS.md` under "Pipeline-
in-a-Box — next work backlog."

## 2026-08-16 — Data/cloud team milestone 1: data-team-lead + 5 specialist agents + 5 local skills

Added a second layer of local subagents on top of `cdk-engineer`, aimed at general
data/cloud work (not just `infra/`): `.claude/agents/data-team-lead.md` (orchestrator,
`tools: Read, Grep, Glob, Bash, WebSearch, WebFetch, Skill, TodoWrite, Agent`) plus five
specialists — `cloud-engineer.md`, `data-engineer.md`, `data-scientist.md`,
`bi-analyst.md`, `business-strategist.md`. All six files are untracked
(`git status`) — not yet committed.

Delegation graph, verified by reading each agent's frontmatter `description` and body
(not inferred): `data-team-lead` can call all six others plus `bungi`. Single-hop-only
hand-offs from there: `cloud-engineer` → `cdk-engineer` only
(`.claude/agents/cloud-engineer.md:42`, "Only hand off to `cdk-engineer`"); `data-engineer`
→ `cloud-engineer` only (`data-engineer.md:41`); `data-scientist` → `data-engineer` or
`bi-analyst` (`data-scientist.md:41`, two options, not just `data-engineer`);
`bi-analyst` → `data-engineer` only (`bi-analyst.md:40`); `business-strategist` queries
the four technical specialists (`cloud-engineer`, `data-engineer`, `data-scientist`,
`bi-analyst`) for cost/feasibility input, and hands full execution to `data-team-lead`
once a case is approved (`business-strategist.md:44-46`).

Added five backing skills, each a single `SKILL.md` (~100-126 lines,
`.claude/skills/{aws-cloud-devops,sql-data-engineering,python-data-science,
powerbi-dax-excel,data-business-strategy}/SKILL.md`) drafted in one fast pass from a
curated subset of the newly-added `docs/Data Science Cheat Sheet/` (SQL, Pandas,
Data Engineering Cookbook, DAX/Data Modeling with DAX, DJ Patil's *Building Data
Science Teams*, Docker CLI/Dockerfile cheat sheets) plus general model knowledge — not
run through `skill-creator`'s eval/iterate loop. See open gap below.

Updated `.claude/skills/README.md` (new table rows + "The data/cloud team (milestone 1)"
section) and root `CLAUDE.md` (new "Data/cloud team" bullet list under "Lab & Agent
Tooling") to document the above, matching the existing `cdk-engineer`/`cdk-data-ai-stack`
documentation pattern. Both still show as modified-not-committed in `git status`.

`.gitignore` also shows a diff (`cdk.out/`, `.cdk.staging/`, `cdk.context.json`) but that
change is the CDK-ignore addition already recorded in the 2026-08-13 entry below — it
just hasn't been committed yet either; not new to this milestone.

**Not done in this change:** no eval/iterate pass on any of the 5 new skills against real
test prompts; no agents invoked end-to-end yet to confirm the routing/hand-off graph
works in practice, only that the files are internally consistent with each other.

## 2026-08-13 — AWS CDK baseline: infra/, cdk-engineer agent, cdk-data-ai-stack skill

Added `infra/` — an AWS CDK (Python) app, `DataAiBaselineStack`, scaffolded via
`cdk init app --language python` and then customized: a VPC with isolated subnets
and `nat_gateways=0` (`infra/infra/constructs/network.py`), an Aurora Serverless v2
Postgres cluster with a Secrets Manager-generated credential
(`infra/infra/constructs/database.py`), and one example Lambda in the same VPC that
reads the DB secret via `boto3` (`infra/infra/constructs/example_lambda.py`,
`infra/lambda_src/example_handler/handler.py`).

Installed AWS CLI (`pip install --user awscli`, v1.46.0 — not on PATH, see
`.claude/skills/cdk-data-ai-stack/references/setup-checklist.md`) and AWS CDK CLI
(`npm install -g aws-cdk`, v2.1136.0). Verified, not just assumed: `pytest tests/ -q`
inside `infra/.venv` passes 3/3, and `cdk synth` exits 0 and produces
`infra/cdk.out/DataAiBaselineStack.template.json` containing the expected
`AWS::EC2::VPC`, `AWS::RDS::DBCluster` (`aurora-postgresql`), and
`AWS::Lambda::Function` resources. No AWS credentials exist in this environment, so
nothing has been deployed — `cdk diff`/`cdk deploy` haven't been (and can't yet be)
run.

Added `.claude/agents/cdk-engineer.md` — the subagent for extending `infra/`; hard
rule not to run `cdk deploy`/`destroy`/`bootstrap` without confirming first.

Added `.claude/skills/cdk-data-ai-stack/` — unlike the 5 vendored skills, this one is
written for this repo and is explicitly meant to keep growing: `references/
conventions.md`, `decisions.md` (dated, append-only ADR log), `lambda-patterns.md`,
`sql-patterns.md`, `setup-checklist.md`.

Updated root `CLAUDE.md` and `.claude/skills/README.md` to reference all of the
above. Added `cdk.out/`, `.cdk.staging/`, `cdk.context.json` to `.gitignore`.

**Not done in this change:** no AWS credentials configured, no `cdk bootstrap`, no
deploy. The Aurora Serverless v2 vs. plain RDS instance cost tradeoff is explicitly
left open — see `GAPS.md`.

## 2026-08-13 — Repo tooling: agent skills, MCP, and lab structure

Installed 5 Claude Code skills into `.claude/skills/` (`skill-creator`, `mcp-builder`,
`agentic-eval`, `prompt-engineer`, `openai-docs`), sourced from their real upstream
repos rather than reconstructed from scratch — see `.claude/skills/README.md` for
exact sources and licenses (Apache-2.0 / MIT, all permissive).

Added `.mcp.json` registering the `openaiDeveloperDocs` MCP server, which the
`openai-docs` skill depends on to fetch live OpenAI documentation.

Added `lab/` — home for future AI/data projects, each in its own subfolder, separate
from the deployed website (`lab/README.md`).

Added `.gitignore` — the repo had none before this; covers secrets (`.env`, `*.key`),
Python/Node artifacts, and OS cruft. Matters now that `lab/` will hold projects that
touch API keys.

Updated root `CLAUDE.md` with a "Lab & Agent Tooling" section pointing at all of the
above.

Created this agent, `bungi` (`.claude/agents/bungi.md`), to keep `docs/bungi/`
current going forward — this file, `GAPS.md`, and `RESEARCH.md`.

**Not done in this change:** none of this touches the deployed site's file map or
editing instructions in `CLAUDE.md` — those are unchanged.
