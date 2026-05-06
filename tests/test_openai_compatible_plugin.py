from __future__ import annotations

import base64
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_INIT = REPO_ROOT / "plugins" / "openai-compatible" / "__init__.py"

_PNG_HEX = (
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000d49444154789c6300010000000500010d0a2db40000000049454e44"
    "ae426082"
)


def _b64_png() -> str:
    return base64.b64encode(bytes.fromhex(_PNG_HEX)).decode()


def _fake_response(*, b64: str):
    item = SimpleNamespace(b64_json=b64, url=None, revised_prompt=None)
    return SimpleNamespace(data=[item])


def _load_plugin_module():
    spec = importlib.util.spec_from_file_location("openai_compatible_test_plugin", PLUGIN_INIT)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_openai_compatible_uses_custom_provider_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    (tmp_path / "config.yaml").write_text(
        yaml.safe_dump({
            "custom_providers": [
                {
                    "name": "ttp",
                    "base_url": "https://api.husanai.com/v1",
                    "api_key": "sk-ttp-test",
                    "model": "gpt-5.5",
                }
            ],
            "image_gen": {
                "provider": "openai-compatible",
                "model": "gpt-image-2-medium",
                "openai_compatible": {
                    "endpoint": "custom:ttp",
                    "model": "gpt-image-2-medium",
                },
            },
        })
    )

    plugin = _load_plugin_module()
    fake_client = MagicMock()
    fake_client.images.generate.return_value = _fake_response(b64=_b64_png())
    fake_openai = MagicMock()
    fake_openai.OpenAI.return_value = fake_client

    provider = plugin.OpenAICompatibleImageGenProvider()
    with patch.dict("sys.modules", {"openai": fake_openai}):
        assert provider.is_available() is True
        result = provider.generate("a person wearing a linen jacket", aspect_ratio="portrait")

    assert result["success"] is True
    assert result["provider"] == "openai-compatible"
    assert result["model"] == "gpt-image-2-medium"
    assert result["quality"] == "medium"
    assert result["endpoint"] == "custom:ttp"
    assert Path(result["image"]).exists()

    fake_openai.OpenAI.assert_called_once_with(
        api_key="sk-ttp-test",
        base_url="https://api.husanai.com/v1",
    )
    call_kwargs = fake_client.images.generate.call_args.kwargs
    assert call_kwargs["model"] == "gpt-image-2"
    assert call_kwargs["quality"] == "medium"
    assert call_kwargs["size"] == "1024x1536"
    assert "response_format" not in call_kwargs
