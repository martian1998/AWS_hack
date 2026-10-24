"""Single source of truth. Generate OpenAPI/TypeScript; do not duplicate schemas."""
from enum import StrEnum
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints, model_validator

Id = Annotated[str, StringConstraints(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
Language = Literal["en", "es", "vi", "zh", "tl"]
Truth = Literal["yes", "no", "unknown"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, allow_inf_nan=False)


class JobState(StrEnum):
    ACCEPTED = "ACCEPTED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    FAILED_VISIBLE = "FAILED_VISIBLE"
    CANCELLED = "CANCELLED"


class JobEnvelope(Contract):
    schema_version: Literal[1] = 1
    job_id: Id
    kind: Literal["notice", "outreach", "triage", "notification", "followup"]
    tenant_id: Id
    event_id: Id
    event_version: int = Field(ge=1)
    patient_id: Id | None = None
    source_message_id: Id | None = None
    created_at: AwareDatetime
    deadline_at: AwareDatetime
    correlation_id: Id
    payload_ref: str = Field(min_length=1, max_length=512, pattern=r"^records://")

    @model_validator(mode="after")
    def coherent(self):
        if self.deadline_at <= self.created_at:
            raise ValueError("deadline must follow creation")
        if self.kind == "triage" and (not self.patient_id or not self.source_message_id):
            raise ValueError("triage requires patient and source message identity")
        return self


class Accepted(Contract):
    job_id: Id
    resource_id: Id
    state: JobState
    status_url: str = Field(pattern=r"^/jobs/[A-Za-z0-9_-]+$")
    duplicate: bool


class Job(Contract):
    envelope: JobEnvelope
    state: JobState
    version: int = Field(ge=1)
    attempts: int = Field(ge=0, le=2)
    result_urls: list[str] = Field(default_factory=list, max_length=10)
    error_code: str | None = None
    observed_at: AwareDatetime
    mode: Literal["MOCK", "LIVE_BEDROCK", "DETERMINISTIC", "REPLAY"]


class Triage(Contract):
    patient_reported_safe: Truth
    emergency: Truth
    device_running: bool | None
    backup_hours_left: float | None = Field(ge=0, le=720)
    needs: list[Literal["oxygen_tank", "transport", "charging", "medication", "other"]] = Field(max_length=5)
    english_translation: str = Field(max_length=4000)
    evidence_quotes: list[Annotated[str, StringConstraints(min_length=1, max_length=1000)]] = Field(max_length=10)
    confidence: float = Field(ge=0, le=1)

    def validate_evidence(self, original: str) -> None:
        if any(quote not in original for quote in self.evidence_quotes):
            raise ValueError("EVIDENCE_NOT_IN_ORIGINAL")
        if (self.emergency != "unknown" or self.patient_reported_safe != "unknown"
                or self.device_running is not None or self.backup_hours_left is not None or self.needs
                ) and not self.evidence_quotes:
            raise ValueError("FINDING_WITHOUT_EVIDENCE")


class Area(Contract):
    name: str = Field(min_length=1, max_length=100)
    zips: list[Annotated[str, StringConstraints(pattern=r"^\d{5}$")]] = Field(max_length=20)
    confident: bool


class NoticeFindings(Contract):
    utility: str = Field(min_length=1, max_length=200)
    areas: list[Area] = Field(max_length=20)
    flagged_areas: list[str] = Field(max_length=20)
    start: AwareDatetime | None
    est_restore: AwareDatetime | None
    confidence: float = Field(ge=0, le=1)
    is_cancellation: bool

    @model_validator(mode="after")
    def ordered_times(self):
        if self.start and self.est_restore and self.est_restore <= self.start:
            raise ValueError("restoration must follow start")
        return self


class OutageEvent(NoticeFindings):
    event_id: Id
    tenant_id: Id
    version: int = Field(ge=1)
    status: Literal["processing", "needs_confirmation", "active", "cancelled", "human_review"]
    outage_hours: float | None = Field(ge=0, le=8760)


class Device(Contract):
    type: Literal["oxygen_concentrator", "ventilator", "cpap", "bipap", "feeding_pump", "suction", "refrigeration", "wheelchair"]
    backup_hours: float | None = Field(ge=0, le=720)
    backup_tank: bool | None


class Address(Contract):
    city: str
    zip: str = Field(pattern=r"^\d{5}$")


class Contact(Contract):
    type: Literal["self", "caregiver", "none"]
    caregiver_name: str | None = None


class Patient(Contract):
    patient_id: Id
    tenant_id: Id
    display_name: str
    language: Language
    address: Address
    contact: Contact
    devices: list[Device] = Field(max_length=8)
    lives_alone: bool
    mobility_limited: bool


class RankedPatient(Contract):
    patient: Patient
    tier: Literal["CRITICAL", "HIGH", "MEDIUM"]
    score: float = Field(ge=0)
    reasons: list[str]
    uncertainties: list[str]
    status: Literal["not_contacted", "awaiting_reply", "reported_safe", "needs_help", "escalated", "unreachable", "human_review"]


class Message(Contract):
    message_id: Id
    source_message_id: Id
    patient_id: Id
    event_id: Id
    direction: Literal["in", "out"]
    text: Text
    language: Language
    created_at: AwareDatetime
    sequence: int = Field(ge=1)
    triage: Triage | None
    processing_state: JobState
    delivery: Literal["queued", "sent", "failed", "acknowledged"]
    mode: Literal["MOCK", "LIVE_BEDROCK", "DETERMINISTIC", "REPLAY"]


class Escalation(Contract):
    case_id: Id
    event_id: Id
    patient_id: Id
    tier: Literal["CRITICAL", "HIGH", "MEDIUM"]
    reason: str
    evidence_quotes: list[str]
    state: Literal["OPEN", "ACKNOWLEDGED", "RESOLVED"]
    version: int = Field(ge=1)
    assigned_to: Id | None
    created_at: AwareDatetime
    acknowledged_at: AwareDatetime | None
    resolved_at: AwareDatetime | None
    resolved_by: Id | None
    notes: str | None


Item = TypeVar("Item")


class Page(Contract, Generic[Item]):
    items: list[Item] = Field(max_length=50)
    next_cursor: str | None
    observed_at: AwareDatetime


class Board(Contract):
    event: OutageEvent
    patients: Page[RankedPatient]
    total_affected: int = Field(ge=0)
    counts: dict[str, int]
    mode: Literal["MOCK", "LIVE_BEDROCK", "DETERMINISTIC", "REPLAY"]


class Thread(Contract):
    patient: Patient
    messages: Page[Message]
    cases: list[Escalation] = Field(max_length=50)


class AuditEntry(Contract):
    audit_id: Id
    event_id: Id
    actor: str
    action: str
    resource_id: Id
    created_at: AwareDatetime
    correlation_id: Id
    mode: Literal["MOCK", "LIVE_BEDROCK", "DETERMINISTIC", "REPLAY"]


class Metric(Contract):
    name: str
    value: float | None
    unit: str
    source: str
    observed_at: AwareDatetime


class Operations(Contract):
    window_start: AwareDatetime
    window_end: AwareDatetime
    metrics: list[Metric]
    mode: Literal["MOCK", "LIVE_BEDROCK", "DETERMINISTIC", "REPLAY"]


class CreateEvent(Contract):
    notice_text: str = Field(min_length=1, max_length=12000)


class OutreachRequest(Contract):
    expected_version: int = Field(ge=1)


class InboundRequest(Contract):
    event_id: Id
    patient_id: Id
    source_message_id: Id
    text: Text
    language: Language


class ConfirmEvent(Contract):
    expected_version: int = Field(ge=1)
    areas: list[Area] = Field(min_length=1, max_length=20)
    start: AwareDatetime | None
    est_restore: AwareDatetime | None
    acknowledged_unknown_time: bool

    @model_validator(mode="after")
    def confirmation(self):
        if (self.start is None or self.est_restore is None) and not self.acknowledged_unknown_time:
            raise ValueError("unknown time must be explicitly acknowledged")
        if self.start and self.est_restore and self.est_restore <= self.start:
            raise ValueError("restoration must follow start")
        return self


class CaseAction(Contract):
    expected_version: int = Field(ge=1)


class AssignCase(CaseAction):
    assigned_to: Id


class ResolveCase(CaseAction):
    notes: Text


class SimulatorSession(Contract):
    token: str
    expires_at: AwareDatetime
    patient_id: Id
    event_id: Id


class CreateSession(Contract):
    patient_id: Id
    event_id: Id


class ApiError(Contract):
    code: str
    message: str
    retryable: bool
    correlation_id: Id


class ErrorResponse(Contract):
    error: ApiError


class Health(Contract):
    ok: Literal[True] = True
