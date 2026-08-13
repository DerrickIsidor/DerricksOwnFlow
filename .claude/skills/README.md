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
