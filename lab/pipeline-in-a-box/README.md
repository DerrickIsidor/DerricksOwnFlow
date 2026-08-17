# Pipeline-in-a-Box

Derrick's first productized service business — a done-for-you ETL pipeline (client data
-> AWS -> Aurora Postgres) feeding an auto-refreshing Power BI dashboard, plus a weekly
written insight note. Launched alongside his day job at an airline; goal is a paying
client within a 6-week challenge.

This folder is the business/go-to-market side, not the technical build. The technical
build (when a client signs) goes through `data-team-lead` and the relevant specialists,
likely landing in its own client-specific subfolder or in `infra/` depending on scope.

## Contents (`engineering/`)

Design docs only so far — nothing here is built or deployed yet.

- `orchestrator-design.md` — the weekly insight-note pipeline that runs on Derrick's
  homelab (TrueNAS), pulls client metrics, and drafts the written insight note. Its
  data-access-to-Aurora decision (§2) is still open.
- `slack-command-center-design.md` — the remote command-and-notification layer: a
  custom Slack bot bridging Slack (from Derrick's phone) to local Claude Code subagents
  on the same homelab box, plus AWS SES email delivery for client notes and Derrick's
  own ops digest. Extends `orchestrator-design.md`; read that one first.

## Contents (`business/`)

1. `01-pitch-positioning.md` — one-page pitch, plain language, two tiers, why-now angle.
2. `02-icp-prospecting.md` — qualifying criteria and concrete prospecting method per
   segment, with real (verified) directories/associations as starting points.
3. `03-outreach-templates.md` — first-touch DM/email templates, warm and cold variants.
4. `04-linkedin-post-1.md` — draft build-in-public post #1 announcing the challenge.
5. `05-pricing-sanity-check.md` — Starter/Growth pricing checked against real market
   comparables, with a labeled-as-rough recommendation.
6. `06-business-plan.md` — market sizing, phased roadmap (2H26 / 1H27 foundation window
   / 3-5yr build-out), and honest risks, sitting above the 6-week challenge.
7. `07-financial-model.md` — unit economics, solo capacity ceiling, and MRR milestone
   math behind the business plan, sourced from real AWS pricing and specialist hours
   estimates rather than guessed.
8. `08-org-chart.md` — the real local subagent roster (`.claude/agents/*.md`) mapped to
   corporate roles, and the human-only accountability lines (money, legal, client
   relationships) that never move.
9. `09-advisory-board.md` — 6 "mastermind alliance" advisor lenses (Naval Ravikant,
   Warren Buffett, Paul Graham, Peter Drucker, Atul Gawande, Jim Collins) — real public
   principles applied as decision-making tools, explicitly not role-play or endorsement.
10. `10-operating-rhythm.md` — the ongoing Monday/Wednesday/Friday team-session cadence
    (extended past the 6-week challenge), what gets reported to Derrick and how often,
    and the near-term file-based bridge for durable notifications until the Slack bot
    exists.
11. `11-legal-financial-foundation.md` — educational (not legal/tax advice) walkthrough
    of Georgia LLC formation, when an S-corp election starts paying off, business
    banking, starter MSA/SOW/NDA contract templates, and the HIPAA/BAA flag for any
    home-health client.

## Status

Week 1, Day 1 of the 6-week challenge. Segment is not locked — casting wide across
general aviation ops, auto repair, home health/elder care, accounting/tax prep, plus
personal network, and letting the first real yes set the direction.
