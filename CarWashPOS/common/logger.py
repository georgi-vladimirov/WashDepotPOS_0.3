import logging
import json
import urllib.request
from typing import Any
from common.middleware import get_current_user


EXCLUDED_FIELDS = {
    "args", "asctime", "created", "exc_info", "exc_text",
    "filename", "funcName", "levelname", "levelno", "lineno",
    "message", "module", "msecs", "msg", "name", "pathname",
    "process", "processName", "relativeCreated", "stack_info",
    "thread", "threadName",
}


def _make_serializable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(i) for i in obj]
    if hasattr(obj, 'hex'):
        return str(obj)
    if hasattr(obj, 'quantize'):
        return float(obj)
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if hasattr(obj, '_meta'):
        return _make_serializable({
            k: v for k, v in obj.__dict__.items()
            if not k.startswith('_')
        })
    if hasattr(obj, '__dict__'):
        return _make_serializable(obj.__dict__)
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        return str(obj)


def _get_user_info() -> dict[str, Any]:
    user = get_current_user()
    if user is None:
        return {"user_id": None, "username": "anonymous"}
    return {"user_id": user.id, "username": user.username}


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        extra = {
            k: _make_serializable(v)
            for k, v in record.__dict__.items()
            if k not in EXCLUDED_FIELDS
        }
        return json.dumps({
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "user": _get_user_info(),
            "extra": extra,
        }, ensure_ascii=False)


class BetterStackHandler(logging.Handler):
    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token
        self.url = "https://in.logs.betterstack.com"
        self._formatter = logging.Formatter()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            extra = {
                k: _make_serializable(v)
                for k, v in record.__dict__.items()
                if k not in EXCLUDED_FIELDS
            }
            log_entry = json.dumps({
                "timestamp": self._formatter.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "user": _get_user_info(),
                **extra,
            }, ensure_ascii=False).encode("utf-8")

            req = urllib.request.Request(
                self.url,
                data=log_entry,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
            )
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass
