# Research Log

Dated entries for anything pulled in from outside the repo to close a knowledge
gap — maintained by the `bungi` agent. Each entry: the question, what was found,
sources, and what it changes here.

---

## 2026-08-13 — Locating real sources for 5 requested Claude Code skills

**Question:** User asked to add 5 named agent skills (`prompt-engineer`,
`skill-creator`, `mcp-builder`, `agentic-eval`, `openai-docs`) — needed to find their
actual upstream source repos rather than write approximations.

**Found:**
- `skill-creator`, `mcp-builder` → official Anthropic skills, `anthropics/skills`
  (Apache-2.0).
- `agentic-eval` → `github/awesome-copilot` (MIT), `skills/agentic-eval/SKILL.md`.
- `prompt-engineer` → `davila7/claude-code-templates` (Apache-2.0),
  `cli-tool/components/skills/ai-research/prompt-engineer/SKILL.md` — itself sourced
  from `vibeship-spawner-skills` per its own frontmatter.
- `openai-docs` → `openai/skills` (Apache-2.0), `skills/.curated/openai-docs/` —
  written for OpenAI's Codex CLI; depends on the `openaiDeveloperDocs` MCP server
  (`https://developers.openai.com/mcp`), now registered in this repo's `.mcp.json`.

Matched against a third-party blog listicle (agentailor.com, "Top 5 Agent Skills
Every Agent Builder Should Install") that named the same 5 skills with the same
source attributions — used as a cross-check, not as the install source itself; actual
files were pulled directly from each skill's own GitHub repo via `gh api`.

**What it changes:** `.claude/skills/*` now contains the real upstream content
(including `references/`/`scripts/` subfolders for `mcp-builder`, `skill-creator`,
`openai-docs`), not reconstructed text. See `.claude/skills/README.md` for the
per-skill source table. `openai-docs`'s Codex-specific MCP-install fallback command
was adapted to the Claude Code equivalent — see the note at the top of its
`SKILL.md`.
