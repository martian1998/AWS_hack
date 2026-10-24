# Runbook

## Current checkpoint

Use `SETUP.md` to start the mock UI and run local checks. Region is us-east-1; approved account/profile are not configured. All app API routes fail closed and queue consumers are disabled. `deploy.sh`, `eval.sh` and `load.sh` deliberately stop with reasons. No live work exists to redrive. Closing the local preview discards only its mock browser state.

## Stage B deployment gate

P2 alone deploys. Confirm expected account via STS, exact profile and Region; name every resource with the verified `tether-` stack prefix. Get organizer-approved identity/model/Guardrail/IAM configuration; do not loosen auth if permissions fail. Implement and pass the atomic-intake/identity tests, replace the inert worker, enable only implemented mappings, grant resource-scoped IAM, and then replace the deploy gate with the reviewed SAM build/deploy command. Run `sam build --template-file infra/template.yaml` (container build requires Docker if local runtime packaging differs) and inspect its changeset before execution. Do not deploy Stage A and call it the patient flow.

Required Stage B smoke: authenticate a patient-scoped synthetic session; submit one Spanish reply; record 202/job; observe committed message/outbox/job; observe real Converse and Guardrail metadata; observe case/SNS publish; have the team confirm email arrival; replay same source ID and prove no new case; disable model and retain urgent case. Capture sanitized IDs, safe codes, timestamps and actual usage, never tokens/conversation logs.

## Planned recovery procedures (implement and exercise in Stage D)

| Signal | Operator action |
|---|---|
| Pending outbox age | Query due index by tenant/lane/shard. Verify committed job, repair dispatcher permission/outage, republish stable envelope, then conditionally checkpoint. Expect duplicates after publish crash. |
| Expired worker lease | Read current job and attempt reservation; acquire new fencing version; preserve unknown-call usage reservation; retry only within attempts/deadline. |
| DLQ | Inspect safe job ID/error code. Reconcile FAILED_VISIBLE before replay; fix cause; verify idempotency retention window; authorized replay links a new job to original. Never delete an unaccounted job. |
| Model throttled/unavailable/budget full | Keep urgent deterministic lane active. Bound retry; route to human review with original message retained. Do not switch to untested model. |
| SNS publish retry | Track stable alert ID/publish attempts. Verify subscription. Duplication at the external boundary is possible; publish is not receipt or human acknowledgment. |
| Unacknowledged urgent case | Follow agency demo policy through human contact; alarm independent of model. Assign/acknowledge explicitly. |
| Stale follow-up | Recheck event version/cancellation, latest reply and contact attempt before acting. TTL deletion is never the timer. |

## Rollback and cleanup

Keep schema-v1 consumers compatible across deployments and retain tables/queues while jobs are pending. Before rollback, stop new optional fan-out, record counts and outbox/lease state; do not disable urgent intake without a human fallback plan. Redeploy the last tested function version and reconcile work. SAM tables use Retain; code rollback must not delete accepted work.

No deployment exists now. Future cleanup requires verified account/profile/Region and an inventory limited to the Tether stack; reconcile/drain or deliberately archive pending work first, then use the stack deletion path. Retained DynamoDB data and hosting/log assets need separate explicit cleanup decisions. Never delete unrelated team resources. Disable external subscriptions/hosting only as part of that reviewed inventory.

Single Region, connectivity, provider throughput and human staffing remain limits. No failover/offline delivery guarantee. Demo clock/reset/fault tools are not implemented; any later implementation requires demo environment + demo_admin and injected adapters.
