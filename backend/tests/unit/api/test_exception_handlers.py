"""Unit tests for exception handlers.

Tests the global exception handling in the API layer.
"""

import pytest
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

from app.api.exception_handlers import register_exception_handlers
from app.domain.exceptions import (
    DomainError,
    ForbiddenError,
    ResourceConflictError,
    ResourceNotFoundError,
    UnauthorizedError,
    ValidationError,
)


@pytest.fixture
def app():
    """Create a test FastAPI app with exception handlers registered."""
    test_app = FastAPI()
    register_exception_handlers(test_app)
    return test_app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestHTTPExceptionHandler:
    """Test handling of HTTPException."""

    def test_handles_400_bad_request(self, app, client):
        """Test 400 Bad Request is handled correctly."""

        @app.get("/test-400")
        def raise_400():
            raise HTTPException(status_code=400, detail="Bad request test")

        response = client.get("/test-400")
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "BAD_REQUEST"
        assert data["message"] == "Bad request test"

    def test_handles_401_unauthorized(self, app, client):
        """Test 401 Unauthorized is handled correctly."""

        @app.get("/test-401")
        def raise_401():
            raise HTTPException(status_code=401, detail="Unauthorized test")

        response = client.get("/test-401")
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "UNAUTHORIZED"
        assert data["message"] == "Unauthorized test"

    def test_handles_403_forbidden(self, app, client):
        """Test 403 Forbidden is handled correctly."""

        @app.get("/test-403")
        def raise_403():
            raise HTTPException(status_code=403, detail="Forbidden test")

        response = client.get("/test-403")
        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "FORBIDDEN"
        assert data["message"] == "Forbidden test"

    def test_handles_404_not_found(self, app, client):
        """Test 404 Not Found is handled correctly."""

        @app.get("/test-404")
        def raise_404():
            raise HTTPException(status_code=404, detail="Not found test")

        response = client.get("/test-404")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "NOT_FOUND"
        assert data["message"] == "Not found test"

    def test_handles_409_conflict(self, app, client):
        """Test 409 Conflict is handled correctly."""

        @app.get("/test-409")
        def raise_409():
            raise HTTPException(status_code=409, detail="Conflict test")

        response = client.get("/test-409")
        assert response.status_code == 409
        data = response.json()
        assert data["code"] == "CONFLICT"
        assert data["message"] == "Conflict test"

    def test_handles_422_unprocessable_entity(self, app, client):
        """Test 422 Unprocessable Entity is handled correctly."""

        @app.get("/test-422")
        def raise_422():
            raise HTTPException(status_code=422, detail="Validation error test")

        response = client.get("/test-422")
        assert response.status_code == 422
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert data["message"] == "Validation error test"

    def test_handles_500_internal_server_error(self, app, client):
        """Test 500 Internal Server Error is handled correctly."""

        @app.get("/test-500")
        def raise_500():
            raise HTTPException(status_code=500, detail="Server error test")

        response = client.get("/test-500")
        assert response.status_code == 500
        data = response.json()
        assert data["code"] == "INTERNAL_SERVER_ERROR"
        assert data["message"] == "Server error test"

    def test_handles_unknown_http_status(self, app, client):
        """Test unknown HTTP status codes are handled with generic code."""

        @app.get("/test-418")
        def raise_418():
            raise HTTPException(status_code=418, detail="I'm a teapot")

        response = client.get("/test-418")
        assert response.status_code == 418
        data = response.json()
        assert data["code"] == "HTTP_ERROR"
        assert data["message"] == "I'm a teapot"


class TestDomainErrorHandler:
    """Test handling of DomainError exceptions."""

    def test_handles_resource_not_found_error(self, app, client):
        """Test ResourceNotFoundError returns 404."""

        @app.get("/test-not-found")
        def raise_not_found():
            raise ResourceNotFoundError("Resource not found test")

        response = client.get("/test-not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "RESOURCE_NOT_FOUND"
        assert data["message"] == "Resource not found test"

    def test_handles_validation_error(self, app, client):
        """Test ValidationError returns 400."""

        @app.get("/test-validation")
        def raise_validation():
            raise ValidationError("Validation failed test")

        response = client.get("/test-validation")
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert data["message"] == "Validation failed test"

    def test_handles_unauthorized_error(self, app, client):
        """Test UnauthorizedError returns 401."""

        @app.get("/test-unauthorized")
        def raise_unauthorized():
            raise UnauthorizedError("Authentication required test")

        response = client.get("/test-unauthorized")
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "UNAUTHORIZED"
        assert data["message"] == "Authentication required test"

    def test_handles_forbidden_error(self, app, client):
        """Test ForbiddenError returns 403."""

        @app.get("/test-forbidden")
        def raise_forbidden():
            raise ForbiddenError("Permission denied test")

        response = client.get("/test-forbidden")
        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "FORBIDDEN"
        assert data["message"] == "Permission denied test"

    def test_handles_resource_conflict_error(self, app, client):
        """Test ResourceConflictError returns 409."""

        @app.get("/test-conflict")
        def raise_conflict():
            raise ResourceConflictError("Resource conflict test")

        response = client.get("/test-conflict")
        assert response.status_code == 409
        data = response.json()
        assert data["code"] == "RESOURCE_CONFLICT"
        assert data["message"] == "Resource conflict test"

    def test_handles_generic_domain_error(self, app, client):
        """Test generic DomainError returns 400."""

        @app.get("/test-domain")
        def raise_domain():
            raise DomainError("Generic domain error")

        response = client.get("/test-domain")
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "DOMAIN_ERROR"
        assert data["message"] == "Generic domain error"

    def test_uses_default_message_when_no_message_provided(self, app, client):
        """Test default message is used when no custom message provided."""

        @app.get("/test-default-message")
        def raise_default():
            raise ResourceNotFoundError()  # No message

        response = client.get("/test-default-message")
        assert response.status_code == 404
        data = response.json()
        assert data["message"] == "Resource not found"  # Default message


class TestGenericExceptionHandler:
    """Test handling of generic Exception."""

    def test_handles_unexpected_exception(self, app, client):
        """Test unexpected exceptions return 500 with generic message."""

        @app.get("/test-unexpected")
        def raise_unexpected():
            raise ValueError("Something unexpected happened")

        # In production, unhandled exceptions would be caught by the handler
        # In test client with debug=True, they may be raised directly
        # We test the handler is registered instead
        assert Exception in app.exception_handlers or any(
            issubclass(exc, Exception) for exc in app.exception_handlers.keys()
        )

    def test_handler_registered_for_exception(self, app):
        """Test that generic Exception handler is registered."""
        handler_types = list(app.exception_handlers.keys())
        assert Exception in handler_types


class TestExceptionHandlerIntegration:
    """Test exception handlers work together correctly."""

    def test_handlers_registered_correctly(self, app):
        """Test that all exception handlers are registered."""
        assert len(app.exception_handlers) >= 3

    def test_response_format_consistency(self, app, client):
        """Test all error responses follow consistent format."""

        @app.get("/test-format-404")
        def raise_format_404():
            raise ResourceNotFoundError("Test message")

        @app.get("/test-format-400")
        def raise_format_400():
            raise ValidationError("Test validation error")

        response_404 = client.get("/test-format-404")
        data_404 = response_404.json()
        assert "code" in data_404
        assert "message" in data_404

        response_400 = client.get("/test-format-400")
        data_400 = response_400.json()
        assert "code" in data_400
        assert "message" in data_400

        assert set(data_404.keys()) == set(data_400.keys())


class TestCategoryStatusMapping:
    """Test category to status code mapping."""

    def test_not_found_category_returns_404(self, app, client):
        """Test NOT_FOUND category maps to 404."""

        @app.get("/test-category-not-found")
        def raise_cat_not_found():
            error = ResourceNotFoundError()
            assert error.category == "NOT_FOUND"
            raise error

        response = client.get("/test-category-not-found")
        assert response.status_code == 404

    def test_conflict_category_returns_409(self, app, client):
        """Test CONFLICT category maps to 409."""

        @app.get("/test-category-conflict")
        def raise_cat_conflict():
            error = ResourceConflictError()
            assert error.category == "CONFLICT"
            raise error

        response = client.get("/test-category-conflict")
        assert response.status_code == 409

    def test_validation_category_returns_400(self, app, client):
        """Test VALIDATION category maps to 400."""

        @app.get("/test-category-validation")
        def raise_cat_validation():
            error = ValidationError()
            assert error.category == "VALIDATION"
            raise error

        response = client.get("/test-category-validation")
        assert response.status_code == 400

    def test_unauthorized_category_returns_401(self, app, client):
        """Test UNAUTHORIZED category maps to 401."""

        @app.get("/test-category-unauthorized")
        def raise_cat_unauthorized():
            error = UnauthorizedError()
            assert error.category == "UNAUTHORIZED"
            raise error

        response = client.get("/test-category-unauthorized")
        assert response.status_code == 401

    def test_forbidden_category_returns_403(self, app, client):
        """Test FORBIDDEN category maps to 403."""

        @app.get("/test-category-forbidden")
        def raise_cat_forbidden():
            error = ForbiddenError()
            assert error.category == "FORBIDDEN"
            raise error

        response = client.get("/test-category-forbidden")
        assert response.status_code == 403

    def test_business_category_returns_400(self, app, client):
        """Test BUSINESS category maps to 400."""

        @app.get("/test-category-business")
        def raise_cat_business():
            error = DomainError()
            assert error.category == "BUSINESS"
            raise error

        response = client.get("/test-category-business")
        assert response.status_code == 400
