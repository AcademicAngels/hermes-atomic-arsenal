"""OpenAI-compatible image generation provider for Hermes.

This user plugin treats ``custom_providers`` entries as multi-capability
endpoints. ``image_gen.openai_compatible.endpoint`` selects which endpoint to
use for image generation, while text generation can continue using the same
``custom:<name>`` provider independently.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from agent.image_gen_provider import (
    DEFAULT_ASPECT_RATIO,
    ImageGenProvider,
    error_response,
    resolve_aspect_ratio,
    save_b64_image,
    success_response,
)

logger = logging.getLogger(__name__)


API_MODEL = "gpt-image-2"

_MODELS: Dict[str, Dict[str, Any]] = {
    "gpt-image-2-low": {
        "display": "GPT Image 2 (Low)",
        "speed": "~15s",
        "strengths": "Fast iteration, lowest cost",
        "api_model": "gpt-image-2",
        "quality": "low",
    },
    "gpt-image-2-medium": {
        "display": "GPT Image 2 (Medium)",
        "speed": "~40s",
        "strengths": "Balanced default",
        "api_model": "gpt-image-2",
        "quality": "medium",
    },
    "gpt-image-2-high": {
        "display": "GPT Image 2 (High)",
        "speed": "~2min",
        "strengths": "Highest fidelity",
        "api_model": "gpt-image-2",
        "quality": "high",
    },
}

DEFAULT_MODEL = "gpt-image-2-medium"

_SIZES = {
    "landscape": "1536x1024",
    "square": "1024x1024",
    "portrait": "1024x1536",
}


def _load_config() -> Dict[str, Any]:
    try:
        from hermes_cli.config import load_config

        cfg = load_config()
        return cfg if isinstance(cfg, dict) else {}
    except Exception as exc:
        logger.debug("Could not load Hermes config: %s", exc)
        return {}


def _image_cfg() -> Dict[str, Any]:
    cfg = _load_config()
    section = cfg.get("image_gen") if isinstance(cfg, dict) else None
    return section if isinstance(section, dict) else {}


def _plugin_cfg() -> Dict[str, Any]:
    cfg = _image_cfg()
    section = cfg.get("openai_compatible") if isinstance(cfg.get("openai_compatible"), dict) else {}
    return section if isinstance(section, dict) else {}


def _resolve_model() -> Tuple[str, Dict[str, Any]]:
    env_override = os.environ.get("OPENAI_COMPATIBLE_IMAGE_MODEL")
    if env_override and env_override in _MODELS:
        return env_override, _MODELS[env_override]

    cfg = _plugin_cfg()
    candidate = cfg.get("model")
    if isinstance(candidate, str) and candidate in _MODELS:
        return candidate, _MODELS[candidate]

    top = _image_cfg().get("model")
    if isinstance(top, str) and top in _MODELS:
        return top, _MODELS[top]

    return DEFAULT_MODEL, _MODELS[DEFAULT_MODEL]


def _compatible_custom_providers() -> List[Dict[str, Any]]:
    cfg = _load_config()
    try:
        from hermes_cli.config import get_compatible_custom_providers

        providers = get_compatible_custom_providers(cfg)
        return providers if isinstance(providers, list) else []
    except Exception as exc:
        logger.debug("Could not load compatible custom providers: %s", exc)
        providers = cfg.get("custom_providers")
        return providers if isinstance(providers, list) else []


def _resolve_endpoint() -> Tuple[Optional[str], Optional[Dict[str, str]], Optional[str]]:
    endpoint = _plugin_cfg().get("endpoint")
    if not isinstance(endpoint, str) or not endpoint.strip():
        return None, None, "image_gen.openai_compatible.endpoint is required"

    endpoint = endpoint.strip()
    if not endpoint.startswith("custom:"):
        return endpoint, None, "Only custom:<name> endpoints are supported by this local plugin"

    name = endpoint.split(":", 1)[1].strip().lower()
    if not name:
        return endpoint, None, "custom endpoint name is empty"

    for entry in _compatible_custom_providers():
        if not isinstance(entry, dict):
            continue
        names = {
            str(entry.get("name", "") or "").strip().lower(),
            str(entry.get("provider_key", "") or "").strip().lower(),
        }
        if name not in names:
            continue
        api_key = str(entry.get("api_key", "") or "").strip()
        base_url = str(entry.get("base_url", "") or "").strip()
        if not api_key or not base_url:
            return endpoint, None, f"{endpoint} is missing api_key or base_url"
        return endpoint, {"api_key": api_key, "base_url": base_url}, None

    return endpoint, None, f"{endpoint} was not found in custom_providers"


class OpenAICompatibleImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        return "openai-compatible"

    @property
    def display_name(self) -> str:
        return "OpenAI-compatible endpoint"

    def is_available(self) -> bool:
        _, creds, _ = _resolve_endpoint()
        if not creds:
            return False
        try:
            import openai  # noqa: F401
        except ImportError:
            return False
        return True

    def list_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": model_id,
                "display": meta["display"],
                "speed": meta["speed"],
                "strengths": meta["strengths"],
                "price": "endpoint dependent",
            }
            for model_id, meta in _MODELS.items()
        ]

    def default_model(self) -> Optional[str]:
        return DEFAULT_MODEL

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "OpenAI-compatible endpoint",
            "badge": "custom",
            "tag": "Use image models exposed by a custom_providers endpoint",
            "env_vars": [],
        }

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        prompt = (prompt or "").strip()
        aspect = resolve_aspect_ratio(aspect_ratio)
        endpoint, creds, endpoint_error = _resolve_endpoint()

        if not prompt:
            return error_response(
                error="Prompt is required and must be a non-empty string",
                error_type="invalid_argument",
                provider=self.name,
                aspect_ratio=aspect,
            )

        if not creds:
            return error_response(
                error=endpoint_error or "OpenAI-compatible endpoint is not configured",
                error_type="auth_required",
                provider=self.name,
                aspect_ratio=aspect,
            )

        try:
            import openai
        except ImportError:
            return error_response(
                error="openai Python package not installed",
                error_type="missing_dependency",
                provider=self.name,
                aspect_ratio=aspect,
            )

        tier_id, meta = _resolve_model()
        size = _SIZES.get(aspect, _SIZES["square"])
        api_model = str(meta.get("api_model") or API_MODEL)
        quality = str(meta.get("quality") or "medium")

        payload: Dict[str, Any] = {
            "model": api_model,
            "prompt": prompt,
            "size": size,
            "n": 1,
            "quality": quality,
        }

        try:
            client = openai.OpenAI(**creds)
            response = client.images.generate(**payload)
        except Exception as exc:
            logger.debug("OpenAI-compatible image generation failed", exc_info=True)
            return error_response(
                error=f"OpenAI-compatible image generation failed: {exc}",
                error_type="api_error",
                provider=self.name,
                model=tier_id,
                prompt=prompt,
                aspect_ratio=aspect,
            )

        data = getattr(response, "data", None) or []
        if not data:
            return error_response(
                error="OpenAI-compatible endpoint returned no image data",
                error_type="empty_response",
                provider=self.name,
                model=tier_id,
                prompt=prompt,
                aspect_ratio=aspect,
            )

        first = data[0]
        b64 = getattr(first, "b64_json", None)
        url = getattr(first, "url", None)
        revised_prompt = getattr(first, "revised_prompt", None)

        if b64:
            try:
                image_ref = str(save_b64_image(b64, prefix=f"openai_compatible_{tier_id}"))
            except Exception as exc:
                return error_response(
                    error=f"Could not save image to cache: {exc}",
                    error_type="io_error",
                    provider=self.name,
                    model=tier_id,
                    prompt=prompt,
                    aspect_ratio=aspect,
                )
        elif url:
            image_ref = url
        else:
            return error_response(
                error="OpenAI-compatible response contained neither b64_json nor URL",
                error_type="empty_response",
                provider=self.name,
                model=tier_id,
                prompt=prompt,
                aspect_ratio=aspect,
            )

        extra: Dict[str, Any] = {
            "size": size,
            "quality": quality,
            "endpoint": endpoint,
            "api_model": api_model,
        }
        if revised_prompt:
            extra["revised_prompt"] = revised_prompt

        return success_response(
            image=image_ref,
            model=tier_id,
            prompt=prompt,
            aspect_ratio=aspect,
            provider=self.name,
            extra=extra,
        )


def register(ctx) -> None:
    ctx.register_image_gen_provider(OpenAICompatibleImageGenProvider())
