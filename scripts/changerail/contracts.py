"""Shared exceptions for the project-local ChangeRail implementation."""

from __future__ import annotations


class DeliveryError(RuntimeError):
    """A bounded local-delivery contract failure."""
