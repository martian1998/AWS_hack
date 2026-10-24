#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from tether.api import app
from tether.models import JobEnvelope

parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
for path, document in [(ROOT / "shared/openapi.json", app.openapi()),
                       (ROOT / "shared/job.schema.json", JobEnvelope.model_json_schema())]:
    text = json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.check:
        if not path.exists() or path.read_text() != text:
            raise SystemExit(f"Contract drift: regenerate {path.relative_to(ROOT)}")
    else:
        path.write_text(text)
print("Canonical schemas synchronized." if args.check else "Exported canonical schemas.")
