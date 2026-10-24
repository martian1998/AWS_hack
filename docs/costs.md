# Cost model and admission limits

No live AWS or model cost was measured. `data/pricing.json` deliberately has null rates/date/model and labels excluded services. Null is unknown, not free. Region is us-east-1. Before estimating, record model/inference-profile, pricing date, source URL, currency, units and policy selection from [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/).

For known rates, model estimate = input_tokens / 1,000,000 × input_rate + output_tokens / 1,000,000 × output_rate. Keep actual usage, estimated charges and billed charges distinct. Include every model attempt/repair and conservatively charge uncertain timed-out invocations against the reservation. Guardrail input/output checks have separate policy/text-unit accounting; the probe includes an extra ApplyGuardrail call.

Required non-model line items: API Gateway requests, Lambda invocations/duration, DynamoDB reads/writes/transactions/GSIs/storage, SQS operations, EventBridge schedules, SNS email/other delivery, CloudWatch ingestion/retention/alarms, Amplify build/hosting/bandwidth, and optional SMS segments/carrier fees. Credits and taxes are separate. No precise total is published while any required price/usage item is unknown.

Planned application caps: MAX_MODEL_CALLS_PER_RUN=5 by default, MAX_MODEL_ATTEMPTS_PER_JOB=2, MAX_INPUT_SIZE=4000 for replies (12000 notices), MAX_OUTPUT_TOKENS=800, MAX_AGENT_STEPS=0 for core, SQS maximum concurrency=2 per lane initially. Live Stage D atomically reserves conservative model quota plus tenant/run calls/tokens before invocation. The one-off preflight probe is capped at one call but is not shared runtime admission control.

AWS Budget notifications may lag and do not stop spend. Application limits constrain the selected workflow, not all spend in an AWS account. No account-wide dollar cap is promised.
