---
name: data-business-strategy
description: Use whenever a data/tech decision needs a business or financial lens — deciding whether a tool or project is worth building, framing an ROI or cost-benefit case, prioritizing what to work on next, structuring how a (possibly one-person) data team should operate, or translating technical work into terms a non-technical stakeholder or investor would read. Trigger on "is this worth it," "should I build this," "how do I prioritize," "make the business case," "how should I structure my team," or any request to connect data/engineering work to revenue, cost, or growth goals — even without the word "business" in the prompt.
---

# Data & Business Strategy

The "should we build this, and how do we know it worked" layer on top of technical work.
Grounded in DJ Patil's *Building Data Science Teams* (O'Reilly) — written for orgs at
LinkedIn/Facebook scale, but the underlying judgment calls apply just as much to a small
team or a single founder wearing every hat.

## Being data-driven — the actual definition, not the buzzword

> A data-driven organization acquires, processes, and leverages data in a timely fashion
> to create efficiencies, iterate on and develop new products, and navigate the
> competitive landscape.

The operational version of that, at any scale:
1. **Instrument and collect** — if you don't capture the data, there's nothing to decide
   from later. Decide what to track *before* the thing launches, not after someone asks
   "how did that do."
2. **Measure proactively and on a timely cadence** — a metric checked once a quarter
   can't inform a decision made this week.
3. **Get more eyes on the data** — a dashboard only you look at catches fewer problems
   than one other people glance at regularly.
4. **Stay curious about *why* a number moved**, not just that it moved.

Avoid the "silver bullet" trap: there's rarely one metric that explains everything. The
best operators find a handful of real levers, act on them, then look for the next ones —
not a single number to obsess over.

## Framing a business case for a tool/project

Before building anything, answer these in one paragraph each — if you can't, the case
isn't ready:
- **What decision or action does this actually change?** "It would be cool to know X" is
  not a business case; "knowing X changes whether we do Y" is.
- **What does it cost** — build time, ongoing maintenance, infrastructure spend (pull
  real AWS numbers via `aws-cloud-devops`/current docs, never guess a dollar figure)?
- **What's the payoff, and on what timeline?** Revenue gained, cost avoided, or time
  saved — quantify it even roughly. A rough number beats "it'll probably help."
- **What's the cheapest version that tests the hypothesis?** Build that first, not the
  full system — this is the same instinct behind an MVP, applied to internal tooling too.

For a solo operator or small team specifically: every hour spent building a tool is an
hour not spent on the thing that tool is supposed to support. Weigh "build vs. buy vs.
skip" honestly — a $20/month SaaS tool is often cheaper than the hours it takes to build
and maintain the equivalent yourself, *unless* the tool itself is the product.

## Roles on a data team (and what they collapse into at small scale)

Patil breaks data work into six functional areas. At LinkedIn each was a team; for a
smaller operation, treat this as a checklist of *jobs that need doing*, even if one person
does several:
- **Decision sciences / BI** — defining and reporting the metrics that actually drive
  decisions (this repo's `powerbi-dax-excel` skill covers the tooling for this).
- **Product/marketing analytics** — did a change move the numbers it was supposed to.
- **Fraud/risk/security** — only relevant once there's real money or user data at stake.
- **Data services & operations** — the database/warehouse staying up and correct
  (`sql-data-engineering`, `aws-cloud-devops`).
- **Data engineering & infrastructure** — building the pipelines everything else depends
  on (same two skills).
- **Organizational alignment** — deciding who does what, and making sure the pieces above
  actually talk to each other instead of duplicating work.

The useful move at small scale isn't picking one of these to specialize in — it's
noticing which one is currently the bottleneck and doing that one next.

## What makes a good data hire (or a good habit to build in yourself)

Four traits, in Patil's framing — worth using as a checklist whether hiring or
self-assessing:
- **Technical expertise** — real depth somewhere, not shallow breadth everywhere.
- **Curiosity** — the drive to dig past the surface number to the actual mechanism.
- **Storytelling** — data that no one else can understand or act on has no value yet.
- **Cleverness** — looking at a stuck problem from a different angle instead of forcing
  the first approach harder.

The "startup test" for a hire or a collaboration: would you be willing to be locked in a
small room with this person for long stretches (implies enjoying their company and
trusting them), could they meaningfully contribute within ~90 days, and in 4-6 years
would you expect them to be doing something impressive — whether at your company or not.

## Prioritization — "everything can't be urgent"

The single most common failure mode of a data-driven team (of any size) is drowning in
inbound requests tagged "ASAP" with no time left for the big-picture work. Force an
explicit priority call on anything new: does this unblock a decision this week, or is it
"nice to know"? Protect time for the second category (batch/strategic analysis) or it
never happens — see `sql-data-engineering`'s batch-vs-streaming framing for the technical
version of the same tradeoff (fast-and-narrow vs. slow-and-complete).

## Where this hands off

- Whether a proposed pipeline/tool is technically sound and what it'd cost to run →
  **sql-data-engineering** / **aws-cloud-devops**.
- Whether a model idea is worth pursuing → **python-data-science**.
- Turning the resulting numbers into something a stakeholder reads →
  **powerbi-dax-excel** / **dataviz**.
