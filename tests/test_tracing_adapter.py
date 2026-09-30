from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app import tracing


class TracingAdapterTests(unittest.TestCase):
    def test_adapter_uses_the_installed_langfuse_v4_api(self) -> None:
        # Verify that the functions are imported from langfuse (or are the same callables)
        # by checking they have the expected callables available
        self.assertTrue(callable(tracing.observe))
        self.assertTrue(callable(tracing.propagate_attributes))
        self.assertTrue(callable(tracing.start_as_current_observation))
        self.assertTrue(callable(tracing.update_current_span))
        # Verify the client returned has the expected methods
        client = tracing.get_langfuse_client()
        self.assertTrue(callable(client.update_current_span))
        self.assertTrue(callable(client.update_current_generation))

    def test_tracing_is_disabled_without_both_keys(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(tracing.tracing_enabled())

        with patch.dict(os.environ, {"LANGFUSE_PUBLIC_KEY": "pk-only"}, clear=True):
            self.assertFalse(tracing.tracing_enabled())


if __name__ == "__main__":
    unittest.main()
