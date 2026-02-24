"""Logging configuration with sensitive data filtering."""

import logging
import re
import sys

from typing_extensions import override


class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from logs.

    Filters out:
    - Passwords (password, passwd, pwd fields)
    - Tokens (access_token, refresh_token, authorization header)
    - Full email addresses (shows only first character + *** + domain)
    - API keys
    - Secret keys
    """

    SENSITIVE_PATTERNS: list[tuple[str, str]] = [
        (
            r'["\']?(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'>\s,}]+)["\']?',
            r"\1=***REDACTED***",
        ),
        (
            r'["\']?(access_token|refresh_token|token|authorization)["\']?\s*[:=]\s*["\']?([^"\'>\s,}]+)["\']?',
            r"\1=***REDACTED***",
        ),
        (
            r'["\']?(api[_-]?key|secret[_-]?key|api_secret)["\']?\s*[:=]\s*["\']?([^"\'>\s,}]+)["\']?',
            r"\1=***REDACTED***",
        ),
        (r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "***JWT-TOKEN-REDACTED***"),
    ]

    EMAIL_PATTERN: str = r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b"

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record and redact sensitive data.

        Args:
            record: The log record to filter.

        Returns:
            True to allow the record to be logged, False otherwise.
        """
        if not record.msg:
            return True

        message = str(record.msg)

        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)

        message = re.sub(
            self.EMAIL_PATTERN,
            lambda m: f"{m.group(1)[0]}***@{m.group(2)}",
            message,
            flags=re.IGNORECASE,
        )

        record.msg = message

        return True


def setup_logging(
    level: int = logging.INFO,
    log_format: str | None = None,
    enable_sensitive_filter: bool = True,
) -> None:
    """Configure application logging.

    Args:
        level: Logging level (default: INFO).
        log_format: Custom log format string. If None, uses default.
        enable_sensitive_filter: Enable sensitive data filtering.
    """
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )

    formatter = logging.Formatter(log_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    if enable_sensitive_filter:
        sensitive_filter = SensitiveDataFilter()
        console_handler.addFilter(sensitive_filter)

    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (usually __name__).

    Returns:
        A configured logger instance.
    """
    return logging.getLogger(name)
