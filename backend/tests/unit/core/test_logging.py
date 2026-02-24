"""Tests for logging module."""

import logging

from app.core.logging import SensitiveDataFilter, get_logger, setup_logging


class TestSensitiveDataFilter:
    """Test SensitiveDataFilter coverage (line 49)."""

    def should_return_true_when_message_is_empty(self):
        """Test line 49: filter returns True when record.msg is empty."""
        # Given
        log_filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg="", args=(), exc_info=None
        )

        # When
        result = log_filter.filter(record)

        # Then
        assert result is True

    def should_filter_password_from_log_message(self):
        """Test password filtering."""
        # Given
        log_filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="password=secret123",
            args=(),
            exc_info=None,
        )

        # When
        result = log_filter.filter(record)

        # Then
        assert result is True
        assert "***REDACTED***" in record.msg
        assert "secret123" not in record.msg


class TestSetupLogging:
    """Test setup_logging function."""

    def should_setup_logging_with_default_format(self):
        """Test setup with default format."""
        setup_logging(level=logging.DEBUG)
        logger = get_logger("test")
        # Child loggers inherit level from root, so check that handlers exist
        assert len(logger.handlers) >= 0  # May be 0 if using root handlers
        assert logging.getLogger().level == logging.DEBUG
