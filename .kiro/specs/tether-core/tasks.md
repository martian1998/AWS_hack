# Owner tasks and checkpoints

P1 AI, P2 backend/cloud and sole deployment owner, P3 frontend, P4 data/evidence. Each row identifies dependencies, affected paths, check and evidence. Contract v1 is a reviewable baseline, not a claim of team approval. No optional features before Stage D safety checks.

Checkpoint status: **A local implementation verified**; live model preflight is blocked by absent AWS access/configuration. Evidence: `docs/evidence/stage-a.md`. **B–E are not implemented/deployed.**

| Stage / owner | Task | Depends on | Files | Acceptance / evidence |
|---|---|---|---|---|
| A / P2 | Spec, canonical models, OpenAPI generation, fail-closed API and SAM baseline | Source reconciliation | .kiro/, backend/, shared/, infra/ | Schema tests, synchronized types, SAM lint; docs/evidence/stage-a.md |
| A / P1 | Model/Guardrail capability preflight and bounded probe | Approved AWS target and model | scripts/preflight.py | Actual tool-use + Guardrail test or precise blocked report |
| A / P3 | Responsive mock board, thread, phone and case-state preview | Contract examples | frontend/ | Typecheck/build, browser navigation + simulator; labeled MOCK |
| A / P4 | Synthetic registry, notices, fixture examples, source inventory | Canonical models | data/, docs/source/ | 60 unique profiles, two tenants, five languages; fixtures validate |
| B / P2 | Identity, durable intake/idempotency, stream outbox, triage/urgent lanes | A + approved credentials | backend/, infra/ | Transaction rollback, duplicate/concurrency, tenant/patient deny tests |
| B / P1 | Converse, exact evidence, Guardrail, timeout->review, usage metadata | Live model capability | backend/tether/ai/ | One real Spanish reply, model metadata; cap tests |
| B / P3 | Authorized live job/thread read adapter | B API | frontend/src/ | Pending job remains distinct from processed; no secrets in build |
| B / P4 | Deployed smoke, replay and SNS arrival evidence | B worker + confirmed team SNS | scripts/, docs/evidence/stage-b.md | Durable request, live call, case, replay no duplicate; human confirms email |
| C / P1 | Notice extraction with ambiguity/unknown handling | B AI | backend/tether/ai/ | Three notices preserve unknown times/areas |
| C / P2 | Confirm/match/rank, bounded template outreach, scoped sessions, human case actions | B + notice contract | backend/, infra/ | Main flow and stale-version/role checks |
| C / P3 | Connect board/thread/case actions and Amplify deployment | C API | frontend/, infra/ | Unbroken deployed journey; all pending/error states |
| C / P4 | Seed sandbox and full smoke/security evidence | C deployment | scripts/, docs/evidence/stage-c.md | Unauthorized/other-agency rejection and human resolution |
| D / P1 | Shared admission, attempt reservations, conservative pricing bounds | B usage | backend/tether/ai/, data/pricing.json | Budget exhaustion; AI-disabled emergency path |
| D / P2 | Reconciliation, leases, DLQ replay, follow-ups, isolation | B/C | backend/, infra/ | Crash/reordering/cancellation tests; no silent losses |
| D / P3 | Recovery/unknown/error UI and audit pagination | D API | frontend/ | Cases stay active after ambiguous/safe replies |
| D / P4 | Recovery harness and authorization matrix regression | D implementation | tests/, scripts/, docs/evidence/stage-d.md | Cross-tenant, patient-token, stale-case, payload-conflict evidence |
| E / P1 | Bounded live evaluation, language misses and token report | Original gold set + D | eval/ | Recall counts, false positives/review rate, no clinical claim |
| E / P2 | Reconciled metrics/cost and deployment checks | D | backend/, docs/ | One state per accepted job; no DLQ double-count |
| E / P3 | Ops panel and 1080p polish | E metrics | frontend/ | Time-window/source labels and readable recording |
| E / P4 | Controlled load, cost worksheet, 5-minute video + verified upload | E evidence | eval/, scripts/, docs/ | Observed results only; deadline buffer preserved |

## Checkpoint rules

Run `scripts/check.sh` after each change to contracts. Stage A must be runnable locally even when AWS is unavailable. Stage B is first deployed checkpoint and remains blocked by credentials/account/model/Guardrail/identity/SNS. Stage C–E are planned; scripts must fail clearly if they are not implemented, never fabricate passing evidence. Keep the main flow ahead of maps/copilot/RAG/handoff/real SMS.

Submission source deck: hard stop Saturday October 24, 2026 at 11:00 AM Pacific; team target 10:30 AM Pacific. This repository does not schedule, record or upload the submission.
