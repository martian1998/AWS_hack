# Capacity worksheet — hypothetical, not tested

The requested scenario is **1,000,000 registered / 100,000 affected / 20,000 replies in 10 minutes**. No such test has run. Actual account/model quotas and measured service times are unknown.

| Quantity | Derivation | Interpretation |
|---|---|---|
| Registry | 1,000,000 profiles | Storage/index size, not request rate |
| Average reply ingress | 20,000 / 600 = 33.33 replies/s | Must separately size bursts and gateway rejection; a queue cannot rescue rejected requests |
| Outreach child jobs | ceil(100,000 / 5) = 20,000 | Bounded fan-out, continuation cursor and event version |
| Model rate if every reply is free text | 2,000 calls/min before retries | Requires measured RPM, not just API throughput |
| Illustrative token rate | 2,000 × (500 input + 300 output) = 1,600,000 tokens/min | Assumption only; selected model may weight output quota differently |
| Illustrative model concurrency | 33.33 × 3-second service time ≈ 100 | 3 seconds is an assumption, not a result |
| Illustrative drain at 60 calls/min | 20,000 / 60 ≈ 333.3 minutes | Assumed quota; increasing Lambda concurrency alone does not fix it |
| Illustrative staff load | 5% × 20,000 = 1,000 cases; 10 minutes/case = 166.7 staff-hours | Assumed case fraction/time; humans may be the bottleneck |

Use sustainable throughput `min(ingress accepted rate, worker concurrency / measured service time, model RPM / 60, model TPM / measured quota tokens, shared budget admission, external-provider rate)`. Model queue-drain time includes backlog and retries. Deterministic triage/explicit codes and templates should reduce required model work without treating acknowledgments as clinical clearance. Urgent deterministic case creation is independent of model quota.

Measure intake p50/p95, completion p50/p95, queue age, accepted unique counts, terminal states and staff acknowledgment separately. Eight event shards and two worker concurrency in the baseline are conservative starting assumptions. No claim that on-demand/serverless equals unlimited. Multiple gateways do not multiply shared account/Region quotas. Stage E begins with a small controlled run, at most five live model calls by default; record mocks and replay separately.
