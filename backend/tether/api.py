"""Contract routes. No Stage A route falsely accepts or authenticates a request."""
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, FastAPI, Header, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mangum import Mangum
from starlette.exceptions import HTTPException

from .models import (Accepted, AssignCase, AuditEntry, Board, CaseAction, ConfirmEvent,
                     CreateEvent, CreateSession, ErrorResponse, Escalation, Health,
                     InboundRequest, Job, Message, Operations, OutageEvent,
                     OutreachRequest, Page, ResolveCase, SimulatorSession, Thread)

app = FastAPI(title="Tether", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)
bearer = HTTPBearer(auto_error=False)


def error(status: int, code: str, message: str, retryable: bool = False):
    return JSONResponse(status_code=status, content={"error": {
        "code": code, "message": message, "retryable": retryable, "correlation_id": str(uuid4())}})


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    code = "AUTH_REQUIRED" if exc.status_code == 401 else "AUTH_NOT_CONFIGURED" if exc.status_code == 503 else "NOT_FOUND"
    return error(exc.status_code, code, str(exc.detail), exc.status_code == 503)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    # Do not echo submitted text, tokens or input values in validation failures.
    return error(422, "INVALID_REQUEST", "Request does not match the published contract.")


def require_identity(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if credentials is None:
        raise HTTPException(401, "A valid scoped credential is required.")
    # Never treat an arbitrary bearer string as an authenticated principal.
    raise HTTPException(503, "Stage B identity and storage adapters are not implemented.")


@app.get("/health", response_model=Health)
def health():
    return Health()


router = APIRouter(dependencies=[Depends(require_identity)], responses={
    code: {"model": ErrorResponse} for code in (401, 403, 404, 409, 422, 503)})
Limit = Annotated[int, Query(ge=1, le=50)]
Key = Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")]


def unavailable():
    raise HTTPException(503, "Stage B identity and storage adapters are not implemented.")


@router.post("/events", response_model=Accepted, status_code=202)
def create_event(body: CreateEvent, idempotency_key: Key):
    return unavailable()


@router.post("/events/{event_id}/confirm", response_model=OutageEvent)
def confirm_event(event_id: str, body: ConfirmEvent):
    return unavailable()


@router.post("/events/{event_id}/outreach", response_model=Accepted, status_code=202)
def outreach(event_id: str, body: OutreachRequest, idempotency_key: Key):
    return unavailable()


@router.post("/inbound", response_model=Accepted, status_code=202)
def inbound(body: InboundRequest):
    return unavailable()


@router.get("/jobs/{job_id}", response_model=Job)
def job(job_id: str):
    return unavailable()


@router.get("/events/{event_id}/board", response_model=Board)
def board(event_id: str, limit: Limit = 20, cursor: str | None = None):
    return unavailable()


@router.get("/patients/{patient_id}/thread", response_model=Thread)
def thread(patient_id: str, event_id: str, limit: Limit = 20, cursor: str | None = None):
    return unavailable()


@router.get("/phone/{patient_id}/messages", response_model=Page[Message])
def phone(patient_id: str, event_id: str, limit: Limit = 20, cursor: str | None = None):
    return unavailable()


@router.post("/simulator/sessions", response_model=SimulatorSession, status_code=201)
def session(body: CreateSession):
    return unavailable()


@router.get("/events/{event_id}/escalations", response_model=Page[Escalation])
def cases(event_id: str, limit: Limit = 20, cursor: str | None = None):
    return unavailable()


@router.post("/escalations/{case_id}/assign", response_model=Escalation)
def assign(case_id: str, body: AssignCase):
    return unavailable()


@router.post("/escalations/{case_id}/acknowledge", response_model=Escalation)
def acknowledge(case_id: str, body: CaseAction):
    return unavailable()


@router.post("/escalations/{case_id}/resolve", response_model=Escalation)
def resolve(case_id: str, body: ResolveCase):
    return unavailable()


@router.get("/events/{event_id}/audit", response_model=Page[AuditEntry])
def audit(event_id: str, limit: Limit = 20, cursor: str | None = None):
    return unavailable()


@router.get("/operations", response_model=Operations)
def operations(event_id: str):
    return unavailable()


app.include_router(router)
handler = Mangum(app, lifespan="off")
