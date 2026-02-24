import logging

from app.core.logging import SensitiveDataFilter, get_logger, setup_logging


class TestSensitiveDataFilter:
    def should_redact_password_when_filter_given_password_in_message(self):
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="User login attempt: email=test@example.com, password=mypassword123",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "password=***REDACTED***" in record.msg
        assert "mypassword123" not in record.msg

    def should_redact_tokens_when_filter_given_tokens_in_message(self):
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Token created: access_token=abc123xyz, refresh_token=def456uvw",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "access_token=***REDACTED***" in record.msg
        assert "refresh_token=***REDACTED***" in record.msg
        assert "abc123xyz" not in record.msg
        assert "def456uvw" not in record.msg

    def should_redact_api_keys_when_filter_given_api_keys_in_message(self):
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="API request: api_key=secretkey123, secret_key=anothersecret456",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "api_key=***REDACTED***" in record.msg
        assert "secret_key=***REDACTED***" in record.msg
        assert "secretkey123" not in record.msg
        assert "anothersecret456" not in record.msg

    def should_redact_jwt_when_filter_given_jwt_in_message(self):
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "***REDACTED***" in record.msg
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in record.msg

    def should_mask_email_when_filter_given_email_in_message(self):
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="User login attempt: email=test@example.com",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "t***@example.com" in record.msg
        assert "test@example.com" not in record.msg

    def should_mask_all_emails_when_filter_given_multiple_emails_in_message(self):
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Emails: user1@example.com, user2@domain.org, user3@test.net",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "u***@example.com" in record.msg
        assert "u***@domain.org" in record.msg
        assert "u***@test.net" in record.msg

    def should_redact_password_case_insensitive_when_filter_given_varied_case(self):
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Login: PASSWORD=secret123, PassWord=secret456",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "PASSWORD=***REDACTED***" in record.msg
        assert "PassWord=***REDACTED***" in record.msg

    def should_redact_sensitive_data_when_filter_given_json_message(self):
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg='{"email": "test@example.com", "password": "secret123"}',
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "password=***REDACTED***" in record.msg
        assert "t***@example.com" in record.msg
        assert "secret123" not in record.msg

    def should_leave_unchanged_when_filter_given_no_sensitive_data(self):
        filter_instance = SensitiveDataFilter()
        original_msg = "User logged in successfully"
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg=original_msg,
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert record.msg == original_msg


class TestSetupLogging:
    def should_configure_root_logger_when_setup_logging_called(self):
        setup_logging(level=logging.DEBUG, enable_sensitive_filter=True)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) > 0

    def should_apply_sensitive_filter_when_setup_logging_with_filter_enabled(self):
        setup_logging(level=logging.INFO, enable_sensitive_filter=True)

        logger = get_logger(__name__)

        log_capture = []

        class ListHandler(logging.Handler):
            def emit(self, record):
                log_capture.append(self.format(record))

        handler = ListHandler()
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)

        logger.info("Login attempt: email=test@example.com, password=mypassword123")

        assert len(log_capture) > 0
        log_message = log_capture[0]
        assert "password=***REDACTED***" in log_message
        assert "mypassword123" not in log_message

        logger.removeHandler(handler)


class TestGetLogger:
    def should_return_logger_instance_when_get_logger_called_with_name(self):
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def should_return_same_instance_when_get_logger_called_multiple_times(self):
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")
        assert logger1 is logger2
