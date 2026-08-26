from __future__ import annotations

import io
import json
import unittest
import urllib.error
from unittest.mock import patch

from coding_agent.config import ModelConfig
from lm_infra.models import ModelResponse, OllamaModel


class FakeHTTPResponse(io.BytesIO):
    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class OllamaModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = OllamaModel(
            ModelConfig(
                name="qwen3.8",
                base_url="http://127.0.0.1:11434",
                temperature=0.2,
                context_length=32_768,
            )
        )

    @patch("lm_infra.models.urllib.request.urlopen")
    def test_generate_normalizes_response(self, urlopen: unittest.mock.Mock) -> None:
        urlopen.return_value = FakeHTTPResponse(
            json.dumps(
                {
                    "message": {"role": "assistant", "content": "next action"},
                    "prompt_eval_count": 120,
                    "eval_count": 18,
                }
            ).encode("utf-8")
        )

        result = self.model.generate([{"role": "user", "content": "Fix the bug"}])

        self.assertEqual(result, ModelResponse("next action", 120, 18))
        request = urlopen.call_args.args[0]
        request_body = json.loads(request.data)
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/api/chat")
        self.assertEqual(request_body["model"], "qwen3.8")
        self.assertFalse(request_body["stream"])
        self.assertEqual(request_body["options"]["num_ctx"], 32_768)

    @patch("lm_infra.models.urllib.request.urlopen")
    def test_connection_error_has_clear_message(self, urlopen: unittest.mock.Mock) -> None:
        urlopen.side_effect = urllib.error.URLError("connection refused")

        with self.assertRaisesRegex(RuntimeError, "Could not connect to Ollama"):
            self.model.generate([])

    @patch("lm_infra.models.urllib.request.urlopen")
    def test_missing_content_is_rejected(self, urlopen: unittest.mock.Mock) -> None:
        urlopen.return_value = FakeHTTPResponse(b'{"message": {}}')

        with self.assertRaisesRegex(RuntimeError, "missing message.content"):
            self.model.generate([])

    @patch("lm_infra.models.urllib.request.urlopen")
    def test_missing_usage_is_unknown(self, urlopen: unittest.mock.Mock) -> None:
        urlopen.return_value = FakeHTTPResponse(
            b'{"message": {"role": "assistant", "content": "hello"}}'
        )

        result = self.model.generate([])

        self.assertIsNone(result.prompt_tokens)
        self.assertIsNone(result.completion_tokens)
