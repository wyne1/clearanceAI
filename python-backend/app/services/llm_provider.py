import os
import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class PricingInfo:
    """Pricing information for an LLM request."""
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float = 0.7
    ) -> Tuple[Dict[str, Any], Optional[PricingInfo]]:
        """
        Generate a JSON response from the LLM.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction/role
            temperature: Temperature setting
            
        Returns:
            Tuple of (parsed JSON dictionary, pricing info)
        """
        pass
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float = 0.6
    ) -> Tuple[str, Optional[PricingInfo]]:
        """
        Generate a text response from the LLM.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction/role
            temperature: Temperature setting
            
        Returns:
            Tuple of (text response string, pricing info)
        """
        pass
    
    @abstractmethod
    def _extract_pricing_info(self, response: Any) -> Optional[PricingInfo]:
        """
        Extract pricing information from provider response.
        
        Args:
            response: Raw response from provider
            
        Returns:
            PricingInfo or None if unavailable
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""
    
    # Pricing per million tokens for different OpenAI models
    # Format: {model_name: (input_price_per_million, output_price_per_million)}
    MODEL_PRICING = {
        "gpt-4o-search-preview": (2.50, 10.00),
        "gpt-4o-mini-search-preview": (0.15, 0.60),
        # Add more models as needed
        # "gpt-4o": (2.50, 10.00),  # Example for regular gpt-4o
        # "gpt-4o-mini": (0.15, 0.60),  # Example for regular gpt-4o-mini
    }
    
    def __init__(self, model_name: str):
        super().__init__(model_name)
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Get pricing for this model, with fallback defaults
        pricing = self.MODEL_PRICING.get(model_name)
        if pricing:
            self.input_price_per_million, self.output_price_per_million = pricing
            logger.info(f"      → Using pricing for {model_name}: ${self.input_price_per_million:.2f} input, ${self.output_price_per_million:.2f} output per million tokens")
        else:
            # Fallback to default pricing (gpt-4o-search-preview pricing)
            self.input_price_per_million = 2.50
            self.output_price_per_million = 10.0
            logger.warning(f"      → No pricing found for {model_name}, using default: ${self.input_price_per_million:.2f} input, ${self.output_price_per_million:.2f} output per million tokens")
    
    async def generate_json(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float = 0.7
    ) -> Tuple[Dict[str, Any], Optional[PricingInfo]]:
        """Generate JSON response from OpenAI."""
        logger.info(f"      → Sending request to OpenAI {self.model_name}...")
        
        # Search models don't support temperature parameter
        is_search_model = "search" in self.model_name.lower()
        
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
        
        # Only add temperature if not a search model
        if is_search_model:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature
            )
        
        # DEBUG: Print raw response for pricing inspection
        logger.info(f"      → RAW OPENAI RESPONSE (for pricing debug):")
        logger.info(f"         Response type: {type(response)}")
        logger.info(f"         Has usage: {hasattr(response, 'usage')}")
        if hasattr(response, 'usage'):
            logger.info(f"         Usage object: {response.usage}")
            if response.usage:
                try:
                    usage_dict = response.usage.model_dump() if hasattr(response.usage, 'model_dump') else vars(response.usage)
                    logger.info(f"         Usage dict: {usage_dict}")
                except Exception as e:
                    logger.info(f"         Could not serialize usage: {e}")
                    logger.info(f"         Usage attributes: {dir(response.usage)}")
        logger.info(f"         Full response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        
        pricing_info = self._extract_pricing_info(response)
        if pricing_info:
            logger.info(f"      → OpenAI tokens: {pricing_info.input_tokens} in, {pricing_info.output_tokens} out (cost: ${pricing_info.total_cost:.6f})")
        else:
            logger.warning(f"      → No pricing info extracted from OpenAI response")
        
        result = response.choices[0].message.content
        if not result:
            raise ValueError("Empty response from OpenAI")
        
        logger.info(f"research_entity_news: OPENAI RESPONSE: {result}") # DEBUG
        
        # Extract JSON from markdown if present
        from app.services.response_normalizer import extract_json_from_response
        json_text = extract_json_from_response(result)
        logger.info(f"      → Extracted JSON text (length: {len(json_text)})")
        
        parsed_result = json.loads(json_text)
        logger.info(f"      → Parsed JSON response successfully")
        return parsed_result, pricing_info
    
    async def generate_text(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float = 0.6
    ) -> Tuple[str, Optional[PricingInfo]]:
        """Generate text response from OpenAI."""
        logger.info(f"      → Sending request to OpenAI {self.model_name}...")
        
        # Search models don't support temperature parameter
        is_search_model = "search" in self.model_name.lower()
        
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
        
        # Only add temperature if not a search model
        if is_search_model:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature
            )
        
        # DEBUG: Print raw response for pricing inspection
        logger.info(f"      → RAW OPENAI RESPONSE (for pricing debug):")
        logger.info(f"         Response type: {type(response)}")
        logger.info(f"         Has usage: {hasattr(response, 'usage')}")
        if hasattr(response, 'usage'):
            logger.info(f"         Usage object: {response.usage}")
            if response.usage:
                try:
                    usage_dict = response.usage.model_dump() if hasattr(response.usage, 'model_dump') else vars(response.usage)
                    logger.info(f"         Usage dict: {usage_dict}")
                except Exception as e:
                    logger.info(f"         Could not serialize usage: {e}")
                    logger.info(f"         Usage attributes: {dir(response.usage)}")
        
        pricing_info = self._extract_pricing_info(response)
        if pricing_info:
            logger.info(f"      → OpenAI tokens: {pricing_info.input_tokens} in, {pricing_info.output_tokens} out (cost: ${pricing_info.total_cost:.6f})")
        else:
            logger.warning(f"      → No pricing info extracted from OpenAI response")
        
        content = response.choices[0].message.content
        logger.info(f"generate_risk_assessment_insights: OPENAI RESPONSE: {content}") # DEBUG
        result = content.strip() if content else ""
        return result, pricing_info
    
    def _extract_pricing_info(self, response: Any) -> Optional[PricingInfo]:
        """Extract pricing info from OpenAI response."""
        if not response.usage:
            return None
        
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        input_cost = (input_tokens / 1_000_000) * self.input_price_per_million
        output_cost = (output_tokens / 1_000_000) * self.output_price_per_million
        total_cost = input_cost + output_cost
        
        return PricingInfo(
            provider="openai",
            model=self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost
        )


class GeminiProvider(LLMProvider):
    """Google Gemini provider implementation with web search."""
    
    def __init__(self, model_name: str):
        super().__init__(model_name)
        from google import genai
        from google.genai import types
        
        self.genai = genai
        self.types = types
        
        # Check if using Vertex AI or regular API
        use_vertexai = os.getenv("GEMINI_USE_VERTEXAI", "false").lower() == "true"
        api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
        
        if use_vertexai:
            # Vertex AI requires project and location
            project = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            
            if not project:
                raise ValueError(
                    "GOOGLE_CLOUD_PROJECT must be set when using Vertex AI. "
                    "Either set GEMINI_USE_VERTEXAI=false to use regular API, "
                    "or set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION"
                )
            
            self.client = genai.Client(
                vertexai=True,
                project=project,
                location=location
            )
            logger.info(f"      → Using Vertex AI (project: {project}, location: {location})")
        else:
            # Regular API - just needs API key
            if not api_key:
                raise ValueError("GOOGLE_CLOUD_API_KEY must be set when not using Vertex AI")
            
            self.client = genai.Client(
                vertexai=False,
                api_key=api_key
            )
            logger.info(f"      → Using Gemini API (non-Vertex AI)")
        
        # Pricing per million tokens (Gemini Flash pricing)
        # Free tier: $0.00, Paid tier: $0.50 input / $3.00 output
        # Default to paid tier pricing (can be overridden via env vars)
        pricing_tier = os.getenv("GEMINI_PRICING_TIER", "paid").lower()
        if pricing_tier == "free":
            self.input_price_per_million = 0.0
            self.output_price_per_million = 0.0
            logger.info(f"      → Using FREE tier pricing (input: $0.00, output: $0.00 per million tokens)")
        else:
            # Paid tier pricing for gemini-3-flash-preview
            self.input_price_per_million = float(os.getenv("GEMINI_INPUT_PRICE_PER_MILLION", "0.50"))
            self.output_price_per_million = float(os.getenv("GEMINI_OUTPUT_PRICE_PER_MILLION", "3.00"))
            logger.info(f"      → Using PAID tier pricing (input: ${self.input_price_per_million:.2f}, output: ${self.output_price_per_million:.2f} per million tokens)")
        
        # Google Search pricing: 5,000 free queries/month, then $14 per 1,000 queries
        # Note: We track this but don't calculate it automatically (requires monthly tracking)
        self.search_queries_free_per_month = 5000
        self.search_price_per_thousand = 14.0
        
        # System instruction for time-sensitive queries
        self.system_instruction_text = """For time-sensitive user queries that require up-to-date information, you MUST follow the provided current time (date and year) when formulating search queries in tool calls. Remember it is 2025 this year."""
    
    async def generate_json(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float = 0.7
    ) -> Tuple[Dict[str, Any], Optional[PricingInfo]]:
        """Generate JSON response from Gemini with web search."""
        logger.info(f"      → Sending request to Gemini {self.model_name}...")
        
        contents = [
            self.types.Content(
                role="user",
                parts=[self.types.Part.from_text(text=prompt)]
            )
        ]
        
        tools = [
            self.types.Tool(google_search=self.types.GoogleSearch())
        ]
        
        generate_content_config = self.types.GenerateContentConfig(
            temperature=temperature,
            top_p=0.95,
            max_output_tokens=65535,
            safety_settings=[
                self.types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF"
                ),
                self.types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="OFF"
                ),
                self.types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF"
                ),
                self.types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF"
                )
            ],
            tools=tools,
            system_instruction=[self.types.Part.from_text(text=f"{self.system_instruction_text}\n\n{system_instruction}")],
            # thinking_config=self.types.ThinkingConfig(
            #     thinking_level="LOW"
            # )
        )
        
        # Use non-streaming API
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=generate_content_config
        )
        
        # DEBUG: Print raw response for pricing inspection and search queries
        logger.info(f"      → RAW GEMINI RESPONSE (for pricing debug):")
        logger.info(f"         Response type: {type(response)}")
        logger.info(f"         Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        
        # Check for search/function call information
        if hasattr(response, 'candidates') and response.candidates:
            for idx, candidate in enumerate(response.candidates):
                logger.info(f"         Candidate {idx}:")
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts'):
                        for part_idx, part in enumerate(candidate.content.parts):
                            logger.info(f"            Part {part_idx} type: {type(part)}")
                            # Check for function calls (search queries)
                            if hasattr(part, 'function_call'):
                                logger.info(f"            Function call found: {part.function_call}")
                            # Check for any search-related attributes
                            part_attrs = [attr for attr in dir(part) if 'search' in attr.lower() or 'function' in attr.lower() or 'tool' in attr.lower()]
                            if part_attrs:
                                logger.info(f"            Search/function related attributes: {part_attrs}")
                                for attr in part_attrs:
                                    try:
                                        value = getattr(part, attr)
                                        if not callable(value):
                                            logger.info(f"            {attr}: {value}")
                                    except Exception as e:
                                        logger.info(f"            Could not get {attr}: {e}")
        
        # Check for automatic function calling history (search queries)
        if hasattr(response, 'automatic_function_calling_history'):
            logger.info(f"         Has automatic_function_calling_history: True")
            try:
                history = response.automatic_function_calling_history
                logger.info(f"         Function calling history: {history}")
                if history:
                    for item in history:
                        logger.info(f"            History item: {item}")
            except Exception as e:
                logger.info(f"         Could not access function calling history: {e}")
        else:
            logger.info(f"         Has automatic_function_calling_history: False")
        
        if hasattr(response, 'usage_metadata'):
            logger.info(f"         Has usage_metadata: True")
            logger.info(f"         Usage metadata type: {type(response.usage_metadata)}")
            if response.usage_metadata:
                logger.info(f"         Usage metadata attributes: {[attr for attr in dir(response.usage_metadata) if not attr.startswith('_')]}")
                try:
                    usage_dict = vars(response.usage_metadata)
                    logger.info(f"         Usage metadata dict: {usage_dict}")
                except Exception as e:
                    logger.info(f"         Could not convert usage_metadata to dict: {e}")
        else:
            logger.info(f"         Has usage_metadata: False")
        # Try to find any token/usage related attributes
        token_attrs = [attr for attr in dir(response) if 'token' in attr.lower() or 'usage' in attr.lower() or 'cost' in attr.lower()]
        if token_attrs:
            logger.info(f"         Token/usage related attributes found: {token_attrs}")
            for attr in token_attrs:
                try:
                    value = getattr(response, attr)
                    if not callable(value):
                        logger.info(f"         {attr}: {value}")
                except Exception as e:
                    logger.info(f"         Could not get {attr}: {e}")
        
        pricing_info = self._extract_pricing_info(response)
        if pricing_info:
            logger.info(f"      → Gemini tokens: {pricing_info.input_tokens} in, {pricing_info.output_tokens} out (cost: ${pricing_info.total_cost:.6f})")
        else:
            logger.warning(f"      → No pricing info extracted from Gemini response")
        
        # Extract text from response
        if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
            raise ValueError("Empty response from Gemini")
        
        result = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                result += part.text
        
        if not result:
            raise ValueError("Empty response from Gemini")
        
        logger.info(f"research_entity_news: GEMINI RESPONSE: {result}") # DEBUG
        
        # Extract JSON from markdown if present
        from app.services.response_normalizer import extract_json_from_response
        json_text = extract_json_from_response(result)
        logger.info(f"      → Extracted JSON text (length: {len(json_text)})")
        
        parsed_result = json.loads(json_text)
        logger.info(f"      → Parsed JSON response successfully")
        return parsed_result, pricing_info
    
    async def generate_text(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float = 0.6
    ) -> Tuple[str, Optional[PricingInfo]]:
        """Generate text response from Gemini with web search."""
        logger.info(f"      → Sending request to Gemini {self.model_name}...")
        
        contents = [
            self.types.Content(
                role="user",
                parts=[self.types.Part.from_text(text=prompt)]
            )
        ]
        
        tools = [
            self.types.Tool(google_search=self.types.GoogleSearch())
        ]
        
        generate_content_config = self.types.GenerateContentConfig(
            temperature=temperature,
            top_p=0.95,
            max_output_tokens=65535,
            safety_settings=[
                self.types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF"
                ),
                self.types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="OFF"
                ),
                self.types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF"
                ),
                self.types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF"
                )
            ],
            tools=tools,
            system_instruction=[self.types.Part.from_text(text=f"{self.system_instruction_text}\n\n{system_instruction}")],
            # thinking_config=self.types.ThinkingConfig(
            #     thinking_level="LOW"
            # )
        )
        
        # Use non-streaming API
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=generate_content_config
        )
        
        # DEBUG: Print raw response for pricing inspection
        logger.info(f"      → RAW GEMINI RESPONSE (for pricing debug):")
        logger.info(f"         Response type: {type(response)}")
        logger.info(f"         Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        if hasattr(response, 'usage_metadata'):
            logger.info(f"         Has usage_metadata: True")
            logger.info(f"         Usage metadata type: {type(response.usage_metadata)}")
            if response.usage_metadata:
                logger.info(f"         Usage metadata attributes: {[attr for attr in dir(response.usage_metadata) if not attr.startswith('_')]}")
                try:
                    usage_dict = vars(response.usage_metadata)
                    logger.info(f"         Usage metadata dict: {usage_dict}")
                except Exception as e:
                    logger.info(f"         Could not convert usage_metadata to dict: {e}")
        else:
            logger.info(f"         Has usage_metadata: False")
        # Try to find any token/usage related attributes
        token_attrs = [attr for attr in dir(response) if 'token' in attr.lower() or 'usage' in attr.lower() or 'cost' in attr.lower()]
        if token_attrs:
            logger.info(f"         Token/usage related attributes found: {token_attrs}")
            for attr in token_attrs:
                try:
                    value = getattr(response, attr)
                    if not callable(value):
                        logger.info(f"         {attr}: {value}")
                except Exception as e:
                    logger.info(f"         Could not get {attr}: {e}")
        
        pricing_info = self._extract_pricing_info(response)
        if pricing_info:
            logger.info(f"      → Gemini tokens: {pricing_info.input_tokens} in, {pricing_info.output_tokens} out (cost: ${pricing_info.total_cost:.6f})")
        else:
            logger.warning(f"      → No pricing info extracted from Gemini response")
        
        # Extract text from response
        if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
            return "", pricing_info
        
        result = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                result += part.text
        
        logger.info(f"generate_risk_assessment_insights: GEMINI RESPONSE: {result}") # DEBUG
        return result.strip(), pricing_info
    
    def _extract_pricing_info(self, response: Any) -> Optional[PricingInfo]:
        """Extract pricing info from Gemini response."""
        # Gemini response structure may differ - need to check actual response format
        # For now, return None if we can't extract token info
        # TODO: Implement actual token extraction from Gemini response
        # This might be in response.usage_metadata or similar
        
        # Placeholder - need to check actual Gemini response structure
        input_tokens = 0
        output_tokens = 0
        
        # Try to extract from response if available
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            if hasattr(usage, 'prompt_token_count'):
                input_tokens = usage.prompt_token_count
            if hasattr(usage, 'candidates_token_count'):
                output_tokens = usage.candidates_token_count
        
        if input_tokens == 0 and output_tokens == 0:
            return None
        
        input_cost = (input_tokens / 1_000_000) * self.input_price_per_million
        output_cost = (output_tokens / 1_000_000) * self.output_price_per_million
        total_cost = input_cost + output_cost
        
        return PricingInfo(
            provider="gemini",
            model=self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost
        )


def get_provider() -> LLMProvider:
    """
    Factory function to get the configured LLM provider.
    
    Returns:
        LLMProvider instance based on LLM_PROVIDER env var
    """
    provider_name = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider_name == "gemini":
        model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        logger.info(f"🔧 Using Gemini provider with model: {model}")
        return GeminiProvider(model_name=model)
    else:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-search-preview")
        logger.info(f"🔧 Using OpenAI provider with model: {model}")
        return OpenAIProvider(model_name=model)

