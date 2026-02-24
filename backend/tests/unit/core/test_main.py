"""Tests for main application configuration and lifespan."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import AsyncClient

from app.main import app, lifespan


class TestApplicationLifespan:
    """Test application lifespan events."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_logging(self):
        """Test startup logging is called (L18-19)."""
        mock_logger = MagicMock()

        with patch("app.main.logger", mock_logger):
            async with lifespan(app):
                pass

            # Verify startup log was called
            mock_logger.info.assert_any_call("Application starting up...")

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_logging(self):
        """Test shutdown logging is called (L21)."""
        mock_logger = MagicMock()

        with patch("app.main.logger", mock_logger):
            async with lifespan(app):
                pass

            # Verify shutdown log was called
            mock_logger.info.assert_any_call("Application shutting down...")


class TestApplicationConfiguration:
    """Test main application configuration."""

    def test_app_title(self):
        """Test FastAPI app has correct title."""
        assert app.title == "Agent Skills Manager API"

    def test_app_version(self):
        """Test FastAPI app has correct version."""
        assert app.version == "1.0.0"

    def test_app_description(self):
        """Test FastAPI app has correct description."""
        assert "API for managing agent skills" in app.description

    def test_cors_middleware_configured(self):
        """Test CORS middleware is configured (L34-40)."""
        # Check if CORS middleware is in the app's user middleware
        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls.__name__ == "CORSMiddleware":
                cors_middleware = middleware
                break

        assert cors_middleware is not None, "CORS middleware not found"
        # Verify CORS options
        assert cors_middleware.kwargs.get("allow_credentials") is True
        assert cors_middleware.kwargs.get("allow_methods") == ["*"]
        assert cors_middleware.kwargs.get("allow_headers") == ["*"]

    def test_health_router_registered(self):
        """Test health router is registered (L42)."""
        # Check if health router is included
        routes = [route.path for route in app.routes]
        assert "/health" in routes

    def test_api_router_registered(self):
        """Test API router is registered (L43)."""
        # Check if API routes are included (they should start with /api/)
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        api_routes = [r for r in routes if r.startswith("/api/")]
        assert len(api_routes) > 0, "No API routes found"
