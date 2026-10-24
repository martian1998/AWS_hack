# Stage A checkpoint — October 23, 2026, Pacific

**Result: local foundation verified; live AWS stages blocked.** This is the first staged checkpoint requested in the guide, not a deployed Tether application.

## What now works

The project is initialized as a Git repository on `main` and was opened in Kiro using its installed CLI. The specification, persistent steering, owner assignments, revised contracts and source reconciliation are saved. No remote repository or commit was created.

Canonical Pydantic models generate OpenAPI, the job JSON schema and TypeScript. The React/Vite/TanStack Query console provides a mock board with search, priority filters and pagination; original-language evidence; an SMS simulator; same-source replay; case assignment, acknowledgment and resolution previews; activity log and implementation status. New mock replies remain in human review. Sixty synthetic profiles span two agencies and five languages; 33 agency-A profiles match this fixture's ZIP selection.

The FastAPI/Mangum scaffold exposes only health without authentication. All 15 application operations reject missing credentials; arbitrary bearer text also grants no access. The SAM baseline includes encrypted tables/queues, DLQs, JWT configuration, retention settings and disabled queue mappings. Its inert worker reports every received record as failed, never completed.

## Commands actually run and observed results

| Command / check | Observed result |
|---|---|
| Tool version checks | Git 2.54.0; system Node 26.12.1/npm 11.20.0; AWS CLI 2.38.5; SAM 1.169.0; Python 3.14 available |
| Project-local Node install/version | Node 24.22.1 used by repository scripts; global runtime unchanged |
| Python installation + `pip check` | Dependencies installed into `.venv`; no broken requirements |
| Frontend installation | Exact versions + package lock; npm reported zero vulnerabilities at installation |
| `./scripts/seed.sh` | 60 profiles; 33 matched agency-A fixtures; no cloud writes |
| `./scripts/check.sh` | Python tests, contract synchronization, TypeScript check, mock tests, production build and SAM lint completed successfully |
| Python test suite | **39 passed**, no skipped tests in the final run; includes all 15 routes with both missing and arbitrary bearer credentials |
| OpenAPI/TypeScript drift checks | Synchronized |
| Frontend workflow tests | **4 passed**: concurrent mock replay/payload conflict, unknown reply preserves case, versioned human resolution, reconciled mock counts |
| Production frontend build | Passed on Node 24.22.1; local font assets bundled |
| `sam validate --lint --region us-east-1 --template-file infra/template.yaml` | Valid SAM template; no deployment attempted |
| `./scripts/browser-check.sh` | **2 passed** in local Chrome: desktop workflow and 390px mobile preview; desktop collected no uncaught page errors |
| `./scripts/smoke.sh local` | **32 passed** for local health, route boundaries and inert worker |
| `aws configure list-profiles` / `aws configure list` | No profiles, credentials or Region in global configuration |
| `aws sts get-caller-identity` | Failed: NoCredentials |
| `./scripts/preflight.sh` | Exit 2 as intended: approved account/profile/credentials and live service configuration absent; recorded Region us-east-1 |
| `git init -b main` | New local repository initialized; no remote/push |
| `kiro /Users/parvatihotagi/Documents/AWS_gpt` | CLI returned success opening project; Kiro's internal spec generation workflow was not run |

`stage-a-checks.txt` preserves the final local check output with terminal color sequences removed. Browser screenshots: [desktop](stage-a-desktop.png), [mobile](stage-a-mobile.png). The preview runs at `http://127.0.0.1:5173` while its local server is active; restart with `./scripts/dev.sh` if needed.

## Findings fixed during this checkpoint

- An initial route-test discovery method produced an empty parameter list with the installed FastAPI version. Tests now enumerate canonical OpenAPI operations and assert all 15 are covered; the final suite has no skips.
- Mobile browser testing detected document-level horizontal overflow. Constrained grid children and the table's positioned scroll container fixed it; the table itself remains horizontally scrollable on small screens.
- SAM initially warned that its global metadata directory was sandbox-protected. Repository scripts now use a project-local ignored SAM metadata directory; final lint completed without that error.
- TypeScript was pinned to 5.9.3 to match the OpenAPI generator's supported peer range. Fonts are bundled locally instead of fetched from Google at runtime.
- Fixture patient state counts were reconciled, and only the featured patient is seeded as escalated with an active case.

Remaining non-failing warnings: the installed Starlette TestClient warns about future migration from httpx to httpx2; Vite reports dependency `use client` directives while building this client-only SPA. Browser checks passed. These warnings are retained in the evidence log, not silently suppressed.

## Live / mock / unimplemented

| Category | Status |
|---|---|
| Local code | Contracts, fixtures, UI, fail-closed API, tooling and validation executed |
| Mock only | Patient data, triage fixture, source replay, case controls, audit and job ledger; browser memory resets on refresh |
| Real AWS | **None deployed or invoked successfully**; no real model call, Guardrail evaluation, notification or email arrival |
| Planned Stage B–D | Live identity/membership, durable transactions, stream outbox/dispatch/recovery, real workers, model triage, SNS, notice/outreach, human authorization, follow-ups, shared quotas/budgets |
| Planned Stage E | Original gold-set evaluation, measured load/cost/performance, video recording and verified upload |

Browser tests are not evidence of AWS concurrency, durability or tenant isolation. The API tests establish only that the scaffold refuses access. SAM validation establishes template validity, not deploy permission or resource existence. No delivery, latency benchmark, clinical-quality or utility-scale result is claimed.

## Blockers and next checkpoint

See [blockers](../blockers.md) for the observed access/configuration gaps and missing original sources. Configure credentials locally through the organizer's approved route and fill ignored `infra/target.local.json`; never paste keys into chat. P2 remains the sole deployment owner. Use Prompt B after reviewing the canonical contracts. The Stage B checkpoint requires a real durably accepted Spanish reply, real model metadata, visible case, replay without duplicate case and team-confirmed email arrival.

All contract changes from the original plan are enumerated in [decisions](../decisions.md). This checkpoint does not assert team approval or silently freeze a changed contract.
