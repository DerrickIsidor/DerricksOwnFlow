# Gaps

Live backlog, not a diary — maintained by the `bungi` agent. Status is one of
`open` / `investigating` / `resolved`. "Last verified" is the last date someone
(Bungi or otherwise) actually checked the current repo state, not just repeated an
earlier claim.

---

## Open — Pipeline-in-a-Box

- **Aurora-from-homelab data access is an open architecture decision, blocking the
  weekly insight-note orchestrator.** `lab/pipeline-in-a-box/engineering/
  orchestrator-design.md` §2: the TrueNAS homelab box is outside AWS entirely, and
  `infra/`'s VPC is isolated-subnet-only (no NAT, nothing inbound) — there is no
  network path today. 3 options weighed (narrow authenticated read Lambda, scheduled
  S3 export, VPN tunnel); doc recommends Option A but says explicitly "revisit in week
  3, not locked in now." Nothing can be built on the homelab side of the orchestrator
  until this is decided. Owner: `cloud-engineer` to make the call with real numbers,
  then `cdk-engineer` to build it. *First logged: 2026-08-16. Last verified:
  2026-08-16.*

- **Secrets Manager is unreachable from `infra/`'s isolated subnets — will surface as
  a Lambda timeout on first real invocation, including the new `TransformLambdaConstruct`.**
  No NAT gateway, no Secrets Manager VPC endpoint; every DB-secret-reading Lambda
  (`ExampleLambdaConstruct` and now every `ClientPipelineConstruct`'s transform Lambda)
  calls `secretsmanager:GetSecretValue` over a network path that doesn't exist yet.
  Not caught so far because nothing has been deployed for real. Fix options: a Secrets
  Manager Interface VPC endpoint (~$7-10/mo/AZ) or a NAT gateway (the cost this repo
  has specifically avoided). Decide before the first Lambda that reads a DB secret is
  actually invoked. Owner: `cdk-engineer`. See `.claude/skills/cdk-data-ai-stack/
  references/decisions.md` ("Open questions"). *First logged: 2026-08-13 (as a
  general `infra/` gap). Last verified: 2026-08-16 — now directly blocks Pipeline-in-
  a-Box's transform Lambda, not just the example one.*

- **No AWS credentials connected in this environment; nothing in `infra/` (baseline or
  Pipeline-in-a-Box additions) has ever been deployed.** `cdk synth`/`pytest` pass;
  `cdk deploy`/`cdk bootstrap`/`cdk diff` have not been run and can't be until Derrick
  connects credentials (in progress separately, per his own account). Blocks: the
  Aurora vs. RDS cost decision below, the Secrets Manager fix above, actually onboarding
  a real client's pipeline. Owner: Derrick (credential setup is human-only; nothing an
  agent can do). *First logged: 2026-08-13. Last verified: 2026-08-16.*

- **`10-operating-rhythm.md`'s near-term durable-notification bridge doesn't exist
  yet.** The doc (`lab/pipeline-in-a-box/business/10-operating-rhythm.md` §4) names a
  specific fix — "write the Friday summary into `lab/pipeline-in-a-box/business/
  ops-log.md`, starting this week" — but that file has not been created
  (`Glob lab/pipeline-in-a-box/business/ops-log.md` → no match, checked 2026-08-16).
  Until it exists, the weekly Friday summary described in that doc has nowhere durable
  to land. Owner: `bungi` (or `business-strategist`) creates it the first Friday the
  rhythm actually runs. *First logged: 2026-08-16. Last verified: 2026-08-16.*

- **No Slack app/workspace exists yet; `slack-command-center-design.md` is 100%
  unbuilt.** Design doc only, explicitly gated ("do not create a Slack app... without a
  separate, explicit go-ahead"). Phase 0 (Slack app skeleton) hasn't started. Owner:
  Derrick (creating the Slack app/tokens is a human action) then whichever specialist
  builds the bot process — the doc doesn't yet assign this to a specific named agent
  beyond "homelab-side `lab/pipeline-in-a-box/` work." *First logged: 2026-08-16. Last
  verified: 2026-08-16.*

- **No SES domain verification done; email delivery for the insight note and Slack
  bot's digest doesn't exist.** `slack-command-center-design.md` §8: domain
  verification + DKIM records aren't in place, SES account is (by default) in sandbox
  mode (~200 msgs/24h, recipient must also be SES-verified), and moving to production
  sending requires a support-ticket-style request with lead time. Nothing here has
  started. Owner: `cdk-engineer` for the domain identity/DKIM/IAM CDK construct (once
  AWS is connected), Derrick for the actual DNS changes and the production-access
  request. *First logged: 2026-08-16. Last verified: 2026-08-16.*

- **No GA LLC filed; Pipeline-in-a-Box is currently operating as an unincorporated
  sole proprietorship with no liability separation.** `11-legal-financial-foundation.md`
  §1-2 lays out the real formation steps and costs (~$110-260 to form, $60/yr after) but
  explicitly says this is educational scaffolding, not something to file today without
  review. Owner: Derrick (filing, paying, and signing are human-only actions no agent
  can perform). *First logged: 2026-08-16. Last verified: 2026-08-16.*

- **No contract template (MSA/SOW/NDA in `11-legal-financial-foundation.md` §5) has
  been reviewed by a licensed attorney.** Doc's own disclaimer states this explicitly
  and says not to use them with a real client before that review. Separately, no BAA
  template exists at all yet for the home-health segment (§6) — intentionally not
  drafted speculatively until a home-health prospect is actually close to signing.
  Owner: Derrick (retaining and paying an attorney is human-only). *First logged:
  2026-08-16. Last verified: 2026-08-16.*

- **No real client has been contacted yet.** `lab/pipeline-in-a-box/README.md:57`:
  "Segment is not locked... letting the first real yes set the direction." All 4 ICP
  segments (`02-icp-prospecting.md`) and their prospecting methods are designed but
  unexecuted. Owner: Derrick (outreach is his own relationship/time to spend, though
  `business-strategist` can help draft/refine messages from `03-outreach-templates.md`).
  *First logged: 2026-08-16. Last verified: 2026-08-16.*

- **Root `CLAUDE.md`'s "Lab & Agent Tooling" section doesn't mention
  `lab/pipeline-in-a-box/` at all.** It documents `lab/` generically, `infra/`,
  `cdk-engineer`, `cdk-data-ai-stack`, and the data/cloud team, but a reader relying on
  `CLAUDE.md` alone (per this repo's own instruction to treat it as authoritative)
  would not discover today's entire new business exists. Not fixed by Bungi per the
  read-only-outside-docs/bungi rule — flagged for whoever next edits `CLAUDE.md`.
  *First logged: 2026-08-16. Last verified: 2026-08-16 (grepped `CLAUDE.md` for
  "pipeline-in-a-box", no match).*

## Pipeline-in-a-Box — prioritized next-work backlog

Ordered by what's actually blocking vs. what can wait; each item names its owner.
Built from the "explicitly not decided or built yet" sections each design doc already
states honestly — not invented here.

**Tier 1 — blocking, do first:**
1. **Connect AWS credentials.** *Owner: Derrick.* Already in progress separately per
   his own account; nothing AWS-side (deploy, cost decisions that need real pricing
   confirmation, Secrets Manager fix) can proceed without this.
2. **Decide Aurora Serverless v2 vs. plain RDS instance cost tradeoff** (open since
   2026-08-13, now has real dollar figures in `07-financial-model.md`'s $44.60/mo
   floor to weigh against). *Owner: `cloud-engineer`* (with `business-strategist` input
   since it's now tied to real unit economics, not just an infra preference).
3. **Fix the Secrets-Manager-unreachable-from-isolated-subnet issue** before any real
   Lambda invocation (VPC endpoint vs. NAT gateway). *Owner: `cdk-engineer`.*
4. **Start real prospecting/outreach across the 4 ICP segments** — this is the
   actual product-market test the whole 6-week challenge is timed against, and nothing
   else in the backlog matters if no client signs. *Owner: Derrick*, using
   `02-icp-prospecting.md`/`03-outreach-templates.md` as the playbook;
   `business-strategist` available to refine messages per real replies.

**Tier 2 — needed before a real client can be onboarded, can run in parallel with
Tier 1's outreach:**
5. **Decide the orchestrator's §2 Aurora-from-homelab data-access architecture** (not
   before week 3 per the doc's own plan, but worth revisiting once AWS credentials
   exist and real client counts are known). *Owner: `cloud-engineer`* to decide, then
   *`cdk-engineer`* to build whichever option is chosen.
6. **Form the GA LLC and open a dedicated business bank account**, before taking any
   client's first payment. *Owner: Derrick* (filing, EIN application, banking are all
   human-only actions).
7. **Get the MSA/SOW/NDA templates reviewed by a licensed GA attorney.** *Owner:
   Derrick* (retaining counsel).
8. **Deploy `infra/` for real (`cdk bootstrap` + first `cdk deploy`) and onboard the
   first pilot client's `ClientPipelineConfig`.** *Owner: `cdk-engineer`*, blocked on
   items 1-3 above; requires Derrick's explicit go-ahead per this repo's standing rule
   that deploy/destroy/bootstrap are never run without confirming first.

**Tier 3 — can wait until there's a second client or the operating rhythm is actually
running:**
9. **Create `lab/pipeline-in-a-box/business/ops-log.md`** the first Friday the
   Mon/Wed/Fri operating rhythm actually runs. *Owner: `bungi` or `business-strategist`.*
10. **Build the Slack Command Center, Phase 0 (Slack app skeleton, `/pipeline status`
    only)** — doesn't require AWS or a signed client, can start any time Derrick wants
    the bridge. *Owner: Derrick* creates the Slack app/tokens; homelab-side bot code is
    `lab/pipeline-in-a-box/` work (not yet assigned to a specific agent in the design
    doc).
11. **Start SES domain/DNS verification early**, since DNS propagation + the
    production-access request both have real lead time — can run in parallel with
    other Tier 2/3 items once a sending domain is chosen. *Owner: `cdk-engineer`* for
    the CDK-side domain identity/DKIM/IAM construct, *Derrick* for DNS changes.
12. **A/B the insight-note model choice (Haiku 4.5 vs. Sonnet 5)** once there's real
    client data to test against — explicitly deferred in `orchestrator-design.md` §6.
    *Owner: whoever builds the orchestrator (`data-team-lead` to assign).*
13. **Update root `CLAUDE.md`'s "Lab & Agent Tooling" section to mention
    `lab/pipeline-in-a-box/`** (see gap above) — cosmetic/documentation-only, doesn't
    block any real work. *Owner: whoever next edits `CLAUDE.md` (Bungi cannot — write
    access is `docs/bungi/` only).*

## Open

- **5 new data/cloud-team skills were fast-drafted, not run through skill-creator's
  eval loop.** `.claude/skills/{aws-cloud-devops,sql-data-engineering,
  python-data-science,powerbi-dax-excel,data-business-strategy}/SKILL.md` were each
  written in one pass from a curated subset of `docs/Data Science Cheat Sheet/` plus
  general model knowledge, backing the new `cloud-engineer`, `data-engineer`,
  `data-scientist`, `bi-analyst`, `business-strategist` agents
  (`.claude/agents/*.md`). No test prompts have been run against them, so triggering
  accuracy (does the `description` field actually cause Claude Code to load the right
  skill for a real ambiguous prompt) and content quality (are the DAX/SQL/pandas
  patterns actually correct, not just plausible) are both unverified. Next step if/when
  the user wants to harden one: run it through `skill-creator`'s eval/iterate loop
  (`.claude/skills/skill-creator/`) against real test prompts.
  *First logged: 2026-08-16. Last verified: 2026-08-16.*

- **`website/` move is now committed but still structurally incomplete.** `index.html`,
  `derricks-own-flow.html`, `dj-flow.html`, `dataflow.html` live in `website/`, but
  `assets/` and `tools/` are still at repo root, and root `CLAUDE.md`'s file map still
  documents the old root-level layout. Internal links (`../assets/shared.js` etc.)
  haven't been checked against the new layout.
  *First logged: 2026-08-13. Last verified: 2026-08-13 (committed in `c77941e`
  "hella ai updates"; confirmed via `git log`/`git status` — working tree clean on
  these files).*

- **`cdk synth`/CDK CLI warns that Node v19.3.0 (installed on this machine) is
  end-of-life.** Works today; CDK CLI support for Node <20 is ending soon per the
  CLI's own notice (id 34635). Upgrade to Node 22 or 24 before it becomes a hard
  blocker for `infra/` work. See
  `.claude/skills/cdk-data-ai-stack/references/setup-checklist.md`.
  *First logged: 2026-08-13. Last verified: 2026-08-13 (`cdk synth` output in
  `infra/`).*

- **Aurora Serverless v2 vs. plain RDS instance cost tradeoff is unresolved.**
  `infra/infra/constructs/database.py` currently provisions Aurora Serverless v2
  Postgres, which has an always-on cost floor (~$40-50/mo) — not yet weighed against
  a cheaper `db.t4g.micro` instance for this low-traffic use case. Nothing deployed
  yet, so no money spent, but this should be decided before the first real
  `cdk deploy`. See
  `.claude/skills/cdk-data-ai-stack/references/decisions.md` and `sql-patterns.md`.
  *First logged: 2026-08-13. Last verified: 2026-08-13.*

- **Newsletter form (`website/index.html`) doesn't send email.** Submit button calls
  `handleNL()` (local JS, browser-only confirmation) — not wired to Formspree or any
  backend. Fix instructions already exist in `CLAUDE.md` under "Making Forms Work".
  *First logged: 2026-06-04 (prior session). Last verified: 2026-08-13 (grepped
  `website/index.html`, confirmed `onclick="handleNL()"` still in place).*

- **LinkedIn/GitHub footer links in `website/dataflow.html` are bare placeholder
  URLs** (`https://linkedin.com`, `https://github.com`, no actual handle).
  *First logged: 2026-06-04. Last verified: 2026-08-13
  (`website/dataflow.html:417-418`).*

## Open — not re-verified this session (carried from 2026-06-04 audit)

These were true as of 2026-06-04 per prior project notes. Not rechecked against
current code in this pass — verify before treating as current fact.

- DJ booking form and DataFlow contact form likely have the same "browser
  confirmation only, no real email" issue as the newsletter form.
- DataFlow project cards are placeholders (`#` links, placeholder case studies).
- `derricks-own-flow.html` progression log has only placeholder "coming soon" cards.
- DJ Instagram footer link is a placeholder, not a real profile.
- DJ Flow mixes have play buttons with no actual audio linked.

## Resolved

*(none yet)*
