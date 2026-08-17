# Slack Command Center — Design Doc

**Status:** Design only. Nothing here is built or deployed. This extends
`orchestrator-design.md` (same folder) — read that first; it is not repeated here except
where this doc changes or depends on one of its open items. AWS credentials are not
connected in this environment as of this writing (Derrick is setting them up separately);
treat everything below as foundation-laying, not a same-day build. Do not create a Slack
app, register a bot, provision SES, or run any `cdk deploy` off the back of this doc
without a separate, explicit go-ahead.

**Scope:** the remote command-and-notification layer that lets Derrick run Pipeline-in-
a-Box operations — kick off a subagent task, get daily/weekly digests, two-way message
his own agent fleet — from Slack on his phone, from anywhere, plus a Python-driven email
channel for client-facing notes and his own ops digest. This is the "how Derrick talks to
the system remotely" piece; it sits alongside, not inside, the weekly insight-note
pipeline `orchestrator-design.md` covers.

---

## 0. Why not the official Claude Tag (Claude in Slack)

Already researched and ruled out, noted here so the reasoning isn't lost: Claude Tag runs
in an Anthropic-hosted sandbox scoped for team-wide Slack work against *connected SaaS
tools* (GitHub, Datadog, etc.). It cannot reach a local repo on Derrick's TrueNAS box and
cannot trigger this repo's local named subagents (`bungi`, `cdk-engineer`, `data-team-lead`,
...) — there's no path from an Anthropic-hosted sandbox to a homelab machine. This needs a
small custom bridge instead: a bot Derrick owns, running where the repo and the `claude`
CLI already live.

---

## 1. End-to-end flow

```
Derrick, Slack mobile
        │  types /pipeline <command> in a DM or a private channel
        ▼
Slack Platform
        │  delivers the command to the bot (transport choice — §2)
        ▼
Slack Command Center bot (Python, running on the TrueNAS box,
alongside the orchestrator container — same host, separate process/container)
        │
        ├─ 1. Verify the request is authentically from Slack (§3)
        ├─ 2. Verify the sender is Derrick's Slack user ID, no one else (§3)
        ├─ 3. Look up the command against a hardcoded allowlist (§4) —
        │     reject anything not on it, no free-form shell text
        ├─ 4. Post an immediate Slack ack ("Started: <command>") so the
        │     interaction never times out waiting on a long job
        ├─ 5. Launch the mapped `claude` CLI invocation as a background
        │     subprocess (list-args, never shell=True) — §5
        └─ 6. Log the invocation (who, what, when) to an audit log — §6
        ▼
The subprocess runs the actual named subagent (bungi, cdk-engineer,
data-team-lead, ...) against the real repo, same as an interactive session
        │  (can take minutes — this is fire-and-forget from Slack's view)
        ▼
When the subprocess exits, the bot posts the result back into the
*same* Slack channel/thread it was invoked from, via a stored bot token
(chat.postMessage) — not Slack's response_url, which expires (§5)
```

---

## 2. Transport — how Slack talks to the homelab bot

### Option A — Socket Mode (recommended)

The bot opens an outbound WebSocket connection *from* the TrueNAS box *to* Slack and
receives commands/events over it. No public HTTPS endpoint, no inbound port on Derrick's
home network at all.

- **Why it fits this homelab, specifically:** the orchestrator design's whole network
  posture (`infra/`'s "no NAT gateway," nothing inbound to the VPC) is "don't open new
  inbound surface unless something genuinely needs it." A bot with a public HTTP endpoint
  on Derrick's home connection would be exactly that — a new internet-facing listener on
  a residential network, needing port-forwarding/dynamic DNS/TLS termination to work at
  all. Socket Mode sidesteps the question entirely: the connection is always outbound.
- **Auth model differs, not disappears:** without a public endpoint there's no HTTP
  request to sign (no `X-Slack-Signature` header to verify), because Slack authenticates
  *the connection itself* via the app-level token (`xapp-...`) used to open the socket,
  and the bot token (`xoxb-...`) used to call back into the Slack Web API. This replaces
  §3's "verify Slack's request signature" step with "the socket itself only exists because
  these two tokens are valid" — the Derrick-only allowlist check on every incoming
  command's `user_id` field still happens regardless of transport and is the layer that
  actually matters most (see §3).
- **Cons:** requires the bot process to stay running continuously (a long-lived
  connection, not a stateless request handler) — needs a supervisor (systemd unit or a
  `restart: unless-stopped` Docker container) so it reconnects after a homelab reboot or
  network blip. Not usable if this app is ever meant to be installed into other Slack
  workspaces (Slack restricts Socket Mode apps from the App Directory) — irrelevant here,
  this is a single-workspace, Derrick-only app.

### Option B — HTTP Events API + request signing

The bot exposes a public HTTPS endpoint; Slack POSTs commands/events to it. Every request
must be verified using Slack's signing secret: recompute an HMAC-SHA256 over the request
timestamp + raw body, compare to the `X-Slack-Signature` header, and reject if it doesn't
match or if the timestamp is more than ~5 minutes old (replay protection).

- **Pros:** stateless, no persistent connection to babysit; this is the shape most Slack
  bot tutorials assume, and the shape the task brief's phrasing ("Slack's own request
  signing") describes directly.
- **Cons:** needs a real public endpoint reachable from the internet — a reverse proxy
  (nginx/Caddy) or Cloudflare Tunnel, a TLS cert, and DNS pointed at the homelab, i.e. new
  attack surface on Derrick's home network that Option A avoids entirely. Also needs its
  own uptime story (Slack retries failed deliveries but expects a fast 200 OK).

### Recommendation

**Option A (Socket Mode)** as the primary build. It best matches this repo's existing
security instinct (avoid new inbound surface unless something needs it — the same logic
`orchestrator-design.md` §2 used to prefer a narrow Lambda API over a VPN tunnel, just
applied to the homelab's own edge instead of AWS's). Keep Option B documented as the
fallback if Socket Mode proves limiting in practice (e.g. Slack Socket Mode rate limits,
or a future need to expose this to more than Derrick). Either way, §3's Derrick-only
allowlist check is the auth layer that actually protects the system — it applies
identically under both options and should not be treated as optional under Option A just
because there's no signature to verify.

---

## 3. Auth model — layered, deny-by-default

This is the part that matters most, per the brief, because a leaked token here means
someone can trigger real actions on real infrastructure from anywhere. No single layer is
trusted alone:

1. **Slack workspace boundary.** The bot lives in a single-member (Derrick-only) Slack
   workspace or a private channel he controls — not a shared/public workspace. This is
   the coarsest layer and the easiest to get wrong by accident (e.g. inviting a
   collaborator later without revisiting this doc).
2. **Transport-level authenticity** (§2) — Socket Mode's app/bot tokens, or Option B's
   signing-secret verification. Confirms the message genuinely came from Slack's servers,
   not a spoofed source.
3. **Derrick-only allowlist — the layer that actually matters.** Every incoming
   command/event carries a Slack **user ID** (`U0XXXXXXX`, stable, not the display name
   or `@handle` which can change). The bot checks that ID against a single hardcoded
   value stored in the `.env` file (§7) before doing anything else. If it doesn't match,
   the bot posts nothing (no error text confirming the bot exists/works, which itself
   would leak information) and logs the rejected attempt. This check runs even for
   commands that look read-only — no exceptions, no "just this once."
4. **Hardcoded command/subagent allowlist, not free-form shell text.** Slack command text
   is never interpolated into a shell string. A Python dict maps a fixed set of command
   names (e.g. `status`, `audit`, `digest`, `run-insight-note`) to a fixed subagent name
   and a fixed CLI argument *template*; the only thing user-supplied text can fill in is a
   narrowly validated parameter (e.g. a `client_id`), checked against the same kind of
   pattern `infra/`'s `ClientPipelineConfig.__post_init__` already uses to validate
   `client_id`/`target_schema`/`target_table` (safe-identifier characters only, checked
   against a known-clients list) — reusing a convention this repo already has, not
   inventing a second one. `subprocess.run([...])` with a list of arguments, never
   `shell=True` and never an f-string building a shell command, so even Derrick's own
   typos in a parameter can't become shell injection.
5. **No deploy/destroy reachable from Slack, at least initially.** `cdk deploy`,
   `cdk destroy`, and `cdk bootstrap` are excluded from the command allowlist entirely in
   phase 1, even though Derrick tapping a button on his phone is, in a real sense, "him
   explicitly confirming." The existing hard limit (`cloud-engineer`/`cdk-engineer` never
   run these without the user confirming, *every time*, in an interactive session) was
   written assuming a live back-and-forth, not a fire-and-forget async job kicked off from
   a phone with no chance to review a `cdk diff` first. Recommendation: keep real AWS
   spend/destroy actions off the Slack surface until there's a track record with the
   read-only/build-only commands, and if they're ever added, require a second-factor
   confirmation step in the Slack flow itself (e.g. the bot echoes back the exact
   `cdk diff` output and requires a literal `CONFIRM` reply in the same thread before
   proceeding) rather than a single tap doing it.
6. **Least-privilege execution.** The `claude` CLI subprocess runs as a dedicated
   low-privileged OS user (or inside a container scoped to just this repo's working
   directory), not root, and not the same user/session Derrick uses interactively on the
   box.
7. **Kill switch.** A single flag the bot checks before processing anything — an
   environment variable or a sentinel file outside the repo — that Derrick can flip
   (even via a Slack command of its own, `pause`/`resume`, itself covered by the same
   allowlist+identity checks) to stop all command execution immediately if a token ever
   leaks, without needing to SSH in and kill the process.

---

## 4. Command allowlist — starting set

Kept intentionally small at first; each entry maps to one existing named subagent this
repo already has, run with a fixed prompt template:

| Slack command | Maps to | Notes |
|---|---|---|
| `/pipeline status` | no subagent — bot reads its own audit log (§6) | Read-only, always safe, good first command to build and test the bridge with before wiring anything real. |
| `/pipeline audit` | `bungi` | Read-only by Bungi's own design (never edits application code). Good second command — proves a *real* subagent invocation end to end with the lowest possible risk. |
| `/pipeline digest` | reads recent logs across the fleet, formats a summary | Not itself an agent call — see §8 (daily/weekly digest). |
| `/pipeline run insight-note client=<id>` | `data-team-lead` or the insight-note script directly | Depends on `orchestrator-design.md` §2's data-access decision being resolved first — don't wire this before that pipeline works standalone via cron (see §9). |
| `/pipeline infra-check` | `cdk-engineer`, restricted to `cdk synth`/`cdk diff` | Read-only against AWS (once credentials exist); explicitly excludes `deploy`/`destroy`/`bootstrap` per §3.5. |
| `/pipeline pause` / `/pipeline resume` | kill switch (§3.7) | Handled by the bot directly, not a subagent call. |

Each command's CLI invocation follows the headless pattern Claude Code's own docs
describe for scripted use: `claude -p "<fixed prompt naming the subagent + validated
params>" --permission-mode <mode> --output-format json`, run with `cwd` pinned to the
repo root. Two things worth flagging for whoever implements this (verify against the
actual CLI on the TrueNAS box before relying on them — don't take flag names as gospel
from a design doc):

- **Permission mode per command, not one blanket setting.** Headless mode has no one to
  answer an interactive permission prompt, so something has to be chosen per command:
  `dontAsk`/`bypassPermissions`-style modes are appropriate for read-only commands like
  `audit`/`infra-check`, but a command capable of writing files or running shell commands
  needs either a narrower `--allowedTools` scope or to stay off the Slack surface (same
  reasoning as §3.5's deploy exclusion, applied more generally — the amount of unattended
  authority a Slack tap grants should scale with how reversible the action is).
- **`--output-format json`** gives the bot a machine-parseable result to reformat for
  Slack, instead of scraping free-text terminal output.

---

## 5. Async execution and result delivery

Slack slash-command interactions expect a fast (~3 second) acknowledgment, and the
`response_url` they hand back for a delayed reply **expires after ~30 minutes** — not
good enough for a subagent run that can take longer. Design:

1. Bot receives the command, does §3's checks, and immediately replies with a short ack
   in the same thread ("Started: audit — I'll post here when it's done").
2. Bot launches the mapped `claude -p ...` invocation as a background subprocess (not
   blocking the Slack event handler) and remembers which Slack **channel ID + thread
   timestamp** the request came from.
3. When the subprocess exits, the bot calls Slack's `chat.postMessage` Web API (using the
   long-lived bot token, not `response_url`) targeting that same channel/thread — this
   works no matter how long the job ran, and threads the result under the original
   command for a clean two-way conversation feel on mobile.
4. Both success and failure post back — a silently-failed job with no Slack message is
   worse than one that reports its own error, especially for something Derrick is
   checking from his phone away from a terminal.

---

## 6. Audit logging

Every command — accepted or rejected — gets appended to a log (plain file on the TrueNAS
box is enough at this scale, same "boring and well-understood" instinct
`orchestrator-design.md` applies elsewhere): timestamp, Slack user ID, command + params,
accepted/rejected, and (once the subprocess finishes) exit status and a short result
summary. This is what `/pipeline status` reads from, and what `/pipeline digest` (§8)
rolls up into the periodic summary — one audit trail feeding both interactive lookups and
scheduled digests, not two separate logging paths.

---

## 7. Secrets handling — same pattern as the orchestrator, extended

Follows `orchestrator-design.md` §4 exactly: a `.env` file on the TrueNAS box's own
filesystem, **outside this git repo**, restrictive file permissions, loaded at process
start (`docker-compose`'s `env_file:` or the process's own env loading) — nothing baked
into an image, nothing committed. This design adds these keys to that same file:

- `SLACK_BOT_TOKEN` (`xoxb-...`) — posts messages back to Slack.
- `SLACK_APP_TOKEN` (`xapp-...`) — opens the Socket Mode connection (Option A).
- `SLACK_SIGNING_SECRET` — only needed if Option B (HTTP) is used instead/later.
- `DERRICK_SLACK_USER_ID` — the §3 allowlist value. Not secret in the sense of granting
  access on its own, but still kept out of the repo so the allowlist logic isn't
  hardcoding a real identifier into version control.
- `AWS_SES_*` credentials (§8) — a narrowly scoped IAM principal, `ses:SendEmail`/
  `ses:SendRawEmail` only, nothing broader — same "never the account's admin/root
  credentials on a homelab box" rule the orchestrator doc states for DB/API credentials.

If any of these ever land in git history, rotating the credential is the fix, not
removing it from a later commit — restated here because it's the single most important
line in this whole doc to not skim past.

---

## 8. Email delivery via Python (AWS SES)

For the weekly client insight notes and Derrick's own daily/weekly ops digest, as a
channel that exists independent of Slack (email survives a Slack outage, and clients
shouldn't need a Slack account to receive their note).

- **Mechanism:** `boto3`'s SES client (`send_email` or `send_raw_email` for anything with
  attachments/HTML formatting), called from a small Python helper — same style/level as
  the rest of the homelab tooling, no separate email service needed for this volume.
- **Real setup requirements, not to be glossed over:**
  - **Domain verification is required before sending as `@derricksownflow.com`** (or a
    subdomain like `mail.derricksownflow.com`, often cleaner so bulk-ish mail is isolated
    from the domain's other DNS records) — SES needs specific DNS records added (domain
    verification TXT record, plus DKIM CNAME records) before it will send from that
    identity.
  - **New SES accounts start in sandbox mode**: capped at roughly 200 messages/24h, ~1
    message/second, and — this is the part that actually blocks testing — **can only send
    to addresses that are themselves verified in SES**, not arbitrary recipients. Fine for
    Derrick testing to his own inbox; not fine for sending a client their first note.
  - **Moving to production access requires a support-ticket-style request** ("SES Sending
    Limits" request) through the AWS console, and AWS now expects the domain's SPF/DKIM/
    DMARC records to already be in place before that request is even made. Approvals are
    typically fast (commonly cited around 24 hours) but this is still a real dependency
    with lead time, not something to assume happens same-day as the domain gets pointed
    at AWS. Verify current requirements against AWS's own SES docs when this is actually
    being set up — sandbox/production limits and the request process do change over time,
    and this section should not be treated as a permanent source of truth.
  - **Region matters**: SES is only available in a subset of AWS regions — confirm the
    region chosen for `infra/`'s existing resources also supports SES, or that sending
    from a different region than the rest of the stack is acceptable (it's a separate
    service call, not something that needs to share a VPC with Aurora).
- **Where this becomes `infra/` work:** the SES domain identity + DKIM configuration + the
  narrowly-scoped IAM sending policy are AWS resources, and per this repo's own convention
  (prefer CDK over console click-ops for anything durable) belong in `infra/` as a new
  construct once AWS credentials are connected — that's `cdk-engineer` work, not something
  to hand-configure in the AWS console and then forget exists outside version control.
  The Python script that *calls* SES (formats and sends a specific note) is homelab-side,
  same as the rest of this doc and `orchestrator-design.md`'s container — not `infra/`.

---

## 9. Relationship to what already exists

- **Sequencing against `orchestrator-design.md`'s open items:** this bridge does not
  require §2's Aurora data-access decision to be made — commands like `status`, `audit`,
  and `infra-check` don't touch client data at all, and are exactly the right commands to
  build and prove the bridge with first. Don't wire a `/pipeline run insight-note`
  command until the insight-note pipeline itself works end to end on its own weekly cron
  (per the orchestrator doc's own week-3 plan) — the Slack layer should trigger a
  pipeline that already works standalone, not become the first place that pipeline is
  ever exercised.
- **This replaces today's in-session Claude Code push notifications, once built — not
  before.** The push notifications available in a live Claude Code session (what's being
  used to work on this very design doc) only exist while that particular chat session is
  open and expire on a short window; they are a development-time convenience, not an
  operations channel. Nothing about this design doc changes that today. Once the Slack
  bot + SES pipeline described here is actually running, it becomes the durable
  always-available answer to "notify Derrick, anywhere, any time" that the in-session
  notifications were only ever standing in for.
- **Phone push notifications specifically** don't need any custom push infrastructure —
  Slack's own mobile app already delivers native push notifications for DMs and mentions.
  Posting the bot's results into a DM or a channel Derrick has notifications on on his
  phone *is* the push channel; no separate push service (APNs/FCM integration, etc.) is
  needed for this design to satisfy "notify me on my phone."
- **Not `infra/` work, mostly.** Like the orchestrator's homelab container, the bot
  process, its Slack SDK usage, and the audit-log file are `lab/pipeline-in-a-box/`
  homelab-side work, not `infra/`. The one piece that is `infra/` work is SES's domain
  identity/DKIM/IAM policy (§8) — flagged there, not duplicated here.
- **This replaces `business/10-operating-rhythm.md`'s near-term bridge, not just the
  in-session notifications.** That doc already names this exact bot ("the Slack bot +
  local orchestrator `cloud-engineer` is building") as the intended eventual delivery
  path for its Friday weekly summary and same-day ad hoc flags, and defines a
  zero-infrastructure stopgap in the meantime: appending each Friday's summary to a
  running file (e.g. `lab/pipeline-in-a-box/business/ops-log.md`). Once this bot ships,
  §8's digest phase (§10 Phase 4 below) should deliver *that same content shape* — the
  weekly summary format `10-operating-rhythm.md` §3 already defines (replies/leads,
  client status changes, hours vs. budget, blockers, next week's priority) — via Slack
  and email instead of a hand-appended file. The cadence and content don't change per
  that doc's own framing; only the delivery mechanism does. Don't redesign the reporting
  rhythm here — reuse it.

---

## 10. Rough build phases

AWS isn't connected yet in this environment, so phases 0–1 deliberately need nothing from
AWS at all — they can start immediately and in parallel with Derrick's own AWS credential
setup, rather than blocking on it.

**Phase 0 — Slack app skeleton (no AWS, no real subagent calls yet)**
Create the Slack app (Socket Mode enabled), generate the app-level + bot tokens, invite it
to a private Derrick-only channel. Build the bot's transport + §3 auth layers (signature/
token check is implicit under Socket Mode, but *write and test the Derrick-user-ID
allowlist check explicitly* — don't skip it just because Socket Mode already narrows who
can reach the bot). Wire exactly one command: `/pipeline status`, returning a hardcoded
"bot is alive" response. Proves the whole bridge shape safely before it can do anything.

**Phase 1 — First real subagent call, still read-only**
Wire `/pipeline audit` → `bungi` end to end: real `claude -p` subprocess invocation,
async execution (§5), result posted back to the originating thread, full audit logging
(§6). This is the phase that proves the actual "Slack → local Claude Code subagent →
Slack" loop the whole design exists for — and it's the one to spend the most testing time
on, since every later command reuses this same plumbing.

**Phase 2 — Expand the command allowlist as AWS comes online**
Once Derrick's AWS credentials are connected and `infra/`'s baseline is actually
deployable, add `infra-check` (`cdk synth`/`cdk diff`, explicitly not `deploy`). Add
`run insight-note` only once `orchestrator-design.md` §2 is decided and that pipeline
works standalone via its own cron (§9) — this phase should not be the thing that forces
that decision early.

**Phase 3 — Email channel (parallel track, can start alongside Phase 1/2)**
Independent of the Slack work — start domain/DNS verification for SES early since DNS
propagation and the production-access request both have real lead time (§8). Build the
`boto3` sending helper against SES sandbox mode first (sending to Derrick's own verified
address), request production access once SPF/DKIM/DMARC are in place, and only then wire
it to send a real client-facing note.

**Phase 4 — Digest**
Combine the audit log (§6) + pipeline run logs + (once it exists) business metrics into a
daily/weekly digest, delivered both ways: posted into Slack (native mobile push, §9) and
sent via SES (§8) as a standing email. This is the first feature that's genuinely useless
without both channels already working, so it comes after both.

**Phase 5 — Hardening**
Secret rotation runbook, review of the audit log for anything unexpected, decide whether
any deploy-capable command ever gets added to the allowlist (§3.5) and if so build its
second-factor confirmation flow, and revisit multi-client fan-out (both here and in
`orchestrator-design.md` §3) once there's a second real client generating enough Slack/
email volume to matter.

---

## 11. What's explicitly not decided or built yet

- Whether Option A (Socket Mode) or B (HTTP + signing) actually ships — recommendation
  given, not final.
- The exact `claude` CLI flags (`--permission-mode`, `--output-format`, tool-scoping)
  each allowlisted command should run with — needs verification against the real CLI on
  the TrueNAS box, not just this doc's citations.
- Whether any deploy/destroy-capable command ever gets a Slack path, and if so, its
  second-factor confirmation design (§3.5).
- SES sending region and whether it shares a region with the rest of `infra/`.
- Everything `orchestrator-design.md` itself still has open (§2 data access chief among
  them) — this doc depends on some of those resolutions (§9) but doesn't resolve them.

**Hand-off:** once AWS is connected and this is ready to actually build, the SES domain
identity/DKIM/IAM piece (§8) is `cdk-engineer` work extending `infra/` per its existing
conventions. The Slack bot itself — transport, auth layers, command allowlist, audit
logging, the `claude` CLI subprocess wiring — is homelab-side `lab/pipeline-in-a-box/`
work, same category as the orchestrator's own container, not `infra/`. Nothing in this
document should be built, deployed, or connected to a real Slack workspace or AWS account
without a separate, explicit go-ahead — this is a design doc only.
