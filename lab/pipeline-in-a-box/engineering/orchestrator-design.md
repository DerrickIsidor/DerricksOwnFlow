# Weekly Insight Note Orchestrator — Design Doc

**Status:** Design only. Nothing here is built or deployed. Full implementation is
scheduled for **week 3** of the 6-week Pipeline-in-a-Box build (this is week 1, day 1).
Do not stand up the container, call `cdk deploy`, or provision any AWS resource off the
back of this doc without a separate, explicit go-ahead.

**Scope:** the piece of Pipeline-in-a-Box that runs on Derrick's homelab (TrueNAS Scale,
Docker-capable) on a weekly cron, hits the Claude API, and drafts a short written insight
note (revenue trend, job volume, retention signal, etc.) summarizing what happened in a
client's data that week. This is one component of the larger product described in
`../business/` (business/go-to-market side — not touched by this doc; referenced only).

---

## 1. End-to-end flow

```
TrueNAS Scale cron (weekly)
        │
        ▼
docker run/compose starts the "insight-note" container, then exits when done
        │
        ▼
1. Pull recent metrics for the client from Aurora Postgres
   (exact transport TBD — see §2, the open question)
        │
        ▼
2. Build a prompt: client context + this week's metrics summary
   (+ optionally last week's note, for continuity)
        │
        ▼
3. One Claude API call (Messages API, single request — this is a
   summarization task, not an agent loop; no tool use needed)
        │
        ▼
4. Format the model's output into the client-facing note
        │
        ▼
5. Deliver it somewhere Derrick/the client sees it (§5, options open)
        │
        ▼
6. Log the run (success/failure, token usage, note produced) so a
   failed week doesn't go unnoticed
```

Each run is one client, one week, one short LLM call — this stays a plain script, not an
agent. No harness, no multi-step tool loop is warranted here (see the "Should I Build an
Agent?" checklist in the `claude-api` skill — complexity, value, viability, and cost-of-error
don't clear the bar for anything beyond a single well-prompted call).

---

## 2. Data access — OPEN ARCHITECTURE QUESTION for week 3

**This is the piece that most needs a decision before implementation starts, and it is
explicitly not decided here.**

### The problem

The homelab container needs to read recent metrics from the same Aurora Postgres
database the pipeline loads into. In this repo's current CDK baseline (`infra/`):

- `infra/infra/constructs/network.py` — the VPC has **isolated subnets only**,
  `nat_gateways=0`. Nothing in the VPC has outbound internet access, and nothing outside
  the VPC can reach in.
- `infra/infra/constructs/database.py` — Aurora Serverless v2 is deployed into those
  `PRIVATE_ISOLATED` subnets, with credentials issued via Secrets Manager, not a public
  endpoint.

A container running on a TrueNAS box in Derrick's homelab is **outside AWS entirely**. As
the stack is configured today, there is no route from that box to the database — not a
missing credential, an actual missing network path. Something has to change before this
piece can work, and the three realistic options below trade off cost, security surface,
and how well they scale as Pipeline-in-a-Box picks up more than one client.

### Option A — Small authenticated read API (Lambda behind API Gateway or a Function URL)

A narrow, purpose-built Lambda — same VPC, same `PRIVATE_ISOLATED` subnets Aurora already
lives in — answers one question: "give me client X's metrics summary for date range Y."
It's invoked over HTTPS from the internet (API Gateway with an API key, or a Lambda
Function URL with IAM auth), the homelab container calls it with a stored credential.

- **Why it fits without a NAT gateway:** the Lambda's *inbound* invocation (from API
  Gateway or a Function URL) doesn't require the Lambda to have outbound internet access
  — it only needs to reach Aurora, which is intra-VPC. The "no NAT gateway" baseline
  decision in `.claude/skills/cdk-data-ai-stack/references/decisions.md` stays intact.
- **Blast radius:** small and explicit — the Lambda only ever runs the one query it was
  written to run, never arbitrary SQL. Even if the API key leaks, the exposure is
  "read this one summary shape," not "read the whole database."
- **Fits existing conventions:** this is exactly the shape `ExampleLambdaConstruct` /
  `lambda-patterns.md` already establish (Lambda in the VPC + Secrets Manager for DB
  creds + a security-group rule wired at the stack level) — `cdk-engineer` extends a
  known pattern rather than inventing one.
- **Scales naturally to more clients:** parameterize the endpoint by `client_id` and one
  endpoint serves every client Pipeline-in-a-Box signs, rather than provisioning a new
  path per client.
- **Cost:** API Gateway + Lambda at this call volume (a handful of requests per client
  per week) is cents/month — consistent with the repo's cost-conscious baseline. Verify
  actual current pricing before committing (don't take this figure as fact — see
  `cloud-engineer`'s standing rule to pull real AWS pricing rather than assume it).
- **Cons:** it's a genuine internet-facing endpoint, so it needs its own real auth
  (API key rotation, rate limiting) and a short security review before go-live — it's
  a new inbound surface on the account, however narrow.

### Option B — Scheduled export/pull of a small metrics summary to somewhere externally reachable

A scheduled (EventBridge-triggered) Lambda — same VPC, no NAT needed for the same reason
as Option A — runs weekly, queries Aurora, and writes a small aggregated JSON/CSV summary
to an S3 bucket. The homelab container then reads that object (scoped IAM credential or a
short-lived presigned URL) instead of calling a live query API.

- **Pros:** no live "answer arbitrary questions" surface at all — S3 `GetObject` with a
  narrowly scoped IAM principal is about as boring and well-understood as AWS access
  patterns get. Decouples the two systems in time; the export just needs to have run
  before the homelab job reads it.
- **Cons:** freshness is pinned to the export's own schedule, not on-demand; there's a
  sequencing dependency between "AWS-side export ran" and "homelab job reads the result"
  that needs handling (e.g. the homelab job checks the object's last-modified timestamp
  before proceeding, or triggers the export itself and polls). Slightly more moving parts
  than Option A for the same outcome.

### Option C — VPN / Site-to-Site tunnel between the homelab and the VPC

Stand up an AWS Client VPN, Site-to-Site VPN, or a lighter WireGuard/Tailscale tunnel
between the TrueNAS box and something inside the VPC, so the homelab container can reach
Aurora's private endpoint directly, as if it were just another resource inside AWS.

- **Pros:** once set up, the homelab side is a normal Postgres client against a private
  endpoint — no new AWS-side API to design or maintain.
- **Cons:** this is real, ongoing infrastructure — a VPN gateway with hourly billing
  reintroduces the always-on cost the "no NAT gateway" decision was specifically trying
  to avoid, and it's a heavier thing to operate for what is, today, one weekly cron job.
  It's also a bigger security surface than the other two options: if the homelab box is
  ever compromised, a live tunnel gives an attacker network-level reach toward the
  database subnet, not just access to one narrow, purpose-built endpoint. As a
  multi-tenant pattern (more clients later) it's also awkward — the tunnel is tied to
  Derrick's specific homelab, not something that scales per-client the way a
  parameterized API does.

### Recommendation (not final — revisit in week 3)

**Option A (small authenticated read Lambda)**, with **Option B as the fallback** if
Derrick would rather avoid any new inbound endpoint at all. Reasoning: Pipeline-in-a-Box
is meant to serve multiple clients per the business plan, and a parameterized read
endpoint scales with client count in a way a homelab-specific VPN tunnel doesn't; it also
reuses infra/'s existing Lambda-in-VPC pattern instead of introducing a new infrastructure
category (a VPN gateway) purely to serve one weekly job. Option C is the right call only
if the homelab ends up needing broader, ongoing access to the VPC for reasons beyond this
one pipeline — not the case today.

**This decision should be revisited in week 3, not locked in now** — with real numbers
(how many clients has Pipeline-in-a-Box actually signed by then, what does Aurora +
Lambda + API Gateway actually cost at that point) rather than the assumptions above. When
it's time to build it, this is `cdk-engineer` work (a new construct in
`infra/infra/constructs/`, wired in `infra_stack.py`) — flag any deploy as touching real,
billed AWS resources and confirm before running `cdk deploy`.

---

## 3. How it triggers — TrueNAS Scale, Docker, cron

- **Scheduler:** TrueNAS Scale's own cron (System Settings → Advanced → Cron Jobs)
  running `docker compose run --rm insight-note` (or a plain `docker run`) on a weekly
  schedule (e.g. Monday morning). Use TrueNAS's scheduler rather than embedding a cron
  daemon inside the container — one scheduling system, not two.
- Alternative considered: TrueNAS Scale's k3s-backed "Custom App" system. More moving
  parts (a Kubernetes app deployment) for a one-shot weekly batch job that doesn't need
  to stay running — plain `docker compose` + host cron is simpler and is the recommended
  starting point. Revisit only if/when secrets management (§4) or multi-client fan-out
  makes the k3s path worth the extra complexity.
- **Container image contents:**
  - Base: `python:3.12-slim` (smallest reasonable base — see the Docker guidance in the
    `aws-cloud-devops` skill).
  - Dependency layer (installed before code, so code-only changes don't force a
    reinstall): the `anthropic` SDK, plus whatever client the §2 data-access decision
    needs (`pg8000` for a direct Postgres connection if a future option needs one — reuses
    the same driver `infra/` already chose for Lambda, see
    `.claude/skills/cdk-data-ai-stack/references/decisions.md` — or `httpx`/`requests`
    for the Option A/B HTTP path).
  - Code layer: a single script (e.g. `generate_insight_note.py`) doing steps 1–6 from
    §1. No secrets baked into the image at build time — see §4.
- **Multi-client fan-out:** out of scope for week 3's first pass with one pilot client,
  but worth flagging now — either the cron job loops over a small client config list and
  runs the container once per client, or it spawns one container invocation per client.
  Decide once there's a second paying client; don't build for it speculatively yet.

---

## 4. Secrets handling

**Hard rule, restated from this repo's conventions: never bake the Claude API key, DB
credentials, or any API key into the Docker image, and never commit them to the repo.**
If one ever lands in git history, rotating the credential is the fix — removing it from a
later commit is not enough.

- **Recommended starting point:** a `.env` file that lives on the TrueNAS box's own
  filesystem, **outside this git repo**, with restrictive permissions (readable only by
  whatever user/context runs the container). `docker-compose`'s `env_file:` directive
  loads it at run time — nothing is baked into the image, and the secret never touches
  version control.
- **Claude API key:** standard `ANTHROPIC_API_KEY` env var — this is what the `Anthropic()`
  client picks up with a bare, zero-arg constructor.
- **DB/API credential:** shape depends entirely on which §2 option gets chosen — a
  connection string + password for Option C, an API key for Option A's read endpoint, or
  a narrowly-scoped AWS access key (single S3 `GetObject` path, nothing broader) for
  Option B. Whichever it is, scope it to the absolute minimum the container needs —
  never the account's admin/root credentials on a homelab box.
- **Revisit if it grows:** TrueNAS Scale's k3s "Custom App" path supports real
  Kubernetes Secrets (secret-at-rest, not just a file) — worth adopting later if managing
  credentials for several clients on one box gets unwieldy with plain `.env` files. Not
  needed for the first client.

---

## 5. Delivery — how the note reaches Derrick/the client

No decision needed today; options, with the tradeoff that matters most flagged below.

| Option | What it looks like | Notes |
|---|---|---|
| **Email** | Transactional email API (SES, Postmark, Resend) or plain SMTP from the container | Simplest to build. `Formspree` (used elsewhere in this repo for the public site's forms) isn't the right tool here — it's a form-to-inbox bridge for the marketing site, not a programmatic sender. |
| **Saved doc** | Google Docs API, Notion API, or a Markdown file synced to a shared drive | Gives a persistent, editable record — a natural place for Derrick to hand-edit before a client ever sees it. |
| **Posted somewhere** | Slack or Discord webhook, or a notification inside whatever dashboard/BI delivery the pipeline already builds | Good for Derrick's own quick glance; weaker as the actual client-facing artifact on its own. |

**The one thing worth deciding early, regardless of which delivery mechanism wins:** this
is a paid-client deliverable, and an unreviewed AI draft going straight to a client
without a human glance is a quality/trust risk, not just a technical one. The likely right
shape is a **review gate** — the note lands with Derrick first (email or doc), he
skims/edits, then a separate step (manual or eventually automated) sends the approved
version on to the client. Whether that gate is manual or built into the pipeline is a
week 3 call, and probably worth a beat with `business-strategist` on how much
human-in-the-loop review the product's positioning actually needs — flagging it here
rather than routing it there myself.

---

## 6. Model choice — a tunable knob, not a decision here

This is a short, mostly-factual summary generated from **structured, pre-aggregated
metrics** (revenue trend, job volume, retention signal) — not open-ended reasoning over
messy raw data. That's a workload where a smaller, cheaper model may perform just as well
as a top-tier one, and at productized-service scale (the same call repeated across every
signed client, every week) the per-call cost difference compounds. Current Claude API
list pricing (per the `claude-api` skill, cached 2026-06-24 — verify before relying on it
for a real cost model):

| Model | Input $/1M | Output $/1M |
|---|---|---|
| Claude Haiku 4.5 | $1.00 | $5.00 |
| Claude Sonnet 5 | $3.00 (intro $2.00 through 2026-08-31) | $15.00 (intro $10.00) |
| Claude Opus 5 | $5.00 | $25.00 |

**Recommendation for week 3:** actually A/B the note quality between Haiku 4.5 and Sonnet
5 on a couple of weeks of real client data before picking one — don't default to the most
capable model without checking whether this specific, narrow task needs it. This is a
prompt-engineering / cost decision, not an infra one, and doesn't block the architecture
work above.

---

## 7. What's explicitly not decided or built yet

- **§2 data access** — the real blocker; needs a decision before any of the rest can
  actually run end to end.
- Whether the review gate in §5 is manual or automated.
- Which delivery mechanism in §5 to use.
- Which Claude model (§6) to call.
- Multi-client fan-out shape (§3), once there's a second client.

**Hand-off:** once §2 is decided, the AWS-side piece (new Lambda/API Gateway/S3 export,
whatever gets chosen) is `cdk-engineer` work extending `infra/` per its existing
conventions — not something to build directly from this doc. The homelab-side container,
script, and docker-compose/cron setup are not `infra/` work at all; they'd land under
`lab/pipeline-in-a-box/` per this repo's `lab/README.md` convention when week 3 actually
starts. Nothing in this document should be built, deployed, or `cdk deploy`'d without a
separate, explicit go-ahead — this is a design doc only.
