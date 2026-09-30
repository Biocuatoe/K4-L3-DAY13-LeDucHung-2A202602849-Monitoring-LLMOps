from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any

try:
    from langfuse import get_client, observe, propagate_attributes

    LANGFUSE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - chỉ dùng khi chưa cài requirements
    LANGFUSE_SDK_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    @contextmanager
    def start_as_current_observation(*args: Any, **kwargs: Any):
        """Dummy context manager that yields a dummy span object."""
        yield _DummySpan()

    def update_current_span(**kwargs: Any) -> None:
        return None

    def update_current_generation(**kwargs: Any) -> None:
        return None

    class _DummyClient:
        def update_current_span(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

    def get_client():
        return _DummyClient()

    @contextmanager
    def propagate_attributes(**kwargs: Any):
        yield


def _get_langfuse_client():
    """Returns the Langfuse client instance, which has start_as_current_observation etc. as methods."""
    return get_client()


def start_as_current_observation(*args: Any, **kwargs: Any):
    """Wrapper that delegates to the client's start_as_current_observation method."""
    return _get_langfuse_client().start_as_current_observation(*args, **kwargs)


def update_current_span(**kwargs: Any) -> None:
    """Wrapper that delegates to the client's update_current_span method."""
    return _get_langfuse_client().update_current_span(**kwargs)


def update_current_generation(**kwargs: Any) -> None:
    """Wrapper that delegates to the client's update_current_generation method."""
    return _get_langfuse_client().update_current_generation(**kwargs)


def get_langfuse_client():
    return _get_langfuse_client()


def tracing_enabled() -> bool:
    return LANGFUSE_SDK_AVAILABLE and bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )


class _DummySpan:
    """Dummy span that supports update() method."""

    def update(self, **kwargs: Any) -> None:
        return None
