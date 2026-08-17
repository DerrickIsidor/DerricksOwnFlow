# Research Log

Dated entries for anything pulled in from outside the repo to close a knowledge
gap — maintained by the `bungi` agent. Each entry: the question, what was found,
sources, and what it changes here.

---

## 2026-08-16 — Verifying AWS SES sandbox limits cited in slack-command-center-design.md

**Question:** `lab/pipeline-in-a-box/engineering/slack-command-center-design.md` §8
states SES sandbox limits (~200 msgs/24h, ~1 msg/sec, recipient must also be
SES-verified) and says production access needs a support-ticket-style request with
DNS/SPF/DKIM/DMARC already in place, "commonly cited around 24 hours" — but flags this
should be verified, not treated as permanent fact. Checked whether that's still
accurate.

**Found (WebSearch, 2026-08-16):** Confirmed accurate as written. AWS's own docs
(docs.aws.amazon.com/ses/latest/dg/request-production-access.html) and current
third-party guides agree: sandbox is capped at 200 messages/24h and 1 message/second,
sending only to SES-verified addresses/domains or the SES mailbox simulator.
Production-access requests typically get an initial AWS response within 24 hours (may
take longer if AWS needs more info). One figure worth adding to the design doc if it's
revisited: post-production starting limits commonly run around 50,000 messages/day and
14 messages/second as of mid-2026 (varies by account/region) — the design doc doesn't
currently state a post-sandbox number, only the sandbox cap.

**What it changes:** Downgrades this from an open research item to confirmed —
`slack-command-center-design.md` §8 doesn't need correction, only the optional addition
of the post-sandbox figure above if useful later. No code or infra change implied; SES
isn't connected yet (see `GAPS.md`, "No SES domain verification done").

**Sources:** [docs.aws.amazon.com/ses/latest/dg/request-production-access.html](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html), [oneuptime.com — Move Amazon SES Out of Sandbox](https://oneuptime.com/blog/post/2026-02-12-move-amazon-ses-out-of-sandbox/view), [sendops.dev — Amazon SES Sending Limits](https://sendops.dev/guides/amazon-ses-sending-limits/)

## 2026-08-16 — Verifying GA LLC filing fees cited in 11-legal-financial-foundation.md

**Question:** `lab/pipeline-in-a-box/business/11-legal-financial-foundation.md` §2
states Georgia Articles of Organization filing = $110 total ($100 + $10 service charge)
and Annual Registration = $60 total ($50 + $10 service fee), both flagged in the doc's
own disclaimer as "verify the live number on the official site before filing."

**Found (WebSearch, 2026-08-16):** Both figures check out against current (2026)
third-party filing guides that themselves cite sos.ga.gov/ecorp.sos.ga.gov — $110
Articles of Organization, $60/yr Annual Registration is the most commonly cited current
figure (one lower-quality source listed $50+$10 without confirming the total, consistent
with $60). Did not fetch sos.ga.gov directly (WebFetch wasn't used for this pass); this
is a cross-check of secondary sources agreeing with the doc's own numbers, not a
first-party confirmation. Recommend an actual sos.ga.gov fetch before Derrick files, per
the doc's own instruction — this research pass lowers the confidence gap but doesn't
fully close it.

**What it changes:** No correction needed to `11-legal-financial-foundation.md` §2 as
written. Leaves the doc's own "verify before filing" instruction intact rather than
downgrading it, since this check used secondary sources, not sos.ga.gov itself.

**Sources:** [bizreport.com — Articles of Organization Georgia](https://www.bizreport.com/articles-of-organization-georgia), [bizreport.com — Georgia Annual Registration Fee](https://www.bizreport.com/annual-registration-llc-georgia), [llcuniversity.com — Georgia LLC Annual Registration](https://www.llcuniversity.com/georgia-llc/annual-report/)

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
