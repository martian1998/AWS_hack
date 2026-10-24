# Tether core requirements — contract v1

Persona: Dana, the home-health coordinator responsible for outreach during a power shutoff. The goal is a repeatable synthetic notice-to-human-resolution journey, with real Bedrock evidence in later stages. This specification is prepared in Kiro's directory format; no Kiro IDE workflow execution is claimed.

## Acceptance criteria

| ID | Requirement and observable acceptance | Stage |
|---|---|---|
| R01 | When Dana submits a notice, return a durable job acknowledgment; extraction preserves unknown start/restore times and flags unrecognized areas. Outreach is blocked until uncertainty is explicitly confirmed. | B/C |
| R02 | Match only confirmed ZIPs through tenant/geography indexes. Show approximate geography and editable demo risk reasons. A board request returns at most 50 rows and a scoped cursor. Unknown backup/duration is never silently zero/48 hours. | C |
| R03 | POST events/outreach/inbound returns 202 only after all required records commit. Inject a transaction failure: return retryable 503 with no accepted job, message or case. | B |
| R04 | Bind idempotency to tenant, authenticated source, operation and client identity. Same identity/payload returns the original job; changed payload returns 409. Concurrent replay produces one message and one incident case. | B/D |
| R05 | A keyword emergency creates a case and urgent outbox in the intake transaction before any model result. Disable Bedrock and observe the case plus visible human review. | B/D |
| R06 | Store job status independently from patient, contact and case states. Every unique accepted job has exactly one current state; failed jobs remain visible. Attempts and notifications are separate records. | B/E |
| R07 | All workers use bounded SQS batches, partial batch failures, DLQs and fenced leases. Crash after publish, expired lease and stream outage leave recoverable work. Queue visibility >= 6 × worker timeout + batch window. | B/D |
| R08 | Notice and multilingual triage use a verified Bedrock model and published Guardrail. Strictly validate bounded schemas and original evidence. Refusal/timeout/invalid output becomes HUMAN_REVIEW after at most two metered attempts. | B/C/D |
| R09 | Initial outreach uses approved language templates in bounded batches. Cancellation or changed event version cancels stale work. A later safe/ambiguous message never closes an existing case. | C/D |
| R10 | Only a coordinator may assign, acknowledge or resolve cases. Resolve requires notes and expected_version; stale writes return 409. Patient credentials cannot read staff views or close cases. | B/C |
| R11 | Validate issuer/audience/expiry/access scopes and server-side tenant membership. Other-tenant or other-patient IDs return 404. Missing/invalid credentials return 401; insufficient same-tenant role returns 403. All job/audit/metrics routes are covered. | B/D |
| R12 | Encrypt persisted resources, use TLS and resource-scoped roles. Logs contain IDs/error codes only. SNS is minimal and contains no patient name/conversation. Audit application roles cannot update/delete existing entries. | B/D |
| R13 | Reserve shared request/token/run ceilings before a model call; count all repairs/retries. Budget exhaustion routes work to human review while deterministic escalation remains available. | D |
| R14 | Follow-ups query a due-time index, re-check event/reply/contact attempt, and ignore stale timers. TTL is retention only. Missing connectivity becomes human outreach, not an offline-delivery claim. | D |
| R15 | UI exposes pending/error/empty/unknown states; status colors include text. Original evidence, case owner and acknowledgment are visible. Every screen labels synthetic data and actual execution mode. | A/C/E |
| R16 | Operations reconcile durable state counts; metrics include source, observed timestamp and time window. Report intake and completion latency separately. Unknown queue/cost values display unknown, never zero. | E |
| R17 | Create 60 synthetic patients across two agencies and EN/ES/VI/ZH/TL. Preserve a supplied original 30-case gold set; if absent, flag that blocker instead of inventing provenance. New regressions are separate. | A/E |
| R18 | Stage evidence lists exact commands/results, mocks/live/unimplemented behavior, blockers and contract changes. No deployment/email/performance claim without observation. | All |

## Foundation checkpoint

Stage A delivers canonical Pydantic/OpenAPI contracts, generated TypeScript, examples, mock board/thread/phone, a safe API scaffold, SAM lint validation, local checks, preflight tooling and an explicit blocker report. Browser mocks do not prove AWS durability or authorization. Stage B cannot pass without a real model call and team-confirmed email arrival.

## Deferred scope

Maps, copilot, RAG, real SMS, agentic outreach and handoff summary wait until the core checks pass. No clinical decisions, emergency-service replacement, multi-Region build or million-patient deployment claim.
