# Installed Skills

Project-level Claude Code skills, vendored from their upstream sources below.
Each is unmodified except where noted.

| Skill | What it's for | Source | License |
|---|---|---|---|
| `skill-creator` | Iterative cycle for building and evaluating new Claude Code skills, with variance analysis and eval scripts | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | Apache-2.0 |
| `mcp-builder` | Full MCP server dev guide (Python FastMCP + Node/TS SDK), with an evaluation harness | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/mcp-builder) | Apache-2.0 |
| `agentic-eval` | Self-critique loops, evaluator-optimizer pipelines, LLM-as-judge and rubric-based evaluation patterns | [github/awesome-copilot](https://github.com/github/awesome-copilot/blob/main/skills/agentic-eval/SKILL.md) | MIT |
| `prompt-engineer` | Prompt structure, context management, output formatting, and prompt evaluation | [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates/blob/main/cli-tool/components/skills/ai-research/prompt-engineer/SKILL.md) (itself sourced from `vibeship-spawner-skills`) | Apache-2.0 |
| `openai-docs` | Fetches current OpenAI developer docs (Responses API, Agents SDK, model guidance, etc.) via the `openaiDeveloperDocs` MCP server | [openai/skills](https://github.com/openai/skills/tree/main/skills/.curated/openai-docs) | Apache-2.0 |
| `cdk-data-ai-stack` | This repo's own growing knowledge base for `infra/` — AWS CDK (Python) conventions, architecture decisions, Lambda/SQL patterns. Not vendored — written for this repo, and expected to keep growing. | n/a (local) | n/a |
| `sql-data-engineering` | SQL, ETL/ELT, data warehousing (star schema, OLTP vs OLAP), batch vs streaming. Backs the `data-engineer` agent. | n/a (local) | n/a |
| `python-data-science` | pandas/numpy EDA, feature engineering, model selection. Backs the `data-scientist` agent. | n/a (local) | n/a |
| `aws-cloud-devops` | General AWS/cloud architecture, Docker/Kubernetes, Linux, Git, CI/CD, security zones — distinct from `cdk-data-ai-stack`'s repo-specific CDK conventions. Backs the `cloud-engineer` agent. | n/a (local) | n/a |
| `powerbi-dax-excel` | Power BI/DAX data modeling and measure patterns, Excel Power Pivot. Backs the `bi-analyst` agent. | n/a (local) | n/a |
| `data-business-strategy` | Framing a business case, data-team roles and hiring, prioritization — grounded in DJ Patil's *Building Data Science Teams*. Backs the `business-strategist` agent. | n/a (local) | n/a |

## The data/cloud team (milestone 1)

`.claude/agents/` also has five new specialist subagents built on the local skills
above — `cloud-engineer`, `data-engineer`, `data-scientist`, `bi-analyst`, and
`business-strategist` — plus `data-team-lead`, an orchestrator that routes multi-part
requests across them (and the existing `cdk-engineer`/`bungi`) and fans work out in
parallel when the parts are independent. Invoke `data-team-lead` for anything spanning
more than one specialty; invoke a specialist directly for a single-specialty task. Each
specialist may hand off to one adjacent specialist on its own (e.g. `data-engineer` →
`cloud-engineer` when a pipeline needs infrastructure decided) — see each agent's file
for its specific hand-off rule.

These five skills were drafted in one fast pass from a curated subset of
`docs/Data Science Cheat Sheet/` (SQL, Pandas, Data Engineering Cookbook, DAX, Building
Data Science Teams, docker CLI cheat sheets) plus general knowledge — not the full
skill-creator eval loop. If a specific one needs sharpening, run it through
`skill-creator`'s eval/iterate loop on real test prompts.

## Notes

- **`openai-docs`** was written by OpenAI for their Codex CLI. The doc-fetching workflow
  was adapted to work in Claude Code (see the note at the top of its `SKILL.md`) and
  needs the MCP server registered in this repo's `.mcp.json` — already set up. The
  skill's "Codex self-knowledge" section describes the Codex CLI product itself and
  doesn't apply here; it's left intact rather than stripped out, for fidelity to the
  source.
- All five are pulled in as-is from public repos, not written from scratch for this
  project. Re-sync a skill by re-fetching its SKILL.md (and any `references/`/`scripts/`
  subfolders) from the source link above if the upstream changes.
- Skill content is instructions to Claude, not application code — nothing here ships
  to the live site.
