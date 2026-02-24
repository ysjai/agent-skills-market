"""User model compatibility module.

This module re-exports User from the new location for backwards compatibility.
"""

from src.domain.aggregates.user import User

__all__ = ["User"]
