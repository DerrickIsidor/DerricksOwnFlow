# Changelog

Maintained by the `bungi` agent (`.claude/agents/bungi.md`). Reverse-chronological.
Each entry: what changed, why, what it affects.

---

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
