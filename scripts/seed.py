#!/usr/bin/env python3
"""Deterministically generate synthetic local fixtures; never writes to AWS."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from tether.models import Board, Escalation, Message, Patient, Thread, Triage

stamp = "2026-10-24T03:00:00Z"
names = ["Sofia Martinez", "Minh Tran", "Evelyn Chen", "Rosa Santos", "James Reed", "Linh Nguyen", "Elena Cruz", "Daniel Wu", "Ana Reyes", "Owen Brooks", "Maya Patel", "Luis Vega"]
languages = ["es", "vi", "zh", "tl", "en", "vi", "es", "zh", "tl", "en", "en", "es"]
device_types = ["oxygen_concentrator", "ventilator", "cpap", "bipap", "feeding_pump", "suction", "refrigeration", "wheelchair"]
patients = []
for i in range(60):
    patients.append(Patient.model_validate({
        "patient_id": f"P-{i + 1:04}", "tenant_id": "agency-a" if i < 40 else "agency-b",
        "display_name": names[i % len(names)] + (f" {i // 12 + 1}" if i >= 12 else ""),
        "language": languages[i % len(languages)],
        "address": {"city": "San Jose", "zip": ["95116", "95122", "95127"][i % 3] if i % 5 else "95035"},
        "contact": {"type": "none" if i % 13 == 12 else "caregiver" if i % 7 == 6 else "self", "caregiver_name": "Demo caregiver" if i % 7 == 6 else None},
        "devices": [{"type": device_types[i % 8], "backup_hours": None if i % 9 == 8 else [2, 4, 8, 12, 24][i % 5], "backup_tank": False if i % 8 == 0 else None}],
        "lives_alone": i % 3 == 0, "mobility_limited": i % 4 == 0,
    }).model_dump(mode="json"))
# Keep the featured Spanish fixture inside the matched area.
patients[0]["address"]["zip"] = "95127"
event = {"event_id": "E-001", "tenant_id": "agency-a", "version": 1,
         "utility": "Bay Valley Electric (fictional)",
         "areas": [{"name": "East San Jose", "zips": ["95116", "95122", "95127"], "confident": True}],
         "flagged_areas": ["Foothill communities — exact area unconfirmed"],
         "start": "2026-10-23T20:00:00-07:00", "est_restore": None,
         "confidence": 0.72, "is_cancellation": False,
         "status": "needs_confirmation", "outage_hours": None}
rows = []
statuses = ["escalated", "awaiting_reply", "human_review", "needs_help", "reported_safe", "not_contacted"]
for i, p in enumerate(patients):
    if p["tenant_id"] != "agency-a" or p["address"]["zip"] not in event["areas"][0]["zips"]:
        continue
    backup = p["devices"][0]["backup_hours"]
    rows.append({"patient": p, "tier": "CRITICAL" if i < 2 else "HIGH" if i < 12 else "MEDIUM",
                 "score": 6.0 if i < 2 else 4.0 if i < 12 else 2.0,
                 "reasons": [f"{backup}h documented backup" if backup is not None else "Backup duration unknown",
                             "Lives alone" if p["lives_alone"] else "Contact information available"],
                 "uncertainties": ["Restoration time unknown"],
                 "status": "needs_help" if i > 0 and statuses[i % 6] == "escalated" else statuses[i % 6]})
counts = {s: sum(r["status"] == s for r in rows) for s in statuses}
board = Board.model_validate({"event": event, "patients": {"items": rows, "next_cursor": None, "observed_at": stamp}, "total_affected": len(rows), "counts": counts, "mode": "MOCK"})
triage = Triage.model_validate({"patient_reported_safe": "no", "emergency": "yes", "device_running": False,
                               "backup_hours_left": None, "needs": [],
                               "english_translation": "I can't breathe. My machine turned off.",
                               "evidence_quotes": ["No puedo respirar", "Mi máquina se apagó"], "confidence": 0.94})
incoming = "No puedo respirar. Mi máquina se apagó."
triage.validate_evidence(incoming)
case = Escalation.model_validate({"case_id": "C-001", "event_id": "E-001", "patient_id": "P-0001", "tier": "CRITICAL",
                                 "reason": "Fixture: patient reports breathing difficulty and a stopped device.", "evidence_quotes": triage.evidence_quotes,
                                 "state": "OPEN", "version": 1, "assigned_to": None, "created_at": stamp,
                                 "acknowledged_at": None, "resolved_at": None, "resolved_by": None, "notes": None})
messages = [Message.model_validate({"message_id": "M-001", "source_message_id": "S-001", "patient_id": "P-0001", "event_id": "E-001", "direction": "out",
                                    "text": "Hola Sofia. Este es un mensaje de demostración de su equipo de atención. Responda 1 para confirmar o 2 para pedir ayuda.",
                                    "language": "es", "created_at": stamp, "sequence": 1, "triage": None, "processing_state": "SUCCEEDED", "delivery": "sent", "mode": "MOCK"}),
            Message.model_validate({"message_id": "M-002", "source_message_id": "S-002", "patient_id": "P-0001", "event_id": "E-001", "direction": "in",
                                    "text": incoming, "language": "es", "created_at": stamp, "sequence": 2, "triage": triage, "processing_state": "SUCCEEDED", "delivery": "acknowledged", "mode": "MOCK"})]
thread = Thread(patient=patients[0], messages={"items": messages, "next_cursor": None, "observed_at": stamp}, cases=[case])
fixtures = {"board": board.model_dump(mode="json"), "thread": thread.model_dump(mode="json")}
for path, obj in [(ROOT / "data/patients.json", patients), (ROOT / "data/mock.json", fixtures)]:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
print(f"Generated {len(patients)} synthetic profiles; {len(rows)} matched agency-a fixtures. No AWS writes.")
