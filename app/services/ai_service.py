"""
AI Service - Multi-Provider AI Integration
Supports: OpenAI, Claude, Gemini, Groq, Ollama, Custom Models
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class AIProvider:
    """Base AI Provider Interface"""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError
    
    async def stream_generate(self, prompt: str, **kwargs):
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI GPT-4/GPT-3.5 Provider"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": kwargs.get("system_prompt", "You are a helpful AI assistant.")},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation error: {str(e)}")
            raise
    
    async def stream_generate(self, prompt: str, **kwargs):
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": kwargs.get("system_prompt", "You are a helpful AI assistant.")},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000),
                stream=True
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {str(e)}")
            raise


class ClaudeProvider(AIProvider):
    """Anthropic Claude 3.5 Provider"""
    
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1024),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude generation error: {str(e)}")
            raise


class GeminiProvider(AIProvider):
    """Google Gemini Provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.model}:generateContent",
                    params={"key": self.api_key},
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": kwargs.get("temperature", 0.7),
                            "maxOutputTokens": kwargs.get("max_tokens", 1000)
                        }
                    }
                )
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Gemini generation error: {str(e)}")
            raise


class GroqProvider(AIProvider):
    """Groq Fast Inference Provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
        self.base_url = "https://api.groq.com/openai/v1"
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": kwargs.get("system_prompt", "You are a helpful AI assistant.")},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 1000)
                    }
                )
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq generation error: {str(e)}")
            raise


class OllamaProvider(AIProvider):
    """Ollama Local AI Provider"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3:8b")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                result = response.json()
                return result["response"]
        except Exception as e:
            logger.error(f"Ollama generation error: {str(e)}")
            raise


class AIService:
    """Multi-Provider AI Service with Intelligent Routing"""
    
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self._initialize_providers()
        self.default_provider = os.getenv("DEFAULT_AI_PROVIDER", "openai")
    
    def _initialize_providers(self):
        """Initialize available AI providers"""
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.providers["openai"] = OpenAIProvider(os.getenv("OPENAI_API_KEY"))
            logger.info("✅ OpenAI provider initialized")
        
        # Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            self.providers["claude"] = ClaudeProvider(os.getenv("ANTHROPIC_API_KEY"))
            logger.info("✅ Claude provider initialized")
        
        # Gemini
        if os.getenv("GOOGLE_API_KEY"):
            self.providers["gemini"] = GeminiProvider(os.getenv("GOOGLE_API_KEY"))
            logger.info("✅ Gemini provider initialized")
        
        # Groq
        if os.getenv("GROQ_API_KEY"):
            self.providers["groq"] = GroqProvider(os.getenv("GROQ_API_KEY"))
            logger.info("✅ Groq provider initialized")
        
        # Ollama
        try:
            self.providers["ollama"] = OllamaProvider()
            logger.info("✅ Ollama provider initialized")
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {str(e)}")
    
    async def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate AI response with intelligent provider routing"""
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            # Fallback to first available provider
            if self.providers:
                provider_name = list(self.providers.keys())[0]
                logger.warning(f"⚠️ Provider '{provider}' not available, using '{provider_name}'")
            else:
                raise ValueError("No AI providers available")
        
        try:
            result = await self.providers[provider_name].generate(prompt, **kwargs)
            logger.info(f"✅ AI generation successful with {provider_name}")
            return result
        except Exception as e:
            logger.error(f"❌ AI generation failed with {provider_name}: {str(e)}")
            # Try fallback providers
            for fallback_provider in self.providers:
                if fallback_provider != provider_name:
                    try:
                        logger.info(f"🔄 Trying fallback provider: {fallback_provider}")
                        result = await self.providers[fallback_provider].generate(prompt, **kwargs)
                        return result
                    except:
                        continue
            raise Exception("All AI providers failed")
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        prompt = f"""Analyze the sentiment of the following text and respond with JSON only:

Text: {text}

Respond with this exact JSON structure:
{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "emotions": ["emotion1", "emotion2"],
    "tone": "description of tone"
}}"""
        
        try:
            response = await self.generate(prompt, temperature=0.3)
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                return {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "emotions": [],
                    "tone": "unclear"
                }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": [],
                "tone": "error"
            }
    
    async def extract_intent(self, text: str) -> Dict[str, Any]:
        """Extract user intent from text"""
        prompt = f"""Extract the intent from the following text and respond with JSON only:

Text: {text}

Respond with this exact JSON structure:
{{
    "primary_intent": "intent_name",
    "confidence": 0.0-1.0,
    "entities": {{"entity_type": "entity_value"}},
    "action_required": "suggested action"
}}"""
        
        try:
            response = await self.generate(prompt, temperature=0.3)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                return {
                    "primary_intent": "unknown",
                    "confidence": 0.0,
                    "entities": {},
                    "action_required": "clarify"
                }
        except Exception as e:
            logger.error(f"Intent extraction error: {str(e)}")
            return {
                "primary_intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "action_required": "error"
            }
    
    async def generate_response(
        self,
        customer_message: str,
        context: Optional[Dict[str, Any]] = None,
        tone: str = "professional"
    ) -> str:
        """Generate contextual response for customer"""
        context_str = ""
        if context:
            context_str = f"\nContext: {json.dumps(context, ensure_ascii=False)}"
        
        prompt = f"""Generate a {tone} response to the following customer message:{context_str}

Customer Message: {customer_message}

Generate a helpful, {tone} response:"""
        
        return await self.generate(prompt, temperature=0.8)
    
    async def summarize_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize a conversation"""
        conversation = "\n".join([
            f"{msg.get('sender', 'User')}: {msg.get('content', '')}"
            for msg in messages
        ])
        
        prompt = f"""Summarize the following conversation in 2-3 sentences:

{conversation}

Summary:"""
        
        return await self.generate(prompt, temperature=0.5, max_tokens=200)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        return list(self.providers.keys())
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available providers"""
        return {
            "available_providers": list(self.providers.keys()),
            "default_provider": self.default_provider,
            "total_providers": len(self.providers)
        }


# Global AI service instance
ai_service = AIService()


async def get_ai_service() -> AIService:
    """Dependency injection for AI service"""
    return ai_service
