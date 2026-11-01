# Nine-Box Customer Discovery Canvas – Health Insurance Cashless Authorization

- **CUSTOMER / PROJECT:** Health insurer (name TBC) – Cashless Authorization Delay Discovery
- **FDE / TEAM:** Saranya M – Forward Deployed Engineer
- **DATE / VERSION:** 01-Nov-2026 / v1.0 (pre-validation draft)

Legend: **[F]** Fact (stated by customer) · **[A]** Assumption (to validate) · **[U]** Unknown (open question) · **[D]** Decision / action with owner

## 01 Customer & Stakeholders
- **[F]** Sponsor: COO. Raised the problem and wants evidence before investing.
- **[F]** Process users: network-hospital insurance desks and the insurer's operations teams (review, clarification, hospital communication). Policyholders are affected while they wait.
- **[A]** Probably also involved: medical reviewers, a TPA (if outsourced), the provider-network team, the call centre, IT/platform owners and compliance.
- **[U]** Who owns the end-to-end turnaround-time (TAT) KPI today? Is it Ops, Claims, or nobody?
- **[U]** Who approves budget and solution? The COO alone, or with the CIO and CFO?
- **[U]** Who says the cause is technology and who says it is process? What evidence does each group have?

## 02 Business Objective
- **[F]** Trigger: complaints from hospitals and policyholders have been rising for several months.
- **[F]** COO's concerns: operational efficiency, hospital relationships, customer satisfaction and reputation.
- **[F]** COO's constraint: no new solution until the actual cause is understood.
- **[U]** Why now? Volume growth, a new platform go-live, staff turnover, rule changes or a regulator notice?
- **[U]** Do regulatory TAT norms apply (e.g., IRDAI's 1-hr cashless / 3-hr discharge limits in India)? Are they being breached?
- **[U]** If speed conflicts with fraud and leakage control, which wins?

## 03 Expected Outcomes
- **[A]** Candidate measures (none agreed yet): end-to-end and per-stage TAT (median and P90) for initial, enhancement and discharge authorizations.
- **[A]** Fewer status follow-ups from hospitals; fewer cases pending beyond SLA; fewer query cycles.
- **[A]** Higher hospital satisfaction and policyholder CSAT; fewer complaints and grievances.
- **[A]** Ops productivity: cases per FTE; touch time vs. waiting time.
- **[A]** Guardrail: no increase in wrongful approvals or denials, claim leakage or fraud.
- **[U]** Target values, baseline period, timeline and who measures success? To be agreed with the COO.

## 04 Current Process / As-Is
- **[F]** Hospital submits a cashless request, the insurer reviews it and the decision goes back to the hospital. Several applications and teams are involved.
- **[A]** Draft flow to check: intake → registration and data entry → eligibility and coverage check → document check → medical review → query loop with the hospital → decision → communication → enhancements → final discharge approval → claim settlement.
- **[U]** Which intake channels are used (portal, email, fax, phone), and what share does each carry? Is data re-keyed between systems?
- **[U]** Where do cases queue? How are they assigned and prioritised? Is there night and weekend cover?
- **[U]** How do hospitals and policyholders see request status today?
- **[D]** How to confirm: process walkthrough, shadowing reviewers, and mining stage timestamps from the system logs.

## 05 Core Problem & Pain Points
- **[F]** Reported but not measured: requests pending longer than expected; hospitals chase status repeatedly; policyholders are uncertain; Ops spends a lot of effort on review, clarification and follow-up.
- **[F]** Root cause is not established. Stakeholders disagree on whether it is technology or process.
- **[A]** H1 Incomplete or incorrect submissions drive query loops. H2 Fragmented systems force manual re-keying. H3 Capacity, peak-hour or shift gaps.
- **[A]** H4 Unclear rules or inconsistent medical review. H5 No status visibility, so chase calls add load. H6 A few hospitals or treatment types cause most of the delay.
- **[U]** Is "longer than expected" measured against a defined SLA? Is the delay mostly waiting time (queues, hospital replies) or working time?

## 06 Business Impact & Baseline
- **[U]** Cashless requests per day: peaks, and breakdown by hospital, planned vs. emergency, and stage?
- **[U]** Current TAT distribution per stage? What % breach SLA? How many requests are pending now, and how old are they?
- **[U]** Query rate, query cycles per case, and time spent waiting on hospital responses?
- **[U]** Volume and handling time of status calls and emails? Complaint and grievance trend?
- **[U]** Ops FTE, cost per case, overtime and rework?
- **[U]** Cost of delay: extra bed-days, cases switched to reimbursement, hospital disputes or exits, renewals lost, regulatory penalties?
- **[F]** No baseline numbers exist yet. Nothing is estimated until data arrives.

## 07 Data, Systems & Constraints
- **[F]** Several digital platforms and applications already support cashless operations.
- **[U]** System inventory: hospital portal, pre-auth/claims, policy admin and eligibility, provider master and tariffs, document management, CRM/call centre, rules engine?
- **[U]** Are timestamps captured at each stage? Who owns the data, how good is it, and how do we get access?
- **[U]** Integrations: APIs or manual? Links to TPA and hospital systems? Standard formats (e.g., NHCX)?
- **[A]** Constraints to confirm: health-data privacy (e.g., DPDP Act), regulatory TAT and audit trail, qualified humans making medical decisions, fraud controls, IT change windows, budget.

## 08 Requirements & MVP Options
- **[A]** First step, no new build: a diagnostic. Extract event logs and build a stage-wise TAT, ageing and query-reason view.
- **[A]** Candidates, chosen only after evidence: (a) smart intake checklist and validation per treatment type (if H1); (b) live status tracker and alerts for hospitals and members (if H5).
- **[A]** (c) Prioritised work queues with SLA-breach alerts and shift rebalancing (if H3); (d) integration or document extraction (if H2); (e) clearer guidelines and AI case summaries, with humans deciding (if H4).
- **[A]** Smallest useful pilot: one fix, for the 5–10 hospitals with the most volume or pending cases, run for 4–6 weeks against a control group.
- **[F]** No option is committed until boxes 05 and 06 are validated.

## 09 Validation & Next Steps
- **[D]** 1. Confirm sponsor, decision owner, objectives and success metrics. Owner: COO (week 1).
- **[D]** 2. Get 3–6 months of pre-auth records with stage timestamps and query reasons. Owner: CIO / data owner.
- **[D]** 3. Walk through the process and shadow Ops. Interview 5–8 hospitals, mixing fast and slow ones. Owners: Ops head and provider-network head.
- **[D]** 4. Analyse delay by stage and Pareto the causes; quantify impact. Owner: FDE team.
- **[D]** 5. Readout of validated causes, quantified impact and ranked options. COO picks the pilot. Compliance and the CMO approve clinical and regulatory guardrails.
- **[U]** All proposed owners need confirmation at the next meeting.

## Supporting Notes

### A. Hypotheses and evidence needed

| Hypothesis | Evidence needed |
|---|---|
| H1 Incomplete/incorrect submissions | Query rate, query reasons, query cycles per case, by hospital |
| H2 Fragmented systems / re-keying | Handoffs between systems; time between stages with no active work |
| H3 Capacity / shift gaps | Arrivals vs. throughput by hour and day; backlog age; FTE roster |
| H4 Rules / review inconsistency | Decision time and outcome variance by reviewer for similar cases |
| H5 Lack of status visibility | Status-call volume and handling time; repeat contacts per case |
| H6 Concentrated segment | Pareto of delay by hospital, treatment type, policy type, region |

### B. Discovery question bank

**COO / Sponsor**
- Which complaint first made this a priority? Can you share examples?
- What would success look like in 3 and 6 months, in numbers?
- What budget, timeline and risk appetite apply? What is off-limits?

**Operations Manager / Team Leads**
- Walk me through one recent delayed case from intake to decision.
- How is work assigned and prioritised? What happens at shift change and after hours?
- Which tasks take the most time? Which ones feel like rework?
- What are the top reasons you raise queries with hospitals?

**Medical Reviewers**
- Which cases take longest to decide, and why?
- Are guidelines clear and applied consistently? How often do you need to escalate?

**Network Hospital Insurance Desks**
- How do you submit requests? What do you do while a request is pending?
- What queries do you get most often? Could they be avoided at submission?
- How do you find out status? How many times do you follow up per case?

**IT / Platform Owners**
- Which systems touch a request? Where is data re-entered by hand?
- Are stage timestamps logged? Can we get an extract, and what approvals are needed?
- What platform changes went live in the last 12 months?

**Customer Service / Policyholders**
- How many contacts are about authorization status? What do callers want to know?
- What happens to the patient and family while they wait?
