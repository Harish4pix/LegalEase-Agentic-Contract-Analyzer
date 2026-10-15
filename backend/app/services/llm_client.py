import json
import re
from typing import Any
import asyncio
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..config import Settings


class LLMClient:
    """Small provider adapter supporting free-tier and fully local models."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def active_provider(self) -> str:
        provider = self.settings.provider
        if provider == "gemini" and not self.settings.gemini_api_key:
            return "demo"
        if provider == "groq" and not self.settings.groq_api_key:
            return "demo"
        return provider

    async def generate_json(self, system: str, prompt: str) -> dict[str, Any]:
        raw = await self._generate(system, prompt, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise ValueError("The model returned an unreadable analysis response.")
            return json.loads(match.group(0))

    async def generate_text(self, system: str, prompt: str) -> str:
        return (await self._generate(system, prompt, json_mode=False)).strip()

    async def _generate(self, system: str, prompt: str, json_mode: bool) -> str:
        provider = self.active_provider
        if provider == "gemini":
            return await self._gemini(system, prompt, json_mode)
        if provider == "groq":
            return await self._groq(system, prompt, json_mode)
        if provider == "ollama":
            return await self._ollama(system, prompt, json_mode)
        raise RuntimeError("LLM generation is unavailable in demo mode.")

    async def _gemini(self, system: str, prompt: str, json_mode: bool) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.model}:generateContent"
        )
        payload: dict[str, Any] = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.15,
                "maxOutputTokens": 8192,
            },
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        data = await self._post_json(
            f"{url}?{urlencode({'key': self.settings.gemini_api_key})}", payload, timeout=55
        )
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _groq(self, system: str, prompt: str, json_mode: bool) -> str:
        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.15,
            "max_completion_tokens": 8192,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        data = await self._post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            payload,
            headers={"Authorization": f"Bearer {self.settings.groq_api_key}"},
            timeout=55,
        )
        return data["choices"][0]["message"]["content"]

    async def _ollama(self, system: str, prompt: str, json_mode: bool) -> str:
        payload = {
            "model": self.settings.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "options": {"temperature": 0.15, "num_ctx": 32768},
        }
        if json_mode:
            payload["format"] = "json"
        data = await self._post_json(
            f"{self.settings.ollama_base_url.rstrip('/')}/api/chat", payload, timeout=180
        )
        return data["message"]["content"]

    @staticmethod
    async def _post_json(
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
        timeout: int = 60,
    ) -> dict[str, Any]:
        def request() -> dict[str, Any]:
            request_headers = {"Content-Type": "application/json", **(headers or {})}
            req = Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=request_headers,
                method="POST",
            )
            try:
                with urlopen(req, timeout=timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                details = exc.read().decode("utf-8", errors="replace")[:500]
                raise RuntimeError(f"Model API returned HTTP {exc.code}: {details}") from exc
            except URLError as exc:
                raise RuntimeError(f"Could not reach the model API: {exc.reason}") from exc

        return await asyncio.to_thread(request)
