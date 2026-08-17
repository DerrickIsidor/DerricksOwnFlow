> **DISCLAIMER — read before using anything in this document.** This is educational
> starting scaffolding written by an AI. It is **not legal advice, not tax advice, and
> not a substitute for a licensed attorney or accountant in Georgia**. Every template,
> number, and recommendation below must be reviewed (and very likely edited) by a real
> licensed Georgia attorney and a real accountant before it is used with an actual paying
> client, signed, or filed with any state or federal agency. Filing fees and thresholds
> below are current as of this writing (Aug 2026, sourced from the Georgia Secretary of
> State and general tax-guidance sources cited inline) and can change — verify the live
> number on the official site before filing or paying anything.

# Legal & Financial Foundation — LLC, Contracts, Banking (Starter Scaffolding)

**What decision this supports:** Derrick has no entity yet, has decided the plan/pricing/
strategy is solid enough to commit to, and wants to move toward a Georgia LLC. This
document teaches the real steps, flags the one real regulatory landmine in the current
ICP (home health/HIPAA), and gives starter contract templates — built out over the coming
weeks per Derrick's request, not something to file or sign today without counsel.

---

## 1. Why an LLC, and why Georgia

**Why an LLC fits this business.** A sole proprietorship (what Derrick has by default
today, with no entity formed) offers **no liability separation** — if a client dispute,
data-handling mistake, or lawsuit happens, Derrick's personal assets (savings, car, home
equity) are exposed, not just the business's. An LLC creates a legal wall between the
business and Derrick personally, *as long as that wall is respected* (see §3 on
commingling — this is the single most common way people accidentally void their own
protection). For a solo service business handling client business data — exactly what
Pipeline-in-a-Box does — that liability separation is the main reason to form an entity
at all, more than any tax benefit.

**Why Georgia, not Delaware/Wyoming.** Delaware and Wyoming get recommended constantly
online, but that advice is written for venture-backed startups planning outside
investment or eventual acquisition — Delaware's appeal is its specialized business court
and case-law predictability, which mostly matters once there are multiple investors,
complex cap tables, or litigation risk at a scale this business isn't at. **For a solo
service business that operates and has its only owner in Georgia, forming in Georgia is
normally simpler and cheaper**, because forming out-of-state doesn't avoid Georgia
involvement — Derrick would still have to register the Delaware/Wyoming LLC as a
"foreign LLC" doing business in Georgia, meaning **two states' filing fees and two
annual registrations** instead of one, for no real benefit at this stage. Unless a
specific future reason applies (outside equity investment, a Delaware-based investor
requiring it), Georgia is the right call.

---

## 2. The real Georgia LLC formation steps

Sourced from the Georgia Secretary of State's Corporations Division (sos.ga.gov) —
verify current fees at the official site before filing, since fees do change:

1. **Name check and reservation (optional).** Search the GA Sec of State's business name
   database to confirm the desired name isn't taken. Not legally required before filing,
   but avoids a rejected filing.
2. **File Articles of Organization.** Filed online (eCorp) or by mail with the GA
   Secretary of State. **Fee: $100 base + $10 service charge = $110 total**, same amount
   whether filed online or by mail. This is the one filing that actually creates the
   legal entity.
3. **Registered agent.** Every GA LLC must designate a registered agent — a person or
   service with a physical Georgia street address (no P.O. boxes) who can receive legal
   documents on the LLC's behalf during business hours. Derrick can be his own registered
   agent at no extra cost if he's comfortable using his own address as a matter of public
   record; commercial registered agent services typically run **roughly $50–150/year**
   for privacy and to guarantee someone's always available at that address (verify current
   pricing with a specific provider before choosing — not sourced from an official fee
   schedule the way the filing fees above are).
4. **Get a free EIN from the IRS.** An Employer Identification Number (like a Social
   Security Number for the business) is issued **for free, instantly, at irs.gov**, once
   the LLC is formed. **Never pay a third-party site for this** — it's a common scam/
   markup; the only legitimate source is the IRS's own online EIN application.
5. **Write an Operating Agreement.** Not filed with the state, but should exist even for
   a single-member LLC — it's the internal document establishing that the LLC is a real,
   separately-managed entity (how it's managed, how profits are handled, what happens if
   Derrick brings on a partner or sells the business later). Courts look at whether an
   operating agreement exists, among other things, when deciding whether to respect an
   LLC's liability shield in a dispute — skipping it weakens the exact protection the LLC
   exists to provide.
6. **Annual Registration.** Georgia LLCs must file an Annual Registration every year,
   window **January 1 – April 1** starting the year after formation. **Fee: $50 base +
   $10 service fee = $60 total**, effective for filings starting January 1, 2026. Missing
   this risks the LLC being administratively dissolved.

**Rough total to get the LLC itself formed: about $110 (formation) + $0 (EIN) + $0–150
(registered agent, if not self-serving) — call it $110–260 to actually exist**, plus $60
every year after to stay in good standing. This is a real, small number — worth
confirming against the live GA Sec of State fee page before paying, since fee schedules
do change.

---

## 3. Business banking — open it before the first client payment

**Do this as soon as the LLC and its EIN exist, and before taking client #1's first
payment, no exceptions.** Open a dedicated business checking account under the LLC's
legal name and EIN (most banks require the EIN confirmation letter and the filed Articles
of Organization to open one) — every business inflow (setup fees, monthly retainers) and
outflow (AWS costs, any tooling) should run through that account, never Derrick's
personal checking.

**Why this matters more than it sounds like it should:** the entire point of forming an
LLC is the liability wall in §1. **Commingling personal and business funds is the single
most common way that wall gets pierced** — if a dispute ever ends up in court, a judge
looking at whether to hold Derrick personally liable will look at whether the business
was actually run as a separate entity (own bank account, own bookkeeping) or was really
just Derrick's personal finances with an LLC name stapled on. A $0-fee business checking
account (many banks and credit unions offer one with no minimum balance for a business
this size) is cheap insurance for the liability protection Derrick is paying $110 to
create in the first place.

---

## 4. When to consider an S-corp election — not now, but know the signal

**Don't do this now.** An LLC can elect to be taxed as an S-corporation (a tax election,
not a different legal entity) once net business income is high enough that the added
payroll/administrative complexity pays for itself. The mechanism: instead of paying
self-employment tax (15.3%) on all net income, an S-corp owner pays themselves a
"reasonable salary" (subject to payroll tax) and can take the remaining profit as a
distribution not subject to self-employment tax — the savings come from that split.

**The real threshold to watch for, not a rule to act on today:** general guidance
converges on **roughly $40,000–80,000 in annual net business income** as the point where
the self-employment-tax savings start to outweigh the added cost — S-corp status adds
real ongoing costs (running actual payroll, more complex bookkeeping, a separate S-corp
tax return), commonly estimated at **roughly $1,500–3,000/year in added compliance
cost**. Below that net-income range, the S-corp election is very likely a net loss once
those costs are counted, not a savings.

**Where this lands against `07-financial-model.md`:** the solo Pipeline-in-a-Box ceiling
alone (~$2,300–5,700/mo revenue, not net income — AWS costs are negligible per that
model, but there's no owner-salary or expense baseline modeled yet) puts *revenue* in a
range that could approach this threshold at the top of the ceiling, but **net income is
a different, lower number once real expenses are counted** — this is a "watch for it,"
not a "do it in 2026" signal. Revisit with a real accountant once there's a full year of
actual net-income numbers, not a revenue projection.

---

## 5. Client contracts — starter templates

**These are drafting starting points, not final legal documents.** Every bracket needs
Derrick's real information, and the whole set needs a licensed GA attorney's review
before any client sees or signs one — these templates have not been reviewed by an
attorney.

### 5a. Master Service Agreement (MSA) — starter template

```
MASTER SERVICE AGREEMENT

This Master Service Agreement ("Agreement") is entered into as of [DATE] between
[LLC LEGAL NAME], a Georgia limited liability company ("Provider"), and
[CLIENT LEGAL NAME] ("Client").

1. SERVICES. Provider will perform the services described in one or more Statements
   of Work ("SOW") executed under this Agreement. Each SOW incorporates this Agreement
   by reference. In the event of a conflict, the SOW controls for that engagement.

2. TERM AND TERMINATION. This Agreement begins on the Effective Date and continues
   until terminated. Either party may terminate a monthly service arrangement with
   [30] days' written notice. Provider may suspend services immediately for
   non-payment beyond [15] days past due.

3. FEES AND PAYMENT. Client will pay the setup fee and monthly fee specified in the
   applicable SOW. Monthly fees are due [in advance / on the 1st of each month].
   Late payments beyond [15] days may result in suspension of services.

4. DATA ACCESS AND OWNERSHIP. Client grants Provider access to the data sources
   specified in the SOW solely to perform the Services. Client retains all ownership
   of its underlying business data. Provider owns the pipeline code, dashboard
   templates, and infrastructure configuration it builds, but Client's specific data
   and any client-specific outputs (dashboards populated with Client's data, insight
   notes) belong to Client.

5. CONFIDENTIALITY. See attached Confidentiality Clause (Section 5c of this
   document set), incorporated by reference.

6. LIMITATION OF LIABILITY. [PLACEHOLDER — an attorney should set an appropriate
   liability cap here, commonly tied to fees paid in a recent period; do not leave
   this unlimited.]

7. NO WARRANTY OF BUSINESS OUTCOMES. Provider builds and maintains data pipelines,
   dashboards, and reporting. Provider makes no guarantee about business decisions
   Client makes based on that reporting.

8. GOVERNING LAW. This Agreement is governed by the laws of the State of Georgia.

9. INDEPENDENT CONTRACTOR. Provider is an independent contractor, not an employee,
   partner, or joint venturer of Client.

[SIGNATURE BLOCKS]
```

### 5b. Statement of Work (SOW) — Starter / Growth tier template

```
STATEMENT OF WORK

Under the Master Service Agreement dated [DATE] between [LLC LEGAL NAME] and
[CLIENT LEGAL NAME].

TIER: [ Starter | Growth ]

SCOPE OF SERVICES:
- Data sources to be connected: [list — e.g., QuickBooks export, scheduling tool export]
- Pipeline: extract from the above source(s), load into Provider's managed database
- Dashboard: [1 dashboard | multi-source dashboard with alerts], refreshed
  [weekly | on a schedule tailored to Client's operations]
- Weekly written insight note: yes, delivered via [email/doc — to be finalized]

FEES:
- Setup fee: $[750 Starter / $2,000 Growth], due upon signing
- Monthly fee: $[300 Starter / $750 Growth — note "founding client" pricing if
  applicable per 05-pricing-sanity-check.md], due [monthly, in advance]

ONBOARDING TIMELINE: estimated [X] weeks from data access being granted to first
dashboard delivery — actual timeline depends on Client's data export availability,
not solely on Provider's build time.

DATA ACCESS NEEDED FROM CLIENT: [specific list — read-only export or API credential
for each named source; Provider will specify exactly what access is requested and
why, per Client's own qualifying/pain-signal notes in 02-icp-prospecting.md's
trust-building approach].

TERM: month-to-month following setup, cancellable per Section 2 of the MSA.
```

### 5c. Confidentiality clause / short mutual NDA

```
CONFIDENTIALITY

Both parties may disclose confidential business information to each other in
connection with this engagement, including but not limited to Client's business data,
financial information, and operational details, and Provider's methods, pipeline
designs, and pricing.

Each party agrees to:
(a) use the other party's confidential information only to perform or receive the
    Services under this Agreement;
(b) not disclose the other party's confidential information to any third party
    without written consent, except as required by law;
(c) protect the other party's confidential information with at least the same care
    it uses for its own confidential information, and no less than reasonable care.

This obligation survives termination of the Agreement for [2] years, except for
Client's underlying business data, which Provider will delete or return within
[30] days of termination upon Client's written request.

This clause does not restrict either party's use of information that is or becomes
publicly available through no fault of that party.
```

---

## 6. The one real compliance landmine: home health / elder care and HIPAA

**This is a decision point, not a footnote.** `02-icp-prospecting.md` explicitly lists
home health/elder care agencies as one of the four target segments. **Licensed home
health agencies (and many non-medical home care agencies that bill Medicaid or work with
covered providers) are very likely HIPAA "covered entities" or work with data that makes
this business a "business associate"** the moment Pipeline-in-a-Box touches client
scheduling, billing, or care data that includes any protected health information (PHI) —
even something as ordinary as a caregiver visit log tied to a named client can qualify.

**What that means in practice, before signing a home-health client:**
- A signed **Business Associate Agreement (BAA)** is very likely required — a separate,
  specific legal document (not covered by the general MSA/NDA above) that HIPAA requires
  between a covered entity and any vendor that creates, receives, maintains, or transmits
  PHI on its behalf.
- Materially more compliance work than any other current segment: encryption of PHI at
  rest and in transit (verify the current `infra/` Aurora/Lambda setup actually meets
  this bar — that's a `cloud-engineer` question, not a legal one, but the legal
  requirement is what triggers needing the technical answer), documented access
  controls (who can see what data), and a written breach-notification procedure.
- **This is real added cost and real added risk** (HIPAA violations carry meaningful
  penalties), not a checkbox — it should factor into whether a home-health prospect is
  worth pursuing at founding-client pricing, or whether it needs its own SOW pricing that
  accounts for the extra compliance build.

**The concrete recommendation:** before signing any home-health/elder-care client, stop
and get a real answer to two questions with a licensed Georgia attorney (and likely a
compliance-aware accountant): (1) does this specific client's engagement make Provider a
HIPAA business associate, and (2) what does a compliant BAA and the underlying technical
controls actually require here. Don't treat the generic MSA/SOW/NDA templates above as
sufficient for this segment — they explicitly are not.

---

## 7. What's left to build out (per Derrick's request, over the coming weeks)

- Attorney review of every template in §5, and a real BAA template if/when a home-health
  prospect is actually close to signing (§6) — don't draft one speculatively without a
  real client in front of it, since BAA terms depend on the specific data flow.
- A real bookkeeping/accounting setup (even a simple spreadsheet or a tool like Wave/
  QuickBooks Simple Start) to actually produce the net-income numbers §4's S-corp
  threshold depends on — nothing here estimates that yet.
- Confirm current GA filing fees at sos.ga.gov before filing anything — the numbers in
  §2 are current as of this writing but not guaranteed to stay so.
