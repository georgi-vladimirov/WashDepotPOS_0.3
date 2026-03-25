import logging
import json
import urllib.request

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "extra": {
                k: v for k, v in record.__dict__.items()
                if k not in {
                    "args", "asctime", "created", "exc_info", "exc_text",
                    "filename", "funcName", "levelname", "levelno", "lineno",
                    "message", "module", "msecs", "msg", "name", "pathname",
                    "process", "processName", "relativeCreated", "stack_info",
                    "thread", "threadName",
                }
            },
        })


class BetterStackHandler(logging.Handler):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.url = "https://in.logs.betterstack.com"
        self._formatter = logging.Formatter()

    def emit(self, record):
        try:
            log_entry = json.dumps({
                "message": record.getMessage(),
                "level": record.levelname,
                "logger": record.name,
                "timestamp": self._formatter.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
                **{k: v for k, v in record.__dict__.items()
                   if k not in {
                       "args", "asctime", "created", "exc_info", "exc_text",
                       "filename", "funcName", "levelname", "levelno", "lineno",
                       "message", "module", "msecs", "msg", "name", "pathname",
                       "process", "processName", "relativeCreated",
                       "stack_info", "thread", "threadName",
                   }},
            }).encode("utf-8")

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
