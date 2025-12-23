import re
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_json_from_response(text: str) -> str:
    """
    Extract JSON from markdown code blocks if present.
    Handles cases like ```json {...} ``` or ``` {...} ```
    
    Args:
        text: Raw response text that may contain JSON in markdown
        
    Returns:
        Extracted JSON string, or original text if no JSON found
    """
    if not text:
        return text
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Try to find JSON in markdown code blocks (handles ```json or just ```)
    # First, find code block markers
    code_block_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if code_block_match:
        extracted = code_block_match.group(1).strip()
        # Validate it's valid JSON before returning
        try:
            json.loads(extracted)
            return extracted
        except json.JSONDecodeError:
            pass
    
    # If no code blocks, try to find JSON object directly (handle nested braces)
    # Find the first { and match to the last }
    brace_start = text.find('{')
    if brace_start != -1:
        # Count braces to find matching closing brace
        brace_count = 0
        for i in range(brace_start, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    extracted = text[brace_start:i+1]
                    # Validate it's valid JSON
                    try:
                        json.loads(extracted)
                        return extracted
                    except json.JSONDecodeError:
                        pass
                    break
    
    # Return original if no valid JSON found
    return text


def normalize_error(error: Exception, provider: str) -> str:
    """
    Normalize error messages across providers.
    
    Args:
        error: Exception object
        provider: Provider name (openai, gemini)
        
    Returns:
        Normalized error message string
    """
    error_msg = str(error)
    
    # Provider-specific error normalization
    if provider == "openai":
        if "rate limit" in error_msg.lower():
            return "Rate limit exceeded. Please try again later."
        elif "invalid api key" in error_msg.lower():
            return "Invalid API key. Please check your OPENAI_API_KEY."
        elif "insufficient_quota" in error_msg.lower():
            return "Insufficient quota. Please check your OpenAI account billing."
    
    elif provider == "gemini":
        if "api key" in error_msg.lower() or "authentication" in error_msg.lower():
            return "Invalid API key. Please check your GOOGLE_CLOUD_API_KEY."
        if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            return "Rate limit or quota exceeded. Please try again later."
    
    # Generic error message
    return f"Error from {provider}: {error_msg}"

