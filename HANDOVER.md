# Tether handover — Friday, October 23, 2026 (evening, Pacific)

Written for the teammate taking over. Everything under "Where things stand" was observed in this repository tonight. Sections marked **Suggested** are plans, not finished work.

Read first: `.kiro/steering/tether.md` (project rules), `docs/decisions.md`, `docs/evidence/stage-a.md`, `docs/blockers.md`.

## 1. Where things stand

| Area | State |
|---|---|
| Stage A (local foundation) | Done and verified locally. Evidence in `docs/evidence/stage-a.md`: 39 Python tests, 4 frontend tests, 2 browser checks, 32 local smoke tests, SAM lint. |
| ChatGPT's partial Stage B | `backend/tether/store.py`, `policy.py`, `config.py` and `errors.py` were edited at 20:50, after the Stage A evidence was written. They are not wired into `api.py` and have no tests. Treat them as an unreviewed draft. |
| API | Only `GET /health` works. The 15 application routes reject everything (401 without a credential, 503 with any bearer token). |
| AWS | Nothing deployed. On this Mac there are no AWS profiles, `aws sts get-caller-identity` fails with NoCredentials, and `infra/target.local.json` does not exist. No Bedrock call, Guardrail check or SNS email has happened. |
| Kiro spec | `.kiro/specs/tether-core/` has requirements.md, design.md and tasks.md, but they are not in Kiro's format. Kiro's task runner finds 0 tasks in tasks.md. tasks.md is unchanged (still ChatGPT's owner table). |
| Git | Branch `main`, no commits, **no remote**. The baseline files are staged but not committed, because `git config user.name` / `user.email` are not set on this Mac. |
| Docker | Not installed (matters for `sam build`, see section 5). |

Two Kiro runs tonight tried to rewrite tasks.md into Kiro's format. Both were aborted and changed no files.

## 2. First steps for the new owner

1. **Get the code.** There is no remote yet. On this Mac:
   ```bash
   git config user.name "Your Name"
   git config user.email "you@example.com"
   git commit -m "Stage A baseline plus ChatGPT's partial Stage B draft"
   git remote add origin <team repo URL>
   git push -u origin main
   ```
   Do not copy `.venv/`, `.tools/`, `node_modules/` or any `*.local.json`. On a new machine run `./scripts/setup.sh` (see SETUP.md).
2. Run `./scripts/check.sh`. It has not been re-run since ChatGPT's 20:50 edits. Because those modules have no tests, a pass says little about them.
3. Start the AWS access steps in section 4 right away. They gate every live stage.

## 3. Suggested plan: local-first, then deploy

The user chose tonight to build the Stage B–C main flow locally first, schedule the AWS coding work in the first batch, and commit the baseline first.

The same code should run locally and deployed:

- **Storage:** `SQLiteStore` locally (a development adapter, never AWS evidence) and `DynamoStore` when deployed, behind the same `Transaction` interface. Both already exist in store.py.
- **Dispatch:** locally, a poller over the pending-outbox due index replaces DynamoDB Streams and SQS. Both paths call the same lane handlers.
- **Model:** Bedrock Converse plus the published Guardrail when deployed; a deterministic stub locally, always labeled MOCK.
- **Notifications:** SNS when deployed; a local stub that records alert IDs only.
- **Identity:** the backend always verifies JWT signatures against a JWKS. Locally the issuer is a loopback-only development OIDC server under `scripts/` that is never deployed. No setting may bypass authentication.

Suggested order. Tasks in the same wave touch different files, so they can run in parallel:

| Wave | Task | Owner | Main files |
|---|---|---|---|
| 0 | Tests and fixes for the transaction store (SQLite + DynamoDB via botocore Stubber) | P2 | store.py, tests/test_store.py |
| 0 | Tests and fixes for keyword/ranking policy | P2 | policy.py, tests/test_policy.py |
| 0 | Wiring: move routes into `backend/tether/routes/` without changing the OpenAPI output, add `deps.py`, all Stage B settings, DomainError handler, pin PyJWT + cryptography, add `model_usage` to the Job contract and regenerate types | P2 | api.py, routes/, deps.py, config.py, models.py |
| 0 | Key layout and shared record shapes from the design's table section | P2 | keys.py |
| 0 | SAM template for the Stage B slice | P2 | infra/template.yaml |
| 0 | Deploy script that refuses the wrong account and asks for confirmation | P2 | scripts/deploy.py |
| 0 | Frontend PKCE sign-in module (tokens in memory only) | P3 | frontend/src/auth.ts |
| 1 | JWT validation, membership lookup, patient-session validator | P2 | identity.py |
| 1 | Local development OIDC issuer | P2 | scripts/local_issuer.py |
| 1 | Bedrock model adapter and MOCK stub | P1 | backend/tether/ai/ |
| 1 | Seed synthetic data and staff memberships into the store | P4 | scripts/seed.py |
| 1 | Frontend live API adapter | P3 | frontend/src/live.ts |
| 2 | Simulator session issuance | P2 | routes/sessions.py |
| 2 | Atomic `POST /inbound`, including the keyword-emergency case | P2 | intake.py, incidents.py |
| 2 | Job, thread and phone reads with a signed cursor | P2 | reads.py, cursor.py |
| 2 | SNS notifier and urgent-lane worker | P2 | notify.py |
| 2 | App.tsx switches between mock and live adapters and shows the real mode | P3 | App.tsx |
| 3 | Fenced triage worker (leases, at most 2 model attempts, run cap) | P2 + P1 | worker.py, jobs.py |
| 3 | Outbox dispatcher and local poller | P2 | dispatch.py |
| 3 | Case assign/acknowledge/resolve, escalation and audit routes | P2 | cases.py |
| 3 | Board read from seeded status rows | P2 | board.py |
| 4 | Deployed smoke script | P4 | scripts/smoke_deployed.py |
| 4 | Local end-to-end flow test | P4 | tests/test_flow_local.py |
| 5 | Checkpoint: `./scripts/check.sh`, record results in `docs/evidence/stage-b-local.md` | all | |
| Optional, last | Notice extraction, confirm/match/rank, template outreach, scheduled reconciler, Amplify hosting, full authorization matrix | | |

Keep these handler names identical in the SAM template and the code: `tether.api.handler`, `tether.dispatch.handler`, `tether.worker.triage_handler`, `tether.notify.urgent_handler`. Keep the inert `tether.worker.handler` for the outreach lane, which stays disabled.

## 4. Manual AWS steps (P2, start now)

1. Sign in through the organizer-approved SSO/profile: `aws sso login --profile <approved-profile>`. Never paste keys into chat or files, and do not create an IAM user to work around restrictions.
2. `cp infra/target.example.json infra/target.local.json` (git ignores it). Fill in profile, expected_account_id, model_id or inference-profile ID, guardrail_id, guardrail_version (the published number), staff_issuer and staff_client_id (or let the stack create Cognito), frontend_origin and sns_topic_arn.
3. Run `./scripts/preflight.sh` (read-only). Then run `./scripts/preflight.sh --live-model`, which makes one bounded Converse call and one Guardrail check and may cost a few cents.
4. After the deploy script exists and the local checks pass, run `./scripts/deploy.sh` and confirm the account and stack name. Confirm the SNS subscription email.
5. Seed the deployed tables and run the deployed smoke test. A person must confirm the alert email actually arrived. Record only observed results in `docs/evidence/stage-b.md`.

## 5. Problems found while reviewing (not yet tested)

I found these by reading the code and template tonight. Verify each before relying on it.

- **DynamoStore.query, first page:** with the default `after=""` it sends `SK > ""`. DynamoDB rejects empty-string key attribute values, so first-page queries will likely fail. Omit the sort-key condition when `after` is empty.
- **SQLiteStore connections:** `with self.connect() as con:` commits or rolls back but never closes the connection.
- **Keyword matching:** `policy.emergency_evidence` does not normalize Unicode, so Vietnamese typed in decomposed form (NFD) will not match. Normalize to NFC and casefold first. Typos such as "cant breath" are not matched; test and document them as known misses.
- **Cognito tokens:** access tokens carry `client_id`, not `aud`. The backend check must accept `client_id` (the API Gateway JWT authorizer already does).
- **Cognito scopes:** the custom scopes `tether/read` and `tether/write` only appear in tokens from Cognito's OAuth2 endpoints, not from USER_PASSWORD_AUTH. A scripted smoke test therefore needs a loopback Authorization Code + PKCE sign-in in the browser.
- **Alarm topic encryption:** `AlertTopic` uses `alias/aws/sns`. CloudWatch alarms cannot publish to a topic encrypted with the AWS-managed SNS key, so the DLQ alarms would not deliver. Use a customer-managed KMS key whose policy allows CloudWatch.
- **No Docker:** `sam build` without a container needs `python3.14` on PATH. Check that pydantic_core and cryptography end up as Linux arm64 wheels in the build output.
- **Artifact bucket:** `sam deploy --resolve-s3` creates a non-Tether stack (`aws-sam-cli-managed-default`). The steering allows only Tether-prefixed resources, so use a Tether-named, encrypted, non-public bucket.
- **Timeout budget:** functions time out at 30 s and the design allows 2 model attempts per job. Two slow Bedrock calls may not fit. Either make one attempt per invocation and retry with a short SQS visibility change, or raise the timeout and the visibility timeout together (visibility must be at least 6 × timeout + batching window).
- **Audit immutability:** IAM "PutItem only" cannot stop a PutItem from overwriting an entry. Overwrite protection comes from the conditional write in code; document that limit.
- **Lambda runtime:** confirm `python3.14` is available in us-east-1 before deploying.

## 6. Tests that prove the core requirements

- **R03:** inject a commit failure; expect 503 and no message, job or case rows.
- **R04:** same source ID and payload returns the original job with `duplicate=true`; a changed payload returns 409; concurrent replay produces one message and one case.
- **R05:** a keyword emergency creates a case inside the intake transaction, visible with the model disabled.
- **R08:** refusal, timeout or invalid model output ends in HUMAN_REVIEW after at most 2 metered attempts; evidence quotes must occur in the original text.
- **R09:** a later safe or ambiguous reply never closes or downgrades a case.
- **R10:** only a coordinator can assign, acknowledge or resolve; resolve needs a prior acknowledgment, notes and the current version (stale version → 409); patient tokens cannot read staff views.
- **R11:** on every route, a missing or invalid credential → 401, an insufficient same-tenant role → 403, another tenant's or patient's IDs → 404.
- **R12:** SNS messages contain no patient name or message text; logs contain IDs and error codes only.

## 7. Notes on using Kiro

- Kiro's task runner needs tasks.md in this shape: `# Implementation Plan: tether-core`, `## Overview`, `## Tasks` with checkbox items (`- [ ] 2.` and `- [ ] 2.1`, optional sub-tasks written `- [ ]* 2.2`), `## Notes`, and `## Task Dependency Graph` containing a json code block such as `{"waves": [{"id": 0, "tasks": ["2.1", "2.2"]}, {"id": 1, "tasks": ["4.1"]}]}`.
- A wave starts only after every task in all earlier waves is complete. Put optional tasks in the last waves or they will block required ones. A checkpoint task left out of the graph is moved to the very end.
- To regenerate tasks.md, ask Kiro to update the tether-core tasks. Kiro's design-first spec workflow has a separate "tasks" phase; tonight's runs started the workflow without choosing that phase, which may be why they stalled.
- requirements.md and design.md also fail Kiro's format check (missing standard headings). That does not block running tasks; converting them is optional.

## 8. Deadline and owners

Hard stop **Saturday, October 24, 2026, 11:00 AM Pacific**; team target 10:30 AM. That includes recording and uploading a video of up to five minutes. Protect the main flow and drop optional items first. If AWS access never arrives, the local stack (SQLite, stub model, local issuer) can still be shown, labeled MOCK.

Owners: P1 AI, P2 backend/cloud and the only person who deploys, P3 frontend, P4 data and evidence. Synthetic data only; no clinical claims.
