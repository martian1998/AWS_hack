# Decisions and reconciliation — October 23, 2026

The revised guide is authoritative where it conflicts with `docs/source/Tether-Team-Build-Plan.md`. No existing implementation was present. Preserve the persona, original language/profile fields, notice/board/thread route names and synthetic-only scope. The idea PDF and original 30 labeled replies were not supplied/found alongside these named sources; no original evaluation data has been fabricated.

| Original plan | Revised decision |
|---|---|
| Synchronous notice and reply AI | 202 durable jobs with separate progress/result routes |
| Async Lambda invoke for a whole outreach list | Transactional outbox -> bounded SQS child jobs with continuation |
| Hash patient/text/minute | Authenticated source + stable client identity + payload digest; conflicts 409 |
| Global patient IDs and unscoped tables | Tenant-prefixed keys, trusted membership, patient/event-scoped simulator credentials |
| x-admin-token and public proxy | JWT/PKCE staff boundary, separate simulator validator, demo_admin guard; no public app proxy |
| Guardrail masks logs | Do not log raw content; explicitly screen tool fields; Guardrail is not invocation-log redaction |
| emergency false/device true defaults | Explicit yes/no/unknown and null values |
| Missing outage=48h/backup=0 | Visible uncertainty and confirmation; demo assumptions labeled |
| Open/resolved case only | Independent assignment, acknowledgment and resolution with expected version and notes |
| Patient details in SNS | Opaque stable alert ID and authenticated link only |
| Outreach agent/coplan/handoff in core | Template outreach; optional agent/copilot/handoff deferred |
| 30/60-min universal timers; demo advance fallback | Configurable demo policy; due index and stale timer checks; no timer substituted silently |
| SDK retries multiplied by repair | Hidden SDK retries disabled; at most two durably reserved attempts/job |
| Automatic invocation logging | Off by default; synthetic-only explicitly enabled evidence if appropriate |
| Python 3.12 copied from plan | Python 3.14 available locally and documented Lambda GA runtime; Node 24 LTS frontend |

Stage A deliberately provides an inert cloud scaffold: application endpoints reject with AUTH_NOT_CONFIGURED, workers return per-record failures, and worker mappings are disabled. It cannot accidentally accept work it cannot durably process. Browser mocks are ephemeral fixtures with no security/durability guarantee. This boundary must be removed through Stage B implementation, not an environment flag that bypasses auth.

The user selected us-east-1. No account/profile/model/Guardrail value was inferred. Pricing values are null until sourced. The current runtime/SDK package versions are locked after installation; SAM CLI is a separately recorded development dependency.
