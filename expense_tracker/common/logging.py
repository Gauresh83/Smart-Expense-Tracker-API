import logging

SENSITIVE_KEYS = frozenset({
    "password", "password2", "old_password", "new_password",
    "authorization", "token", "refresh", "access",
    "secret", "api_key", "credit_card",
})


class SensitiveDataFilter(logging.Filter):
    """
    Strips sensitive fields from log records so passwords and tokens
    never appear in log output, even at DEBUG level.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, dict):
            record.args = self._scrub(record.args)
        elif isinstance(record.args, (list, tuple)):
            record.args = type(record.args)(
                self._scrub(a) if isinstance(a, dict) else a
                for a in record.args
            )
        return True

    def _scrub(self, data: dict) -> dict:
        return {
            k: "***REDACTED***" if k.lower() in SENSITIVE_KEYS else v
            for k, v in data.items()
        }
