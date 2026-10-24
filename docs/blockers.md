# Observed blockers — October 23, 2026, Pacific

The user selected **us-east-1**. Read-only `aws configure list-profiles` returned no profiles; `aws configure list` showed no credentials/Region; `aws sts get-caller-identity` failed with `NoCredentials`. The project preflight repeated the missing-credential finding. The Region is recorded in the project configuration example, not silently written to the user's global AWS config.

| Blocker | Required action / owner |
|---|---|
| No approved account ID/profile/credentials | P2: use organizer login locally and fill ignored target config; no secrets in chat |
| Model/inference profile unselected, invocation untested | P1: identify permitted model in us-east-1 and run bounded tool-use/schema/Spanish probe |
| Guardrail absent/unverified | P1: create/use approved Guardrail, publish version; verify treatment-advice blocking and distress capture |
| Staff identity issuer/client and trusted membership unavailable | P2: configure Cognito/OIDC or organizer-approved provider; implement PKCE and tenant roles |
| Patient-scoped credentials not implemented | P2: issue short-lived opaque session, server validate patient/event scope |
| SNS topic/subscription/arrival unverified | P2 + team: confirm approved email subscription, then observe live flow delivery |
| Deploy permissions and model/account quotas unknown | P2: obtain approved resource route/permissions and inspect actual quotas |
| Original idea PDF and original 30-case gold JSONL absent | P4: add actual originals; keep new regressions separate |
| Stage B–E runtime features not implemented | Follow the owner tasks and stage gates; no live UI toggle exists yet |

Installed tools are present. Network and loopback operations needed sandbox escalation during setup/testing; those are execution permissions, separate from AWS access. No AWS deployment attempt was made.
