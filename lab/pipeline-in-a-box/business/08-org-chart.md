# Org Chart — The Real Agent Roster as a Company

**What this is:** a corporate-role mapping of the subagents that actually exist in this
repo (`.claude/agents/*.md`), so "the team" has a legible structure instead of just being
a list of tool names. **This is not a legal org chart** — none of these agents are
employees, contractors, or legal persons. Derrick is the only human, the only legal
entity (once the LLC exists, see `11-legal-financial-foundation.md`), and the only one who
can sign anything, spend anything, or make a client commitment. Every role below is
"drafts/executes when directed" — never "decides and acts alone."

Roles and capabilities are pulled directly from each agent's real `description` and body
in `.claude/agents/*.md` — nothing here is aspirational or invented.

---

## The chart

```
                         ┌─────────────────────────────┐
                         │   DERRICK — CEO / Founder    │
                         │   (the only human)           │
                         └───────────────┬───────────────┘
                                          │
                 ┌────────────────────────┼────────────────────────┐
                 │                        │                        │
   ┌─────────────▼─────────────┐ ┌────────▼─────────┐  ┌───────────▼───────────┐
   │  data-team-lead            │ │ business-strategist│  │  bungi                │
   │  Head of Delivery / COO    │ │ Chief Strategy     │  │  Chief of Staff /     │
   │  equiv.                    │ │ Officer equiv.      │  │  Record Keeper        │
   └─────────────┬─────────────┘ └────────┬─────────┘  └───────────────────────┘
                 │                        │
     (dispatches, in parallel,    (queries the same 4 specialists
      to whichever specialists     directly for cost/feasibility
      a request needs)             input on a business case)
                 │                        │
        ┌────────┴────────┬───────────────┴────────┬─────────────┐
        │                 │                         │             │
┌───────▼──────┐  ┌───────▼──────┐        ┌─────────▼───────┐ ┌──▼─────────┐
│ cloud-engineer│  │ data-engineer│        │  data-scientist  │ │ bi-analyst │
│ Infrastructure│  │ Data Eng.    │        │  Analytics/ML    │ │ Client     │
│ /Platform Lead│  │ Lead         │        │  Lead            │ │ Reporting  │
└───────┬──────┘  └──────────────┘        └──────────────────┘ └────────────┘
        │
┌───────▼──────────┐
│ cdk-engineer      │
│ Infra Engineer    │
│ (infra/ code only)│
└────────────────────┘
```

**This is a matrix, not a strict hierarchy — say so plainly rather than pretend
otherwise.** `data-team-lead` and `business-strategist` both sit as peers directly under
Derrick, not one under the other. Both can call the four technical specialists directly
(`data-team-lead` when a multi-part build needs coordinating, `business-strategist` when
a business case needs a real cost/effort input) — the lines above show the two most common
paths, not the only legal ones. `bungi` reports to no one and is invoked by anyone
(Derrick, `data-team-lead`, or `cdk-engineer` after a change) — it sits off to the side
because it never manages or gets managed, it only documents.

---

## Role definitions — what each one actually does, and doesn't

| Role | Agent | Does | Does not |
|---|---|---|---|
| **CEO / Founder** | Derrick (human) | Signs contracts, opens/owns the bank account, sets prices and go/no-go on every client, owns all legal and financial liability, has final say on every decision below | Nothing is withheld from Derrick — he's the only one with unlimited authority |
| **Head of Delivery / COO equiv.** | `data-team-lead` | Routes a multi-specialty request to the right specialist(s), dispatches independent work in parallel, synthesizes their outputs into one coherent answer | Never writes code, queries, DAX, or infra itself — if it's about to implement something directly, that's a sign the work should have gone to a specialist instead |
| **Chief Strategy Officer equiv.** | `business-strategist` | Frames the ROI/business case (what decision changes, what it costs, what it pays off, the cheapest version that tests the hypothesis), queries the 4 technical specialists directly for real cost/effort numbers rather than guessing, hands approved work to `data-team-lead` to build | Never invents a cost or revenue number and presents it as solid; never executes a build itself |
| **Infrastructure/Platform Lead** | `cloud-engineer` | Decides AWS/cloud architecture, Docker/K8s, DevOps, security-zone design — the "how should this be hosted" call | Never runs a destructive or spend-incurring AWS command without Derrick's explicit confirmation; only hands off to `cdk-engineer`, no further chaining |
| **Infrastructure Engineer (infra/ implementation)** | `cdk-engineer` | Writes and maintains the actual `infra/` CDK (Python) code once `cloud-engineer` has decided the architecture | Never runs `cdk deploy`/`destroy`/`bootstrap` without Derrick confirming first, every time — those touch real, billed AWS resources |
| **Data Engineering Lead** | `data-engineer` | SQL, ETL/ELT pipeline design, warehousing/schema design, batch-vs-streaming calls | Never invents table/column names against a real schema; never runs a migration or destructive query against a real/shared database without confirmation |
| **Analytics/ML Lead** | `data-scientist` | Python/pandas EDA, data cleaning, feature engineering, model selection/evaluation | Never reports model performance without held-out evaluation data; doesn't build the ongoing report artifact itself — hands that to `bi-analyst` |
| **Client Reporting Lead** | `bi-analyst` | Power BI/DAX/Excel — the dashboard and report a client (non-technical stakeholder) actually reads | Never builds a measure needing time comparisons without a proper Date table; won't build on top of an unreliable data source without flagging it |
| **Chief of Staff / Record Keeper** | `bungi` | Documents what changed and why (`docs/bungi/CHANGELOG.md`), tracks the live gap backlog (`GAPS.md`), researches and logs open knowledge gaps (`RESEARCH.md`) | Never touches application code, never commits or pushes — reads the whole repo, writes only inside `docs/bungi/` |

---

## Where the human-only line is — no exceptions

Every one of the roles above can **draft, estimate, design, and prepare**. None of them
can do the following — this list is the actual accountability boundary of the company,
and it doesn't move as the agent roster grows:

- **Money.** No agent opens a bank account, moves money, sets final pricing on an
  invoice, or has any access to a real payment credential. `business-strategist` can model
  unit economics; Derrick decides what to actually charge and collect.
- **Legal signatures and filings.** No agent files Articles of Organization, signs a
  client contract, signs a BAA, or represents to a client (implicitly or explicitly) that
  an AI produced a binding commitment. Contract *drafts* come from this process
  (`11-legal-financial-foundation.md`); Derrick reviews with real counsel and signs.
- **Client relationships.** No agent replies to a prospect, negotiates a price, or says
  yes/no to taking on a client. Outreach *templates* exist (`03-outreach-templates.md`);
  sending them, and every reply after, is Derrick.
- **Spend-incurring or destructive infrastructure actions.** `cdk deploy`/`destroy`/
  `bootstrap` and any real AWS resource change require Derrick's explicit confirmation
  every time, per `cloud-engineer.md` and `cdk-engineer.md`'s own hard limits — not a
  one-time approval that carries forward.
- **Committing to the repo.** `bungi` explicitly never commits or pushes — every agent's
  output is left in the working tree for Derrick to review before it becomes permanent.

## See also

- `.claude/agents/*.md` — the source of truth for every role definition above; if an
  agent's actual instructions change, this chart needs to be re-verified against them,
  not assumed to still match.
- `06-business-plan.md` §3 — flags "single-operator bus factor" as a real risk; this
  chart is the current mitigation (a documented division of labor) but doesn't remove the
  risk — every one of these roles still ultimately runs through Derrick's own review.
