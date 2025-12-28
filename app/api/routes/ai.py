"""
AI API Routes
AI-powered features and integrations
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.ai_service import AIService, get_ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


# ==================== SCHEMAS ====================

class GenerateRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: Optional[str] = None


class GenerateResponse(BaseModel):
    response: str
    provider: str
    model: str


class SentimentRequest(BaseModel):
    text: str


class IntentRequest(BaseModel):
    text: str


class ResponseGenerationRequest(BaseModel):
    customer_message: str
    context: Optional[Dict[str, Any]] = None
    tone: str = "professional"


class ConversationSummaryRequest(BaseModel):
    messages: List[Dict[str, Any]]


# ==================== ENDPOINTS ====================

@router.post("/generate", response_model=GenerateResponse)
async def generate_text(
    request: GenerateRequest,
    ai: AIService = Depends(get_ai_service)
):
    """
    Generate text using AI
    
    - **prompt**: Text prompt for generation
    - **provider**: AI provider (openai, claude, gemini, groq, ollama)
    - **temperature**: Creativity level 0.0-2.0
    - **max_tokens**: Maximum response length
    - **system_prompt**: System instruction
    """
    try:
        response = await ai.generate(
            prompt=request.prompt,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt
        )
        
        return GenerateResponse(
            response=response,
            provider=request.provider or ai.default_provider,
            model="auto"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")


@router.post("/sentiment")
async def analyze_sentiment(
    request: SentimentRequest,
    ai: AIService = Depends(get_ai_service)
):
    """
    Analyze text sentiment
    
    Returns:
    - **sentiment**: positive, negative, or neutral
    - **confidence**: Confidence score 0.0-1.0
    - **emotions**: Detected emotions
    - **tone**: Overall tone description
    """
    try:
        result = await ai.analyze_sentiment(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis error: {str(e)}")


@router.post("/intent")
async def extract_intent(
    request: IntentRequest,
    ai: AIService = Depends(get_ai_service)
):
    """
    Extract user intent from text
    
    Returns:
    - **primary_intent**: Main intent
    - **confidence**: Confidence score
    - **entities**: Extracted entities
    - **action_required**: Suggested action
    """
    try:
        result = await ai.extract_intent(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent extraction error: {str(e)}")


@router.post("/generate-response")
async def generate_customer_response(
    request: ResponseGenerationRequest,
    ai: AIService = Depends(get_ai_service)
):
    """
    Generate contextual response for customer
    
    - **customer_message**: Customer's message
    - **context**: Additional context (customer info, history, etc.)
    - **tone**: Response tone (professional, friendly, casual, formal)
    """
    try:
        response = await ai.generate_response(
            customer_message=request.customer_message,
            context=request.context,
            tone=request.tone
        )
        
        return {
            "response": response,
            "tone": request.tone
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response generation error: {str(e)}")


@router.post("/summarize-conversation")
async def summarize_conversation(
    request: ConversationSummaryRequest,
    ai: AIService = Depends(get_ai_service)
):
    """
    Summarize a conversation
    
    - **messages**: List of messages with 'sender' and 'content'
    
    Returns brief 2-3 sentence summary
    """
    try:
        summary = await ai.summarize_conversation(request.messages)
        
        return {
            "summary": summary,
            "message_count": len(request.messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")


@router.get("/providers")
async def list_providers(ai: AIService = Depends(get_ai_service)):
    """
    List available AI providers
    
    Returns:
    - **available_providers**: List of active providers
    - **default_provider**: Current default
    - **total_providers**: Count
    """
    info = ai.get_provider_info()
    return info


@router.get("/health")
async def health_check(ai: AIService = Depends(get_ai_service)):
    """
    Check AI service health
    
    Tests connection to available providers
    """
    try:
        providers = ai.get_available_providers()
        
        # Test default provider
        test_prompt = "Say 'OK' if you can read this."
        try:
            response = await ai.generate(test_prompt, max_tokens=10)
            default_status = "healthy"
        except:
            default_status = "degraded"
        
        return {
            "status": "healthy" if providers else "no_providers",
            "available_providers": providers,
            "default_provider": ai.default_provider,
            "default_provider_status": default_status,
            "total_providers": len(providers)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
