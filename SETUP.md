# Setup and team handoff

Project directory: `/Users/parvatihotagi/Documents/AWS_gpt`. Use this repository, not a replacement `~/Projects/tether` directory.

## Tools

Observed: Git 2.54.0, system Node 26.12.1/npm 11.20.0, Python 3.14 and 3.15, AWS CLI 2.38.5, SAM CLI 1.169.0. This project uses Python 3.14 and Node 24 LTS. A project-local Node **24.22.1** is installed under `.tools/node/`, and `scripts/env.sh` selects it without changing system tools. `.venv` contains the locked Python packages. Node package versions are exact in `frontend/package.json` and `package-lock.json`; transitive Python versions are in `requirements-dev.lock` and runtime-only `backend/requirements.txt`.

For another Mac, install compatible runtimes with your preferred approved package manager; for Homebrew:

```bash
brew install node@24 python@3.14 awscli aws-sam-cli
export PATH="$(brew --prefix node@24)/bin:$PATH"
./scripts/setup.sh
```

Alternatively install a project-local Node 24 runtime with `npm install --prefix .tools/node --save-exact node@24.22.1`. This changes only the ignored tool directory. Verify `node --version` after sourcing `scripts/env.sh`. Python 3.15 is not the selected Lambda runtime. Runtime references checked October 23, 2026: [Node release status](https://nodejs.org/en/about/previous-releases), [Lambda runtimes](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html).

## Commands

| Purpose | Command | Current behavior |
|---|---|---|
| Install | `./scripts/setup.sh` | Local locked install, types and fixtures |
| Console | `./scripts/dev.sh` | Browser mock on loopback port 5173 |
| API skeleton | `./scripts/dev-api.sh` | Loopback port 8000; health 200, app routes reject |
| Generate contracts | `./scripts/contracts.sh` | Python → OpenAPI/JSON schema → TypeScript |
| Checks | `./scripts/check.sh` | Python + frontend tests, drift, build, SAM lint |
| Browser | `./scripts/browser-check.sh` | Installed Google Chrome; no AWS calls |
| Local seed | `./scripts/seed.sh` | Rewrites deterministic synthetic JSON only |
| Preflight | `./scripts/preflight.sh` | Read-only AWS checks; exit 2 lists blockers |
| Model probe | `./scripts/preflight.sh --live-model` | Explicitly opts into at most one Converse call (800 output tokens) and one extra output Guardrail check; no repairs |
| Smoke | `./scripts/smoke.sh local` | Local health/fail-closed boundary tests |
| Deploy | `./scripts/deploy.sh` | Stops: live Stage B not implemented |
| Evaluation | `./scripts/eval.sh` | Stops: original labels/live adapter absent |
| Load | `./scripts/load.sh` | Stops: durable intake/shared caps absent |
| Cleanup | `./scripts/cleanup.sh` | Reports no deployment; does not delete resources |

Do not treat gated scripts as implemented live flows. Their gates make the remaining work explicit. Tests use loopback and synthetic fixtures, not AWS security/durability evidence. The browser check requires Google Chrome; change its `channel` only for an installed supported browser.

## Configure the approved AWS target locally

1. Use the organizer's team account and temporary credential/SSO process. Never paste credentials into chat or source. If they supply IAM Identity Center, configure the approved SSO profile and sign in using `aws sso login --profile <approved-profile>`. Do not create a new IAM user to bypass organizer restrictions.
2. Copy `infra/target.example.json` to ignored `infra/target.local.json`. Region is already `us-east-1`. Fill the approved profile/account, exact model or inference-profile ID, Guardrail ID and **published numeric version**, public OIDC client/issuer, future HTTPS frontend origin, and team SNS topic ARN. Never put secrets in this JSON or VITE variables.
3. Run `./scripts/preflight.sh`. It checks local credentials and STS identity before any other AWS request, rejects account mismatch, and prints safe error codes instead of raw payloads. The report is ignored at `docs/evidence/preflight.local.json`.
4. Once model/Guardrail access is configured, explicitly run `--live-model`. Catalog presence is insufficient. This opt-in probe may incur small charges and is not the future shared-budget enforcement mechanism. Verify actual quotas and IAM deployment permissions with the organizer; do not guess them.
5. P2 implements/deploys Stage B only after the target is correct. P1 proves a real model response; the team separately confirms actual SNS email arrival. A confirmed subscription alone does not prove delivery.

No preflight output currently establishes deployed resources, model access, quotas or email delivery. See [blockers](docs/blockers.md).
