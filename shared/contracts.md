# Canonical API contract v1

Authority: `backend/tether/models.py` and typed routes in `backend/tether/api.py`. Generated artifacts: `openapi.json`, `job.schema.json`, `frontend/src/generated/api.ts`. Run `scripts/contracts.sh`; drift is checked by `scripts/check.sh`. Example fixtures are validated by Pydantic in `scripts/seed.py`. All IDs/examples below are synthetic.

## Routes and authorization

| Method/path | Input | Result | Boundary |
|---|---|---|---|
| GET /health | — | 200 `{ok:true}` | Public, no configuration |
| POST /events | CreateEvent + Idempotency-Key | 202 Accepted | coordinator |
| POST /events/{event_id}/confirm | ConfirmEvent with expected_version | 200 OutageEvent | coordinator |
| POST /events/{event_id}/outreach | OutreachRequest + Idempotency-Key | 202 Accepted | coordinator, confirmed active event |
| POST /inbound | InboundRequest, stable source_message_id | 202 Accepted | patient/event session; tenant derived server-side |
| GET /jobs/{job_id} | — | 200 Job | tenant staff or exact owning patient session |
| GET /events/{event_id}/board | limit, cursor | 200 Board | tenant viewer/coordinator |
| GET /patients/{patient_id}/thread | event_id, limit, cursor | 200 Thread | tenant viewer/coordinator |
| GET /phone/{patient_id}/messages | event_id, limit, cursor | 200 Page[Message] | exact patient/event session |
| POST /simulator/sessions | CreateSession | 201 SimulatorSession | coordinator, expires in 15 minutes |
| GET /events/{event_id}/escalations | limit, cursor | 200 Page[Escalation] | tenant viewer/coordinator |
| POST /escalations/{case_id}/assign | assigned_to, expected_version | 200 Escalation | coordinator; assignee must be same-tenant staff |
| POST /escalations/{case_id}/acknowledge | expected_version | 200 Escalation | coordinator |
| POST /escalations/{case_id}/resolve | expected_version, notes | 200 Escalation | coordinator; acknowledged case |
| GET /events/{event_id}/audit | limit, cursor | 200 Page[AuditEntry] | tenant viewer/coordinator |
| GET /operations | event_id | 200 Operations | tenant viewer/coordinator |

Every app route currently fails closed in the Stage A API scaffold: no credential -> 401; a supplied bearer credential -> 503 AUTH_NOT_CONFIGURED. A bearer string is not validated in Stage A and grants no access. No public Swagger/OpenAPI route or admin reset/fault route exists. The browser adapter is deliberately independent and labeled MOCK. Live JWT/session authorization and data adapters are Stage B.

## Examples

Inbound request:
```json
{"event_id":"E-001","patient_id":"P-0001","source_message_id":"source-001","language":"es","text":"No puedo respirar. Mi máquina se apagó."}
```

After a successful live atomic transaction (not yet implemented):
```json
{"job_id":"job-001","resource_id":"message-001","state":"ACCEPTED","status_url":"/jobs/job-001","duplicate":false}
```

Same identity/same payload returns original IDs, current job state and duplicate=true. A new message must have a new source_message_id. A failed request retries with the same identity; different payload with that identity:
```json
{"error":{"code":"IDEMPOTENCY_CONFLICT","message":"This source identity was already used with a different payload.","retryable":false,"correlation_id":"corr-001"}}
```

Job envelope (queue contains references only):
```json
{"schema_version":1,"job_id":"job-001","kind":"triage","tenant_id":"agency-a","event_id":"E-001","event_version":1,"patient_id":"P-0001","source_message_id":"source-001","created_at":"2026-10-24T03:00:00Z","deadline_at":"2026-10-24T03:05:00Z","correlation_id":"corr-001","payload_ref":"records://agency-a/message-001"}
```

Human resolution:
```json
{"expected_version":2,"notes":"Synthetic demonstration: coordinator completed the handoff."}
```

Unknown finding:
```json
{"patient_reported_safe":"unknown","emergency":"unknown","device_running":null,"backup_hours_left":null,"needs":[],"english_translation":"","evidence_quotes":[],"confidence":0}
```

Pagination uses limit 1–50 (default 20), next_cursor=null at the end, and observed_at. Cursors are opaque, scoped, signed and expiring in the planned live adapter. Errors have code/message/retryable/correlation_id; no request-text echoes. 401 missing/invalid identity, 403 same-tenant forbidden role, 404 inaccessible object, 409 conflict/version mismatch, 422 invalid contract, 503 retryable service unavailable. Limits reject input before acceptance. Completed triage is distinct from human acknowledgment and resolution.
