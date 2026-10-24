---
inclusion: always
---
# Tether engineering conventions

Read `.kiro/specs/tether-core/` and `docs/decisions.md` before changes. The revised build guide supersedes conflicting original plan sections. Preserve Dana's home-health coordinator persona. Synthetic data only; never claim clinical validation, utility integration or guaranteed emergency detection.

P2 owns canonical Pydantic contracts and infrastructure. Generate OpenAPI and TypeScript; never edit generated types. Build one stage at a time and record commands, results, mocks and blockers in `docs/evidence/`. No automatic extra agents or concurrent deployment owners.

AWS target Region: us-east-1, selected by the user. Account/profile are unconfirmed. Do not select a different account or create credentials. Use temporary organizer credentials locally, never chat or source. Deploy Tether-prefixed resources only after target verification.

202 means a committed atomic intake transaction, not an enqueued in-memory task. Commit inbox/job/audit/outbox together. No live write-then-publish dual-write gap. At-least-once queues require durable idempotency, payload conflicts, fenced leases, bounded attempts and recovery queries. No swallowing worker exceptions or acknowledging unfinished records.

Only validated staff membership grants tenant/role access. Patient simulator credentials are short-lived and scoped to patient/event. Human case acknowledgment/resolution are distinct from delivery, triage and patient state. AI or patient replies never close cases. Unknown fields remain unknown; exact evidence quotes must occur in the original.

Emergency keyword decisions precede AI and remain active if AI fails. Treat all message/notice content as untrusted data. No clinical advice. No secrets in VITE_*; no conversations, authorization headers or guardrail traces in routine logs. SNS contains opaque alert IDs and authenticated links only.

Reserve shared model quotas and conservative spend before each call, including retries/repairs. SDK hidden retries disabled. Default at most 2 model attempts/job and 5 calls/test run. No precise cost without dated model/Region prices and usage. All screens label SYNTHETIC DEMO DATA and MOCK/LIVE BEDROCK/REPLAY honestly.
