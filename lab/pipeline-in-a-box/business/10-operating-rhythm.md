# Operating Rhythm — Daily/Weekly Cadence, Beyond Week 6

**What this extends:** the Monday/Wednesday/Friday team-session pattern used inside the
6-week challenge, turned into an ongoing rhythm that doesn't stop at week 6 — tied
directly to the 2H26 targets already committed to in `06-business-plan.md` §2 (3–4
clients signed, ~$1,500–2,500 MRR by Dec 2026, no day-job hours change).

**Real constraint this is designed around, not invented around:** in-chat session
notifications aren't durable — max 7 days, gone once the session closes. The durable
notification path is a custom Slack bot + local orchestrator `cloud-engineer` is
designing separately. This document doesn't redesign that — it designs the cadence and
content assuming that pipe eventually exists, with a concrete near-term bridge (below)
for right now.

---

## 1. Daily — a lightweight pulse check (Derrick-run, ~5 minutes)

There's no scheduler running yet that could trigger this automatically — the only
scheduled piece designed so far is the weekly insight-note orchestrator
(`engineering/orchestrator-design.md`), and that's client-facing, not internal-ops. Until
that or the Slack bot exists, the daily pulse is a short personal checklist Derrick runs
himself, not an agent session:

1. **Anything land that needs a same-day response?** A prospect reply, a client question,
   a scheduling conflict at the airline that eats into this week's hours budget. If yes,
   handle it now — don't let it wait for Wednesday/Friday.
2. **What's today's single next action** toward this week's priority (set on Monday, see
   below)? One thing, not a list — the 10–15 hr/week budget from `07-financial-model.md`
   §3 doesn't survive a long daily to-do list.
3. **Log it if it's worth remembering** — a reply received, a client issue, a number that
   moved — in whatever the current durable log is (see §4). This is the "acquire and
   collect" instinct from the data-business-strategy skill applied to the business itself:
   if it isn't written down, Friday's rollup has nothing real to work from.

No agent needs to run for this — it's a personal ritual. It only becomes agent-assisted
once the Slack bot exists and can push a same-day flag to Derrick without him having to
remember to check.

---

## 2. Weekly — the three-session pattern, extended past week 6

### Monday — Planning / priority-setting

**Leads: `business-strategist`, with `data-team-lead` co-leading for specialist
coordination.**

- Review the prior week's real numbers against `06-business-plan.md`/
  `07-financial-model.md`: outreach sent, replies received, client status, hours spent
  vs. the 10–15/wk budget.
- Set **one clear priority for the week** — a specific decision this maps to (more
  outreach because the pipeline's thin, a client onboarding sprint because someone said
  yes, a churn conversation because a client's gone quiet) — not a running list.
- If the week's priority needs technical work, `data-team-lead` identifies which
  specialist(s) it touches and flags what's needed from them, so Wednesday's checkpoint
  has something concrete to check on.

### Wednesday — Build / delivery checkpoint

**Leads: `data-team-lead`.**

- Mid-week check on whatever technical work Monday flagged — an onboarding build in
  progress, a pipeline fix, a dashboard tweak. Short: is it on track for this week, is
  anything blocked, does the plan need to change.
- Only invoke the specific specialist(s) the week's priority actually touches — this
  isn't a standing all-hands with every agent every week. Most weeks this session is
  short or skipped entirely if there's no active technical work (e.g., a pure
  outreach-only week).
- If a client-facing deliverable is due this week (onboarding milestone, a weekly insight
  note once that's live), this is the checkpoint that catches a slipping timeline before
  Friday, not after.

### Friday — Close-out and reporting

**Leads: `bungi` for documentation, `business-strategist` for the numbers rollup.**

- `bungi` logs anything real that happened this week to `docs/bungi/CHANGELOG.md`
  (a shipped piece of work, a decision made) and updates `GAPS.md` if anything new
  surfaced or an old gap got closed.
- `business-strategist` rolls up the week's numbers into a short written summary (below)
  and checks them against the milestone bands in `07-financial-model.md` §6 — not to
  hit a number every week, but to catch drift early rather than discovering in November
  that the year's off track.
- **This is the actual "report to Derrick" moment of the week** — see §3 for what it
  contains and how it reaches him.

---

## 3. What gets reported to Derrick, and how often

| Cadence | Content | Trigger |
|---|---|---|
| **Same-day, ad hoc** | Anything that needs a decision now — a prospect reply, a client issue, a price question | Whenever it happens, not batched to Friday |
| **Weekly (Friday)** | Short summary: replies/leads this week · client status changes · hours spent vs. budget · any blocker · next week's single priority | Every Friday, once the rhythm is running |
| **Monthly (last Friday of the month)** | Rollup of the four weekly summaries against `06-business-plan.md` §2's 2H26 targets (3–4 clients, ~$1,500–2,500 MRR by Dec 2026) | Owned by `business-strategist` — the explicit "are we on pace" check |

Keep the weekly summary genuinely short — a handful of lines, not a report. The
milestone bands in `07-financial-model.md` exist precisely so a single good or bad week
doesn't get over-read; the monthly rollup is where trend actually matters.

---

## 4. The notification-durability problem — bridge, not a fix

In-chat pushes don't survive past 7 days and disappear when a session closes, so the
Friday summary can't live only in a chat message. **Near-term bridge, until the Slack
bot exists:** write the Friday summary into a real file in this repo — a running,
append-only log (e.g., a new `lab/pipeline-in-a-box/business/ops-log.md`, dated entries,
same append-only pattern `docs/bungi/CHANGELOG.md` already uses) rather than only ever
being said in a session. A file in the repo is durable across sessions in a way an
in-chat notification is not — this isn't a redesign of the Slack bot, it's the
zero-infrastructure version of "get the weekly report somewhere Derrick can always find
it," usable starting this week.

Once the Slack bot + local orchestrator `cloud-engineer` is building is live, the Friday
summary (and same-day ad hoc flags) should push there instead — the content and cadence
above don't change, only the delivery mechanism does. Don't wait for the bot to start the
rhythm; start it now with the file-based bridge.

---

## 5. When this cadence itself should change

- **Once client #1 signs:** add a standing line item to the Wednesday checkpoint —
  client health (is the pipeline running, has the client engaged with the weekly note) —
  this is new work the current cadence doesn't yet account for.
- **Once the weekly insight-note orchestrator goes live (week 3 build):** its own
  run-success/failure logging (§1 of `engineering/orchestrator-design.md`) becomes part
  of the Wednesday or Friday check — a failed run shouldn't go unnoticed until a client
  asks where their note is.
- **Don't add more sessions or more agents to this rhythm by default.** The whole point
  of the Monday/Wednesday/Friday shape is that it's already sized to the 10–15 hr/week
  budget — treat any addition to it as a cost against that budget, not a free improvement.
