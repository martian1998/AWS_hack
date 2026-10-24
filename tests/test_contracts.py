import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from tether.models import Board, ConfirmEvent, InboundRequest, JobEnvelope, Patient, ResolveCase, Thread, Triage

ROOT = Path(__file__).resolve().parents[1]


def unknown():
    return dict(patient_reported_safe="unknown", emergency="unknown", device_running=None,
                backup_hours_left=None, needs=[], english_translation="", evidence_quotes=[], confidence=0)


def test_unknown_values_survive_without_claiming_safety():
    finding = Triage(**unknown())
    assert finding.emergency == "unknown" and finding.device_running is None and finding.backup_hours_left is None
    finding.validate_evidence("No sé.")
    with pytest.raises(ValidationError):
        Triage(**{**unknown(), "emergency": False})


def test_unsupported_findings_and_fabricated_evidence_rejected():
    with pytest.raises(ValueError, match="WITHOUT_EVIDENCE"):
        Triage(**{**unknown(), "device_running": True}).validate_evidence("Maybe.")
    with pytest.raises(ValueError, match="NOT_IN_ORIGINAL"):
        Triage(**{**unknown(), "evidence_quotes": ["I am fine"]}).validate_evidence("Not fine.")
    for invalid in (-1, float("inf"), 1000):
        with pytest.raises(ValidationError):
            Triage(**{**unknown(), "backup_hours_left": invalid})


def test_untrusted_fields_cannot_expand_inbound_authority():
    request = dict(event_id="E-001", patient_id="P-0001", source_message_id="msg-1", text="Hello", language="en")
    for field in ("tenant_id", "role", "actor", "resolve_case"):
        with pytest.raises(ValidationError):
            InboundRequest(**request, **{field: "admin"})
    with pytest.raises(ValidationError):
        InboundRequest(**{**request, "text": " "})


def test_queue_envelope_requires_identity_aware_timestamps_and_refs():
    envelope = dict(job_id="job-1", kind="triage", tenant_id="agency-a", event_id="E-001", event_version=1,
                    patient_id="P-0001", source_message_id="source-1", created_at="2026-10-24T03:00:00Z",
                    deadline_at="2026-10-24T03:05:00Z", correlation_id="corr-1", payload_ref="records://agency-a/m-1")
    JobEnvelope(**envelope)
    for change in ({"source_message_id": None}, {"deadline_at": "2026-10-24T02:00:00Z"},
                   {"created_at": "2026-10-24T03:00:00"}, {"conversation": "secret"}):
        with pytest.raises(ValidationError):
            JobEnvelope(**{**envelope, **change})


def test_human_confirmation_and_resolution_cannot_hide_unknowns():
    with pytest.raises(ValidationError):
        ResolveCase(expected_version=1, notes=" ")
    with pytest.raises(ValidationError):
        ConfirmEvent(expected_version=1, areas=[{"name":"East", "zips":["95127"], "confident":True}],
                     start=None, est_restore=None, acknowledged_unknown_time=False)


def test_fixtures_match_canonical_contracts_and_tenant_scope():
    patients = [Patient.model_validate(p) for p in json.loads((ROOT / "data/patients.json").read_text())]
    assert len(patients) == len({p.patient_id for p in patients}) == 60
    assert {p.tenant_id for p in patients} == {"agency-a", "agency-b"}
    assert {p.language for p in patients} == {"en", "es", "vi", "zh", "tl"}
    data = json.loads((ROOT / "data/mock.json").read_text())
    board, thread = Board.model_validate(data["board"]), Thread.model_validate(data["thread"])
    assert all(row.patient.tenant_id == board.event.tenant_id for row in board.patients.items)
    assert board.total_affected == sum(board.counts.values()) == len(board.patients.items)
    for message in thread.messages.items:
        if message.triage: message.triage.validate_evidence(message.text)
