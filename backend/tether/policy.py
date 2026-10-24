"""Editable synthetic demonstration policy; not clinical risk scoring."""
import re
from .models import Triage

AREA_ZIPS = {"East San Jose": ["95116", "95122", "95127"], "Milpitas": ["95035"], "Alum Rock": ["95127"]}
KEYWORDS = {
    "en": [r"can['’]?t breathe", r"cannot breathe", r"chest pain", r"unconscious", r"turning blue"],
    "es": [r"no puedo respirar", r"dolor (?:en el|de) pecho", r"inconsciente"],
    "vi": [r"không thở được", r"đau ngực", r"bất tỉnh"],
    "zh": [r"呼吸困难", r"喘不过气", r"胸痛", r"失去意识"],
    "tl": [r"hindi makahinga", r"sakit sa dibdib", r"walang malay"],
}
LIFE_SUPPORT = {"oxygen_concentrator", "ventilator"}
TEMPLATES = {
    "en": "Synthetic care-team check-in: a power shutoff may affect your area. Reply 1 to acknowledge or 2 to request help. Contact your care team through this demo. For an emergency, call local emergency services.",
    "es": "Mensaje de demostración: un corte de luz puede afectar su zona. Responda 1 para confirmar o 2 para pedir ayuda. Contacte a su equipo en esta demostración. En una emergencia, llame a los servicios de emergencia locales.",
    "vi": "Tin nhắn minh họa: khu vực có thể bị mất điện. Trả lời 1 để xác nhận hoặc 2 để yêu cầu trợ giúp. Liên hệ nhóm chăm sóc trong bản minh họa. Khi khẩn cấp, gọi dịch vụ cấp cứu địa phương.",
    "zh": "演示关怀消息：您所在地区可能停电。回复1确认，回复2请求帮助。请在演示中联系照护团队。如遇紧急情况，请拨打当地急救电话。",
    "tl": "Demonstrasyon: maaaring mawalan ng kuryente sa inyong lugar. Sumagot ng 1 upang kumpirmahin o 2 para humingi ng tulong. Makipag-ugnayan sa pangkat dito. Sa emergency, tumawag sa lokal na emergency services.",
}


def emergency_evidence(text):
    # Deliberately conservative: negations/quotes can still be flagged for human assessment.
    # Suppressing hits based on a simplistic negation rule can miss actual distress.
    matches = []
    for patterns in KEYWORDS.values():
        for pattern in patterns:
            matches.extend(m.group(0) for m in re.finditer(pattern, text, flags=re.IGNORECASE))
    return list(dict.fromkeys(matches))[:10]


def rank(patient, event):
    hours = event.get("outage_hours")
    unknowns = []
    reasons = []
    if hours is None: unknowns.append("Restoration time unknown")
    score = 0.5 * patient["lives_alone"] + 0.5 * patient["mobility_limited"]
    critical = False
    for device in patient["devices"]:
        backup = device["backup_hours"]
        life = device["type"] in LIFE_SUPPORT
        score += 3 if life else 1
        if backup is None:
            unknowns.append("Backup duration unknown")
            reasons.append(f"{device['type'].replace('_', ' ')}: backup unknown")
        else:
            reasons.append(f"{device['type'].replace('_', ' ')}: {backup:g}h documented backup")
            if hours is not None:
                deficit = max(0, hours - backup)
                score += min(3, deficit / max(hours, 1) * 3)
                critical |= life and backup < min(hours, 12)
    if patient["lives_alone"]: reasons.append("Lives alone")
    if patient["mobility_limited"]: reasons.append("Mobility assistance may be needed")
    return {"patient": patient, "tier": "CRITICAL" if critical else "HIGH" if score >= 3 or unknowns else "MEDIUM",
            "score": score, "reasons": reasons, "uncertainties": unknowns, "status": "not_contacted"}


def finding_severity(triage, patient):
    if triage.emergency == "yes" or (triage.device_running is False and any(d["type"] in LIFE_SUPPORT for d in patient["devices"])):
        return "CRITICAL"
    if triage.patient_reported_safe == "no" or triage.needs:
        return "HIGH"
    return None


def unknown_triage():
    return Triage(patient_reported_safe="unknown", emergency="unknown", device_running=None,
                  backup_hours_left=None, needs=[], english_translation="", evidence_quotes=[], confidence=0)
