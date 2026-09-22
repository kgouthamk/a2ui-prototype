# Test inputs

Copy any block below into the **Markdown input** box at `http://localhost:5173`
and click **ENRICH**. Each one says what widgets it should produce, so you can
tell a bad result from a broken one.

Not running yet? See [Run it](README.md#run-it). Offline, with no API key:
`A2UI_DEMO=1 uvicorn app.main:app --reload` renders a fixed rich sample.

---

## Interactive

These produce working forms. Fill them in and press the button: the client posts
the action id plus your values to `/api/action`, and the agent returns a new tree.

### 1. Claim review

Expect `Select` + `TextField` + `Checkbox` + `Button`, above a `KeyValueList` of
the claim facts. Submitting should return a green success `Alert` and echo your
values back.

```markdown
## Claim Review - CLM-2026-88392

**Policyholder:** Apex Logistics LLC
**Total Claimed:** $148,500.00
**Date of Loss:** Aug 14, 2026

The adjuster must record a decision. Choose an outcome (Approve, Deny, or
Request more information), enter reviewer notes, and indicate whether a site
inspection is required. Then submit the review.
```

### 2. Release sign-off

Expect a `Stepper` for the rollout and a form in the same tree, plus a `warning`
`Alert` for the breaking migration.

```markdown
# Release 4.2.0 — Sign-off Required

Changes: payments retry logic, new audit log, dropped Node 18 support.

Warning: this release includes a breaking migration.

Rollout is: 1. canary at 5% 2. hold 30 minutes 3. full fleet.

The release manager must pick a target environment (staging, production,
production-canary), confirm they have read the migration notes, and optionally
leave a note for the on-call engineer before approving.
```

### 3. Expense submission

Exercises `Switch` and a multiline `TextField`.

```markdown
## Expense Report

**Employee:** J. Okafor
**Period:** September 2026
**Total:** $2,310.40

Submit the report: choose a cost centre (Engineering, Sales, Operations),
describe the largest line item, toggle whether receipts are attached, and
toggle whether this needs expedited reimbursement.
```

### 4. Deliberately broken

Expect a **warning box**, not a dead button. A control that cannot work is
supposed to say so rather than look clickable and do nothing.

```markdown
Show me a button that says "Click me" with no action attached to it.
```

---

## Presentational

### 5. Widest catalog coverage

Expect `Heading`, `KeyValueList`, `Alert(warning)`, `Table`, `Stepper`,
`Accordion` and `ChipGroup` in one tree. This is also the input most likely to
trip the provider's JSON validator, because failure rate scales with tree size —
if it comes back plain, check the backend terminal.

```markdown
# Incident Report: Checkout Outage

**Incident ID:** INC-4471
**Severity:** Sev-1
**Duration:** 47 minutes

> Warning: the rollback script has a known bug on multi-region clusters.

## Impact by region

| Region | Requests Failed | Error Rate |
|--------|-----------------|------------|
| us-east-1 | 84,200 | 31% |
| eu-west-2 | 11,900 | 8% |

## Remediation steps

1. Drain traffic from the failing ASG
2. Roll back payment-service to v3.8.1
3. Verify checkout in a canary session

## Follow-up questions

**Why did the canary not catch this?** It does not cover the multi-region path.
**Can this recur?** Yes, until the deploy gate is updated.

Tags: payments, sev1, postmortem
```

### 6. Alert severities

Expect three `Alert`s in different colours — `info`, `warning`, `error`.

```markdown
Note: backups run at 02:00 UTC.
Warning: restoring overwrites the live database.
Error: the last three backup jobs failed.
```

### 7. KeyValueList

Labels in a muted left column, values right. If value and label look swapped,
that is a regression in `registry.tsx`.

```markdown
**Order ID:** SO-99182
**Customer:** Northwind Traders
**Ship Date:** Oct 2, 2026
**Total:** $8,410.00
```

### 8. Table

```markdown
Plan comparison: Basic is $10/mo with 1 seat, Pro is $30/mo with 5 seats,
Enterprise is $120/mo with unlimited seats.
```

### 9. Stepper

```markdown
To rotate the signing key: first generate a new keypair, then upload the public
half to the IdP, then update the secret in the vault, then restart the auth pods.
```

### 10. ChipGroup and List

```markdown
Skills: Python, Kubernetes, Terraform, PostgreSQL, gRPC

The deployment requires: a valid TLS cert, a configured load balancer,
at least two healthy replicas, and a populated secrets store.
```

---

## If the output looks plain

A `Card` containing one block of your own text, unchanged, is the **fallback** —
the agent did not reach the model, or the reply was unusable. It is not the model
choosing badly. The backend terminal names the cause on every fallback:

| Log reason | What it means |
|---|---|
| `model_call_failed:AuthenticationError` | bad or missing API key |
| `model_call_failed:NotFoundError` | the model in `A2UI_MODEL` was retired |
| `model_call_failed:RateLimitError` | free-tier quota spent |
| `model_call_failed:BadRequestError` | provider rejected its own JSON; retries usually absorb it |
| `invalid_json` / `schema_violation` | reply was not valid JSON, or used an off-catalog widget |

The fallback echoes your input **verbatim**, so if the "Cleaned markdown" tab is
byte-identical to what you pasted, the model was never reached.

## Budget

Every ENRICH is one model call and every form submit is another; a failure costs
up to `A2UI_RETRIES` more. Free tiers are small — Gemini AI Studio allows 20
requests per day per model. Running `pytest -q` in `evals/pytest` spends 3.
