# Evaluation checkpoint

No live evaluation has run. The original plan specifies 30 labeled replies (10 EN, 8 ES, 6 VI, 6 ZH), including 6 emergencies, 6 ambiguous replies and 2 injections, but does not include their text/labels. Preserve that original set when provided; do not replace it with invented originals. The UI fixture is not an evaluation result.

P1/P4 will add independent safety regressions for negation, quoted emergencies, indirect phrasing, typos, prompt attacks, distress allowed through Guardrails, treatment-advice blocking, unknown backup/device fields, model timeout/refusal/invalid JSON and older-safe/newer-emergency ordering. Add TL cases separately before making language-quality claims.

Report emergency recall as numerator/denominator, false positives, human-review counts, language misses, validated quote failures, actual model calls/tokens and mode. Default live cap is five calls; a full set requires an explicit larger bounded run. Record per-case outcomes and preserve misses. No clinical-validation claim.
