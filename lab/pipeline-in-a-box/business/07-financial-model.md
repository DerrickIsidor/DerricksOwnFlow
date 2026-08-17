# Financial Model — Inputs, Unit Economics, Capacity Math

**Everything in this file is labeled by source.** Real AWS pricing and hours estimates
came from `cloud-engineer`, `data-engineer`, and `bi-analyst` (queried directly against
the actual templates in `../engineering/`, not guessed) on 2026-08-16. Anything beyond
that — capacity ceilings, milestone math, the $30K path — is business-strategist
arithmetic built on top of those inputs, labeled as such. Revisit every number here once
client #1 produces real hours/AWS-spend/churn data; nothing below is measured yet.

---

## 1. Inputs (cite before you trust)

### AWS cost — real pricing, `cloud-engineer`, 2026-08-16

| | Amount | Why |
|---|---|---|
| Fixed monthly floor | **≈ $44.60/mo** | Aurora Serverless v2 `min_capacity=0.5` ACU (`infra/infra/constructs/database.py`) never scales to zero — 0.5 × 730 hrs × $0.12/ACU-hr = $43.80, plus ~$0.80 Secrets Manager. Exists whether Pipeline-in-a-Box has 0 or 20 clients on it. |
| Marginal AWS cost per additional client | **≈ $0.25–0.50/mo** (call it $0.35) | ~1GB Aurora storage, a few ETL Lambda runs, a handful of insight-note API calls — all close to AWS's free tiers at this scale. Verify against a real client's actual export size once one exists; larger-than-assumed data volume is the one thing that would move this. |
| Allocated AWS cost per client, at different client counts | 1 client ≈ **$45/mo** · 5 clients ≈ **$9.25/mo** · 20 clients ≈ **$2.60/mo** | Fixed floor ÷ client count + marginal. This is *why* landing client #2 and #3 fast matters beyond revenue — it cuts effective infra cost/client ~5x by client #5. |
| Claude API cost for the weekly insight note | **~$0.02/month/client** (business-strategist rough calc, not a specialist estimate) | ~1,500 input + 500 output tokens/note on Haiku 4.5 ($1/$5 per 1M) × 4.33 weeks ≈ $0.017/mo. Rounding error next to everything else — confirms LLM cost is not a constraint at this scale. |
| What AWS cost is **not** the constraint on | Everything above 5 clients | Cost/client keeps falling as client count grows (shared Aurora cluster). The real ceiling is Derrick's hours, not infrastructure spend — see §3. |

Real pricing sources `cloud-engineer` cited: AWS RDS/Aurora, Lambda, S3, Secrets Manager,
API Gateway, CloudWatch, VPC/NAT, Route53 pricing pages (Aug 2026).

### Onboarding & maintenance hours — `data-engineer` (ETL) + `bi-analyst` (dashboard/note), 2026-08-16

| | Starter | Growth |
|---|---|---|
| **Onboarding, client #1–2** (building the reusable template as a byproduct) | ETL ~14 hrs + BI ~11 hrs ≈ **~25 hrs** | ETL ~14 hrs + BI ~20 hrs ≈ **~34 hrs** |
| **Onboarding, client #3+** (template exists) | ETL ~10 hrs + BI ~4 hrs ≈ **~14 hrs** (range 12–16) | ETL ~12 hrs + BI ~5 hrs ≈ **~17 hrs** (range 15–20) |
| **Weekly maintenance, steady state** | ETL ~1.0 hr + BI ~0.5 hr + note review ~0.3 hr ≈ **~1.8 hr/wk** (~7.8 hr/mo) | ETL ~1.25 hr + BI ~1.0 hr + note review ~0.35 hr ≈ **~2.6 hr/wk** (~11.3 hr/mo) |

Notes on where these numbers came from and where I extrapolated:
- ETL onboarding (~10 hrs median, range 6–16) and ETL maintenance (~1 hr/wk average) are
  `data-engineer`'s direct estimates against the actual `etl-template/` code.
- BI build hours (Starter 10–13 hrs client #1 → 3–5 hrs client #3+; Growth 18–22 hrs
  client #1 → 4–6 hrs client #3+) and maintenance (Starter ~0.5 hr/wk, Growth ~1 hr/wk)
  and the weekly-note human-review time (~0.25–0.4 hr/wk) are `bi-analyst`'s direct
  estimates against the actual star schema.
- **The Growth-tier ETL bump (10→12 hrs onboarding, 1.0→1.25 hr/wk maintenance) is my
  own extrapolation, not either specialist's number** — `data-engineer` didn't split by
  tier; I added a modest buffer because Growth explicitly means "more data sources,"
  which is more field-mapping surface. `bi-analyst` separately flagged that "more data
  sources" is the single biggest unscoped swing factor in the whole model — if a Growth
  client's second source is a genuinely new data domain (not just a second feed of the
  same shape), get a real `data-engineer` estimate before quoting hours, don't trust this
  extrapolation for that case.
- **AI Automation Retainer hours are not estimated by any specialist yet** — it doesn't
  exist as a build, so there's nothing to estimate against. Get real hours from
  `cloud-engineer`/`data-engineer` once it's about to be sold (month 3+ on client #1, per
  the roadmap), not before.

---

## 2. Per-client unit economics (steady state, post-onboarding, monthly)

Using marginal AWS cost ($0.35) since that's the number that actually changes per
client. "Effective $/hr" = (revenue − AWS marginal cost) ÷ monthly maintenance hours —
this is revenue attributable per hour of Derrick's ongoing work, not an assumption about
what his time is "worth"; compare it against his own day-job hourly-equivalent yourself.

| Tier / pricing | Monthly revenue | AWS cost | Maintenance hrs/mo | Effective $/hr |
|---|---|---|---|---|
| Starter, founding ($300/mo) | $300 | $0.35 | 7.8 | **≈ $38/hr** |
| Starter, raised (~$390/mo, client #3+) | $390 | $0.35 | 7.8 | **≈ $50/hr** |
| Growth, founding ($750/mo) | $750 | $0.35 | 11.3 | **≈ $66/hr** |
| Growth, raised (~$950/mo, client #3+) | $950 | $0.35 | 11.3 | **≈ $84/hr** |

**Reading this:** per-client margin is genuinely good on an hours basis — this is not a
business where the unit economics are the problem. The constraint is how many of these
hour-blocks fit into a part-time schedule (§3), not whether each one is profitable.

### Setup-fee economics (one-time, per onboarding)

| | Setup fee | Hours | $/hr |
|---|---|---|---|
| Starter, client #1–2 | $750 | ~25 | ~$30/hr (sunk template-build cost, pays off on every future client) |
| Starter, client #3+ | $750 | ~14 | ~$54/hr |
| Growth, client #1–2 | $2,000 | ~34 | ~$59/hr |
| Growth, client #3+ | $2,000 | ~17 | ~$118/hr |

Confirms `05-pricing-sanity-check.md`'s read: setup fees are already well-calibrated for
a templated build. Client #1–2's lower $/hr is the real cost of building the reusable
template — worth thinking of as an investment, not underpricing.

---

## 3. Solo capacity ceiling — the actual constraint

Budget: **10–15 hrs/week**, part-time around a full-time airline job (Derrick's own
stated framing). Reserve **~3 hrs/week minimum** for sales/outreach/admin — a pipeline
that isn't being fed goes stale even after client acquisition slows down — leaving
**~7–12 hrs/week** for client maintenance + onboarding sprints.

| Portfolio mix | Hrs/wk per client | Sustainable client ceiling (7–12 hrs/wk ÷ hrs/client) |
|---|---|---|
| All Starter | 1.8 | **~4–7 clients** |
| All Growth | 2.6 | **~3–5 clients** |
| Realistic mixed portfolio (horizontal GTM → expect a blend) | ~2.2 avg | **~4–6 clients** |

**Headline number: ~5–6 clients is the realistic sustainable ceiling for one person,
part-time, with a full-time day job — this is tighter than `data-engineer`'s
ETL-only estimate (5–7) because it also accounts for BI maintenance and weekly-note
review time, which that estimate didn't include.**

This ceiling, not AWS cost (§1) and not market size (see `06-business-plan.md` §2), is
the real limit on 2H26–2027 growth. Every roadmap milestone below is built around it.

---

## 4. MRR at the solo capacity ceiling (Pipeline-in-a-Box only, raised pricing)

| Mix (6 clients) | MRR |
|---|---|
| 6 Starter | 6 × $390 = **$2,340/mo** |
| 6 Growth | 6 × $950 = **$5,700/mo** |
| 3 Starter + 3 Growth (representative blend) | 3×$390 + 3×$950 = **$4,020/mo** |

**Realistic Pipeline-in-a-Box-only ceiling while solo + full day job: roughly
$2,300–$5,700/month, ~$4,000/month for a representative mixed portfolio.** This is a
real, meaningful supplemental income — but nowhere close to $30K/month, and that's the
honest headline finding of this model: **$30K/month is not reachable solo, on this
product alone, no matter how pricing or mix is optimized.** Something structural has to
change (headcount, or heavy retainer weighting, or both) — see §5.

I don't know Derrick's day-job take-home, so I'm not going to invent a "replaces X% of
salary" claim — compare the $2,300–$5,700/mo band above against his own number.

---

## 5. Path to $30K/month — illustrative, not a plan to execute yet

Two honest facts drive this section:
1. At raised Growth pricing alone, $30,000/mo ÷ $950 ≈ **32 clients** — roughly 5-6x the
   solo capacity ceiling in §3. Not reachable without more hours than one person has.
2. The AI Automation Retainer ($2K–10K/mo, 60–80% gross margin per the existing
   framing in `01-pitch-positioning.md`/README) is the only product in the current plan
   with revenue-per-relationship high enough to close that gap without needing 30+
   client relationships — but its own hours-per-client are **not yet estimated by any
   specialist** (see §1), so treat the numbers below as illustrative of the *shape* of
   what's needed, not a real forecast.

**Illustrative combination that reaches ~$30K/month:**

| | Count | Avg revenue | Subtotal |
|---|---|---|---|
| Pipeline-in-a-Box clients (mixed) | 10 | ~$600/mo blended | $6,000/mo |
| AI Automation Retainer clients | 4 | ~$6,000/mo (upper-middle of $2K–10K range) | $24,000/mo |
| **Total** | **14 relationships** | | **~$30,000/mo** |

14 total client relationships is more than double the ~5–6 solo ceiling from §3 — **this
combination requires at least one hire or subcontractor** handling Pipeline-in-a-Box
onboarding/maintenance, freeing Derrick to focus on retainer relationships and sales.
That's consistent with Derrick's own 3–5 year build-out framing, not a 1–2 year target —
treat this table as a sanity check on *what has to become true*, not a near-term plan.

---

## 6. Milestone bands (MRR only — map against your own numbers)

| MRR band | What it takes (Pipeline-only, solo) | What it takes (with retainer upsell, still solo-capacity-bound) |
|---|---|---|
| ~$2K–4K/mo | 4–6 Starter clients, raised pricing | 3–4 Pipeline clients + early retainer conversations, not yet closed |
| ~$4K–6K/mo | 4–6 Growth clients, raised pricing | Solo ceiling (§3) with 1 retainer client closed |
| ~$8K–14K/mo | Not reachable solo on Pipeline alone | Solo ceiling with 2 retainer clients closed (~$4–8K blended retainer revenue on top) |
| ~$30K/mo | Not reachable solo, any mix | Requires headcount — see §5, 3–5 year horizon |

Use this table, not a single target date, to sanity-check any "should I reduce day-job
hours" decision — the honest trigger is hitting the top of the solo ceiling band
*and* having 2+ retainer clients proven, not a calendar date. See
`06-business-plan.md` §3 for when that's realistically expected to happen.
