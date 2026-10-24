# Tether — Shutoff Outreach Desk

A synthetic home-health coordination desk for Dana: notice → confirmed area → ranked outreach → multilingual reply → human case handling.

**Current checkpoint: Stage A foundation.** The React application runs in explicit browser MOCK mode. The API is a fail-closed contract scaffold. No AWS resources have been deployed, no Bedrock calls have run, and no SNS email has been sent. Region: **us-east-1**, selected by the user. Live stages await approved AWS access and implementation.

## Run locally

```bash
./scripts/setup.sh       # Node 24 LTS and Python 3.14; installs locked dependencies
./scripts/dev.sh         # http://127.0.0.1:5173
./scripts/check.sh       # schema/API tests, generated types, mock tests, build, SAM lint
./scripts/browser-check.sh # local Chrome: desktop + mobile workflow checks
```

On this machine dependencies and a project-local Node 24 runtime are already installed. The setup script is for a fresh checkout. See [SETUP.md](SETUP.md) for runtime installation, AWS login and preflight.

## What works now

- Shared [requirements](.kiro/specs/tether-core/requirements.md), [design](.kiro/specs/tether-core/design.md) and [owner tasks](.kiro/specs/tether-core/tasks.md).
- Canonical Pydantic → OpenAPI → generated TypeScript, with [contract examples](shared/contracts.md) and drift checks.
- Responsive mock board, search/priority filtering, pagination, exact-evidence thread, simulated SMS, source-ID replay, case assignment/acknowledgment/resolution previews and session activity ledger.
- 60 fictional patients, two agencies, five languages; the authored board fixture includes 33 agency-A patients in the selected ZIPs.
- A SAM baseline with encrypted tables/queues, DLQs, disabled worker mappings, a staff JWT boundary and inert application endpoints.
- Read-only preflight and an opt-in bounded Bedrock/Guardrail capability probe. It has **not** been run against a live model.

The browser's ephemeral adapter is not a durability or authorization test. Every new mock reply goes to human review; only the initial Spanish message has authored triage. Refresh clears the session. Case preview controls represent the coordinator persona and do not authenticate anyone.

## Continue in Kiro

Open this folder in Kiro. The spec lives at `.kiro/specs/tether-core/`; persistent conventions are in `.kiro/steering/tether.md`. Read [the Stage A evidence](docs/evidence/stage-a.md) and [blockers](docs/blockers.md), review the [contract changes](docs/decisions.md), then use Prompt B in `docs/Tether-Kiro-Build-Guide.txt` after configuring the approved AWS target. The files were prepared here; running Kiro's internal spec workflow is not claimed.

P1 owns AI; P2 owns backend/cloud, shared schemas and deployment; P3 owns frontend; P4 owns data/evidence/story. Use one deployment owner. No extra agents were used.

## Limits

Only synthetic data. Not for clinical use or an emergency-service replacement. Keywords cannot guarantee emergency detection. The guide's live transactions, authentication, worker leases/outbox recovery, shared budgets, follow-ups and load/evaluation evidence are **planned**, not implemented. Maps, copilot, RAG, agentic outreach, real SMS and handoff summaries are deferred.

The original plan and challenge deck are preserved under `docs/source/`. The named idea PDF and original evaluation JSONL were unavailable. Cost rates and quotas remain unknown. No clinical, customer-validation or utility-scale claims are made.
