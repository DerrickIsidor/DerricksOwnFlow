# Business Plan — Pipeline-in-a-Box (and the AI Automation Retainer beyond it)

**What decision this drives:** whether/how far to push this venture beyond the current
6-week challenge, and — the thing Derrick actually asked — what has to be true before
reducing day-job hours or treating this as more than a side project. Short answer up
front: the unit economics are genuinely good (see `07-financial-model.md` §2), but a
solo part-time operator hits a hard ceiling around **5–6 clients / ~$2,300–$5,700 MRR**
well before anything resembling $30K/month — closing that gap requires either the AI
Automation Retainer upsell converting, or headcount, or both, on a 3–5 year horizon.
None of that changes what to do *now*: keep running the 6-week challenge, land the first
1–2 clients, and don't make a day-job decision off numbers this early.

All dollar/hour figures below are pulled from `07-financial-model.md`, which is itself
sourced from real AWS pricing (`cloud-engineer`) and hours estimates against the actual
built templates (`data-engineer`, `bi-analyst`) — not guessed. Read that file for the
math; this file is the plan built on top of it.

---

## 1. Market sizing

Pulled from `02-icp-prospecting.md`'s own sourcing, not re-researched:

| Segment | Directory-listed size (real, sourced) |
|---|---|
| Aviation (FBO/MRO/flight schools) | AOPA: 6,400+ airport businesses · NATA: ~3,700 member cos · ARSA: 400+ MRO shops |
| Auto repair | No single directory count given — described as "every town has a dozen," effectively the largest and most saturated of the four |
| Home health/elder care | NAHC national database: 30,000+ member agencies |
| Accounting/tax prep | NSA: ~30,000 independent practitioners/small firms |

**Rough total across all four, before any ICP filtering: well over 60,000–70,000
listed entities.** Applying the "too big for a spreadsheet, too small to have hired an
analyst" qualifying filter (no real data on what fraction actually fits — labeling this
a rough placeholder) — call it **15–30% of listed entities**, i.e. **roughly
10,000–20,000 realistic-fit prospects nationally.**

**The honest finding: market size is not, and will not become, the constraint at any
stage Derrick will realistically reach.** Even the 3–5 year, post-headcount scenario in
`07-financial-model.md` §5 (14 client relationships) uses well under 1% of the
addressable pool. The real constraint, at every phase of this plan, is Derrick's own
hours — see `07-financial-model.md` §3.

**What's actually reachable in year 1** is bounded by outreach capacity, not the market:
outreach templates call for batches of 4–5/day; sustained at that pace during active
prospecting weeks (not all year — client onboarding/maintenance competes for the same
hours once clients exist), a realistic estimate is **150–300 real outreach touches
across 2H26.** At a rough blended conversion (warm intros converting far better than
cold — no real data yet, treat as a placeholder to replace with actual reply/conversion
rates once outreach is underway), that's consistent with landing **low single digits of
clients by end of 2026** — which is exactly what the roadmap below targets, not a
stretch goal built backward from $30K.

---

## 2. Phased roadmap

### 2H26 (through Dec 2026) — setup and launch

- The existing 6-week challenge (already running) is the mechanism for this — this plan
  doesn't redo it, just sets what "success" looks like beyond week 6.
- **Target: 3–4 total clients signed by end of 2026**, founding-client pricing
  ($750/$300 Starter, $2,000/$750 Growth), mixed across whichever 2–3 segments produce
  real replies (per `02-icp-prospecting.md`'s own "don't pick a favorite yet" instruction).
- **Target MRR by Dec 2026: ~$1,500–2,500/mo.** Modest by design — the real deliverable
  of this phase is the **first published case study** from client #1, which is what
  makes every subsequent conversion easier (referenceable proof, not a cold pitch).
- No AI Automation Retainer sales in this window — the product's own framing gates it to
  month 3+ of an established client relationship, and no client will be 3 months in
  before ~Q4 2026 at the earliest.
- No day-job hours change. Onboarding hours for client #1–2 run high (~25–34 hrs each,
  see `07-financial-model.md` §1) because the reusable template is being built as a
  byproduct — budget for that explicitly rather than being surprised by it.

### 1H27 and the foundation/trust window (through ~2027)

"Foundation and trust" concretely means:
- **Grow toward the solo-sustainable ceiling of ~5–6 clients**, reached gradually across
  2027, not immediately — onboarding pace is realistically 1–2 new clients/month
  (`data-engineer`'s estimate) constrained as much by client-side scheduling latency as
  by Derrick's own hours.
- **Retention/churn: no real data yet — the honest assumption is early-stage services
  see meaningful churn (ballpark 10–20%/year) until there's a track record.** This is a
  placeholder, not a forecast — instrument it from day one (which client, when, why they
  left) so it stops being a guess by mid-2027. This is the "acquire and measure, don't
  wait to be asked" instinct from the data-business-strategy skill applied to the
  business itself, not just its dashboards.
- **Pricing raise to ~$390 Starter / ~$950 Growth kicks in starting client #3**, per the
  already-decided plan in `05-pricing-sanity-check.md` — restate here, don't re-decide.
- **AI Automation Retainer upsell: earliest realistic first sale is Q1 2027** (client #1,
  signed ~Sept/Oct 2026, hits the month-3+ trust gate around Dec 2026/Jan 2027). Target
  **1 retainer client sold by mid-2027**, not more — this product has no hours estimate
  yet (see `07-financial-model.md` §1) and shouldn't be oversold internally before it's
  been priced against real build effort.
- **Day-job hours: no change recommended in 1H27.** The trigger for even considering a
  reduction is hitting the *top* of the solo ceiling band (5–6 clients) **and** having
  2+ retainer clients proven — realistically not before late 2027/2028. Don't let a good
  month pull this decision forward; one client's payment cycle isn't a trend.

### 3–5 year build-out

What has to become true to scale past a single operator, in priority order:

1. **Headcount, not more AWS spend, is the actual scaling lever.** AWS cost per client
   *drops* with scale (~$45/client at 1 client → ~$2.60/client at 20, per
   `07-financial-model.md` §1) — infra was never going to be the bottleneck. The
   ~5–6-client ceiling is entirely a Derrick's-hours problem, so the fix is subcontracting
   (pay-per-onboarding contractors, cheapest first step) or a part-time hire once retainer
   margin (60–80% gross, per the existing framing) can fund it.
2. **"AI Ops in a Box" (phase 2 — selling the agent stack itself)** becomes worth building
   only once Pipeline-in-a-Box + the AI Automation Retainer are both proven repeatable —
   realistically year 2–3, not before. Don't let this pull focus from the two live
   products in 2026–2027.
3. **Geographic/vertical expansion** — the horizontal 2026 approach is *for* discovering
   which vertical(s) actually convert; year 2+ is when doubling down on the winner(s)
   makes sense, not before there's real conversion data across segments.
4. **What it costs to get there:** the illustrative $30K/month scenario in
   `07-financial-model.md` §5 needs ~14 total client relationships (10 Pipeline + 4
   retainer) — more than double the solo ceiling, meaning at least one subcontractor/hire
   handling Pipeline-in-a-Box delivery is a prerequisite, not a nice-to-have, for that
   number. Tooling/AWS costs at that scale stay low (well under $5/client/month); the
   real new cost line is payroll/contractor spend, sized against the retainer margin once
   the retainer product actually has hours attached to it.

---

## 3. Risks and honest assumptions

- **Day-job time conflict is the binding constraint, not a side risk.** The entire
  roadmap above is sized around it (§2, and `07-financial-model.md` §3). A bad
  scheduling month at the airline directly cuts into onboarding/maintenance capacity —
  there's no slack built in at 10–15 hrs/week.
- **Single-operator bus factor.** Every ETL fix, dashboard tweak, client email, and
  weekly note runs through Derrick alone. Worth writing down SOPs for each of these
  *before* the first subcontractor/hire (3–5 year phase), not scrambling to document them
  under pressure once help is finally needed.
- **Client concentration risk is real at low client counts.** At 3–6 total clients,
  losing 1–2 is a large percentage hit to MRR. The horizontal, multi-segment GTM already
  in place (`02-icp-prospecting.md`) is the right mitigation — don't over-index on
  aviation just because it's the warmest channel; the case study from any segment is what
  actually compounds.
- **Aviation-vertical cyclicality.** GA/FBO/MRO spending tracks fuel prices and broader
  travel-industry cycles. Real edge (insider access) but real correlated-downturn risk if
  the client base skews too heavily aviation — another reason to keep the portfolio mixed.
- **What happens if the AI Automation Retainer doesn't convert as modeled.** This is the
  single biggest swing factor in the entire plan — without it, the ceiling is
  Pipeline-in-a-Box's own solo MRR band (~$2,300–5,700/mo, `07-financial-model.md` §4),
  which is real, legitimate supplemental income but never reaches $30K/month at any
  client count a solo operator can service. That's not a failure scenario to hide from —
  it's the honest floor of "what this business is worth if only one product ever works,"
  and worth Derrick deciding now whether that outcome alone is worth the time investment,
  independent of whether the upsell ever lands.
- **Where I'm estimating vs. citing something real, restated:** AWS pricing and per-client
  infra cost (`07-financial-model.md` §1) are real, sourced pricing. ETL/BI hours are
  specialist estimates against actual built code, not measurements — no real client has
  gone through onboarding yet. Churn, outreach conversion rates, and every number in the
  $30K illustrative scenario (`07-financial-model.md` §5) are explicitly labeled
  placeholders pending real data. Replace every placeholder with a measured number the
  first time real data exists for it — that's the whole point of writing them down now.

---

## See also

- `07-financial-model.md` — the underlying math (unit economics, capacity ceiling, MRR
  milestone bands, $30K path) this plan is built on.
- `01-pitch-positioning.md` / `05-pricing-sanity-check.md` — product/pricing, unchanged
  by this plan.
- `02-icp-prospecting.md` / `03-outreach-templates.md` / `04-linkedin-post-1.md` —
  the active 6-week challenge this plan sits above, not a replacement for it.
