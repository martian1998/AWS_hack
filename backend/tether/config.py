import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str = "unconfigured"
    prefix: str = "tether-demo"
    region: str = "us-east-1"
    database: str = ".local/tether.sqlite3"
    model_id: str = ""
    guardrail_id: str = ""
    guardrail_version: str = ""
    issuer: str = ""
    client_id: str = ""
    frontend_origin: str = "http://127.0.0.1:5173"
    cursor_secret: str = ""
    max_calls: int = 5
    max_tokens: int = 100000
    model_rpm: int = 5
    model_tpm: int = 20000
    output_tokens: int = 800
    followup_seconds: int = 1800
    model_disabled: bool = False

    @classmethod
    def from_env(cls):
        fields = {}
        for name, item in cls.__dataclass_fields__.items():
            value = os.getenv("TETHER_" + name.upper())
            if value is not None:
                if isinstance(item.default, bool): value = value.lower() == "true"
                elif isinstance(item.default, int): value = int(value)
                fields[name] = value
        return cls(**fields)
