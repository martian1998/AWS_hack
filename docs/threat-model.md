# Threat model and test matrix

Assets: synthetic patient records/conversations, staff identity and tenant memberships, case decisions, job/audit ledger, deployment credentials, model budget. Trust boundaries: browser → API auth; patient session → exact patient/event; validated subject → trusted membership; untrusted notice/reply → model; durable database → at-least-once queue; app → external email.

| Threat | Required mitigation | Evidence/state |
|---|---|---|
| Forged tenant/role/body identity | Derive from validated subject + server membership; forbid authority fields in input | Contract forbids fields; live membership Stage B |
| Other-tenant patient/job/case/metrics IDs | Scope every lookup/query/cursor; 404 without existence leak | Live matrix Stage B/D |
| Patient token used for staff read/resolve | Distinct short-lived scopes/validator; no token in URL/log/storage | Design only; live regression pending |
| Arbitrary bearer bypass | No insecure fallback | All scaffold routes reject supplied bearer with 503 |
| Replay/concurrent redelivery | Durable namespace + digest, transaction, case generation pointer, fenced completion | Browser preview test only; live Stage B/D |
| Prompt attack closes case or changes tool/tenant | Model extracts findings only; no resolve/database/network tools; human endpoint with version | No live model; schema checks and preview regressions |
| Model refuses/blocks distress | Deterministic keyword escalation before AI; preserve message and critical evidence | Live Stage B/D pending |
| Old safe result overwrites newer emergency | Sequence guard, append evidence, independent active case | Design; live regression pending |
| Unlimited retries/spend | Shared conservative reservation, explicit attempt ledger, SDK retries disabled | Probe has one call; distributed controls Stage D |
| Worker loss after 202 | Atomic outbox; due index; leases; partial batches; visible DLQ | Stage A never accepts cloud work; live Stage B/D |
| PHI/token leakage | No raw request logs/exception echoes; minimal SNS; no frontend secrets | Synthetic-only scaffold; deployment/log review pending |
| Untrusted HTML script injection | React text rendering, no dangerouslySetInnerHTML | Implemented UI uses text nodes |

Audit is append-oriented by application IAM, not a legally tamper-proof record: admins/retention can affect it. Stage A role grants no database access. Future policies must permit conditional PutItem audit insertion but not UpdateItem/DeleteItem, including transaction constituent actions. HTTP API has no direct WAF attachment; any future WAF design requires a supported front door or REST API alternative.
