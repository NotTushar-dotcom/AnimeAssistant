"""
Aara Brain - Multi-provider LLM Interface
Supports Claude, Groq, Gemini, Ollama with automatic fallback.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Generator, Optional

from config.settings import SETTINGS, LLMProvider
from core.personality import AARA_SYSTEM_PROMPT, extract_emotion_tag

logger = logging.getLogger(__name__)


class LLMBrain(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        """Send messages and get a complete response."""
        pass

    @abstractmethod
    def chat_stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Send messages and stream the response."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        pass

    def get_system_prompt(self) -> str:
        """Get Aara's system prompt."""
        return AARA_SYSTEM_PROMPT


class AnthropicBrain(LLMBrain):
    """Claude LLM provider."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """Initialize with API key and model."""
        self.model = model
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
            logger.info(f"Initialized Anthropic brain with model: {model}")
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic: {e}")
            raise

    def chat(self, messages: list[dict]) -> str:
        """Send messages and get response."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=SETTINGS.llm.max_tokens,
                system=self.get_system_prompt(),
                messages=messages,
            )
            content = response.content[0].text
            logger.debug(f"Anthropic response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise

    def chat_stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens."""
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=SETTINGS.llm.max_tokens,
                system=self.get_system_prompt(),
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic stream error: {e}")
            raise

    def get_provider_name(self) -> str:
        return f"Anthropic ({self.model})"


class GroqBrain(LLMBrain):
    """Groq LLM provider (free tier)."""

    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        """Initialize with API key and model."""
        self.model = model
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
            logger.info(f"Initialized Groq brain with model: {model}")
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {e}")
            raise

    def chat(self, messages: list[dict]) -> str:
        """Send messages and get response."""
        try:
            full_messages = [{"role": "system", "content": self.get_system_prompt()}] + messages
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=SETTINGS.llm.max_tokens,
                temperature=SETTINGS.llm.temperature,
            )
            content = response.choices[0].message.content
            logger.debug(f"Groq response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"Groq chat error: {e}")
            raise

    def chat_stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens."""
        try:
            full_messages = [{"role": "system", "content": self.get_system_prompt()}] + messages
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=SETTINGS.llm.max_tokens,
                temperature=SETTINGS.llm.temperature,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Groq stream error: {e}")
            raise

    def get_provider_name(self) -> str:
        return f"Groq ({self.model})"


class GeminiBrain(LLMBrain):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """Initialize with API key and model."""
        self.model_name = model
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=model,
                system_instruction=self.get_system_prompt(),
            )
            logger.info(f"Initialized Gemini brain with model: {model}")
        except ImportError:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise

    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """Convert messages to Gemini format."""
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})
        return gemini_messages

    def chat(self, messages: list[dict]) -> str:
        """Send messages and get response."""
        try:
            gemini_messages = self._convert_messages(messages)
            chat = self.model.start_chat(history=gemini_messages[:-1])
            response = chat.send_message(gemini_messages[-1]["parts"][0])
            content = response.text
            logger.debug(f"Gemini response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            raise

    def chat_stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens."""
        try:
            gemini_messages = self._convert_messages(messages)
            chat = self.model.start_chat(history=gemini_messages[:-1])
            response = chat.send_message(gemini_messages[-1]["parts"][0], stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini stream error: {e}")
            raise

    def get_provider_name(self) -> str:
        return f"Gemini ({self.model_name})"


class OllamaBrain(LLMBrain):
    """Ollama local LLM provider."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3.2:8b"):
        """Initialize with host URL and model."""
        self.host = host.rstrip("/")
        self.model = model
        import requests
        self.requests = requests
        logger.info(f"Initialized Ollama brain with model: {model} at {host}")

    def _check_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = self.requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def chat(self, messages: list[dict]) -> str:
        """Send messages and get response."""
        try:
            full_messages = [{"role": "system", "content": self.get_system_prompt()}] + messages
            response = self.requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": full_messages,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            content = response.json()["message"]["content"]
            logger.debug(f"Ollama response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise

    def chat_stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens."""
        try:
            full_messages = [{"role": "system", "content": self.get_system_prompt()}] + messages
            response = self.requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": full_messages,
                    "stream": True,
                },
                stream=True,
                timeout=120,
            )
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            raise

    def get_provider_name(self) -> str:
        return f"Ollama ({self.model})"


class OpenRouterBrain(LLMBrain):
    """OpenRouter LLM provider."""

    def __init__(self, api_key: str, model: str = "meta-llama/llama-3.1-8b-instruct:free"):
        """Initialize with API key and model."""
        self.model = model
        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            logger.info(f"Initialized OpenRouter brain with model: {model}")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter: {e}")
            raise

    def chat(self, messages: list[dict]) -> str:
        """Send messages and get response."""
        try:
            full_messages = [{"role": "system", "content": self.get_system_prompt()}] + messages
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=SETTINGS.llm.max_tokens,
                temperature=SETTINGS.llm.temperature,
            )
            content = response.choices[0].message.content
            logger.debug(f"OpenRouter response: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"OpenRouter chat error: {e}")
            raise

    def chat_stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens."""
        try:
            full_messages = [{"role": "system", "content": self.get_system_prompt()}] + messages
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=SETTINGS.llm.max_tokens,
                temperature=SETTINGS.llm.temperature,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenRouter stream error: {e}")
            raise

    def get_provider_name(self) -> str:
        return f"OpenRouter ({self.model})"


def create_brain() -> LLMBrain:
    """Factory function to create the best available LLM brain."""
    provider = SETTINGS.llm.provider
    logger.info(f"Creating brain with provider: {provider.value}")

    # Try providers in fallback order
    providers_to_try = []

    if provider == LLMProvider.ANTHROPIC:
        providers_to_try = [
            (LLMProvider.ANTHROPIC, SETTINGS.llm.anthropic_key),
            (LLMProvider.GROQ, SETTINGS.llm.groq_key),
            (LLMProvider.GEMINI, SETTINGS.llm.google_key),
            (LLMProvider.OLLAMA, None),
        ]
    elif provider == LLMProvider.GROQ:
        providers_to_try = [
            (LLMProvider.GROQ, SETTINGS.llm.groq_key),
            (LLMProvider.GEMINI, SETTINGS.llm.google_key),
            (LLMProvider.OLLAMA, None),
        ]
    elif provider == LLMProvider.GEMINI:
        providers_to_try = [
            (LLMProvider.GEMINI, SETTINGS.llm.google_key),
            (LLMProvider.GROQ, SETTINGS.llm.groq_key),
            (LLMProvider.OLLAMA, None),
        ]
    elif provider == LLMProvider.OPENROUTER:
        providers_to_try = [
            (LLMProvider.OPENROUTER, SETTINGS.llm.openrouter_key),
            (LLMProvider.GROQ, SETTINGS.llm.groq_key),
            (LLMProvider.OLLAMA, None),
        ]
    else:  # OLLAMA or default
        providers_to_try = [
            (LLMProvider.OLLAMA, None),
            (LLMProvider.GROQ, SETTINGS.llm.groq_key),
        ]

    for prov, key in providers_to_try:
        try:
            if prov == LLMProvider.ANTHROPIC and key:
                return AnthropicBrain(api_key=key, model=SETTINGS.llm.model)
            elif prov == LLMProvider.GROQ and key:
                return GroqBrain(api_key=key, model="llama-3.1-70b-versatile")
            elif prov == LLMProvider.GEMINI and key:
                return GeminiBrain(api_key=key, model="gemini-1.5-flash")
            elif prov == LLMProvider.OPENROUTER and key:
                return OpenRouterBrain(api_key=key, model=SETTINGS.llm.model)
            elif prov == LLMProvider.OLLAMA:
                brain = OllamaBrain(host=SETTINGS.llm.ollama_host, model=SETTINGS.llm.model)
                if brain._check_available():
                    return brain
                logger.warning("Ollama not available, trying next provider")
        except Exception as e:
            logger.warning(f"Failed to create {prov.value} brain: {e}, trying next")
            continue

    # Last resort: return Ollama anyway
    logger.warning("All providers failed, returning Ollama (may not work)")
    return OllamaBrain(host=SETTINGS.llm.ollama_host, model=SETTINGS.llm.model)
