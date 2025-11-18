import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = "gpt-4o"
MODEL_NAME = "gpt-4o-search-preview"


def extract_json_from_response(text: str) -> str:
    """
    Extract JSON from markdown code blocks if present.
    Handles cases like ```json {...} ``` or ``` {...} ```
    """
    import re
    import json
    
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

async def research_entity_news(entity_name: str, entity_type: str, country: Optional[str] = None) -> Dict[str, Any]:
    """
    Use GPT-4o to research an entity and find potential risk indicators.
    Returns news items, sentiment, and risk flags.
    """
    country_context = f" based in {country}" if country else ""
    
    prompt = f"""You are a compliance research assistant for Mexican customs brokers. Research the entity "{entity_name}" ({entity_type}{country_context}) and identify any potential risk indicators.

Search for and analyze:
1. Negative news articles (criminal associations, tax issues, fraud, legal problems)
2. Compliance violations or customs issues
3. Regulatory problems or investigations
4. Suspicious business practices

Return your findings as a JSON object with this structure:
{{
    "newsItems": [
        {{
            "headline": "Article headline",
            "source": "News source name",
            "date": "YYYY-MM-DD",
            "sentiment": "negative|neutral|positive",
            "excerpt": "Brief summary of the article"
        }}
    ],
    "riskFlags": ["flag1", "flag2"],
    "summary": "Overall risk assessment summary"
}}

If you cannot find specific information, create realistic but clearly marked as simulated news items. Focus on finding negative indicators that would concern customs brokers."""

    try:
        logger.info(f"      → Sending request to OpenAI GPT-4o...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a compliance research assistant. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            # temperature=0.7,
            # response_format={"type": "json_object"}
        )
        
        logger.info(f"      → Received response from OpenAI (tokens: {response.usage.total_tokens if response.usage else 'unknown'})")
        result = response.choices[0].message.content
        logger.info(f"research_entity_news: OPENAI RESPONSE: {result}") # DEBUG
        if not result:
            raise ValueError("Empty response from OpenAI")
        
        # Extract JSON from markdown code blocks if present
        json_text = extract_json_from_response(result)
        logger.info(f"      → Extracted JSON text (length: {len(json_text)})")
        
        import json
        parsed_result = json.loads(json_text)
        logger.info(f"      → Parsed JSON response successfully")
        return parsed_result
    except Exception as e:
        logger.error(f"research_entity_news: OPENAI API error: {str(e)}") # DEBUG
        logger.warning(f"      → Using fallback response")
        # Fallback response if OpenAI fails
        return {
            "newsItems": [
                {
                    "headline": f"Limited information available for {entity_name}",
                    "source": "Internal Research",
                    "date": "2024-11-15",
                    "sentiment": "neutral",
                    "excerpt": "Unable to retrieve comprehensive information at this time."
                }
            ],
            "riskFlags": [],
            "summary": "Insufficient data for risk assessment."
        }


async def analyze_trading_pattern(
    entity_name: str,
    commodity: str,
    origin: str,
    historical_patterns: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Use GPT-4o to analyze if a trading pattern is anomalous.
    """
    patterns_text = "\n".join([
        f"- {p.get('commodity', 'Unknown')}: {p.get('frequency', 0)} shipments, typical origins: {', '.join(p.get('normalOrigins', []))}"
        for p in historical_patterns
    ])
    
    prompt = f"""Analyze this trading pattern for potential anomalies:

Entity: {entity_name}
Current Shipment: {commodity} from {origin}

Historical Trading Patterns:
{patterns_text if patterns_text else "No historical data available"}

Determine if this shipment represents an anomaly. Consider:
1. Is this commodity typical for this entity?
2. Is the origin country typical for this commodity?
3. Does this represent a significant deviation from normal patterns?

Return JSON:
{{
    "isAnomaly": true|false,
    "anomalyType": "commodity_change|origin_mismatch|route_change|none",
    "analysis": "Detailed explanation of the pattern analysis",
    "riskLevel": "high|medium|low"
}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a trade pattern analyst. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            # temperature=0.5,
            # response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        logger.info(f"analyze_trading_pattern: OPENAI RESPONSE: {result}") # DEBUG
        if not result:
            return {
                "isAnomaly": False,
                "anomalyType": "none",
                "analysis": "Pattern analysis unavailable.",
                "riskLevel": "low"
            }
        
        # Extract JSON from markdown code blocks if present
        json_text = extract_json_from_response(result)
        logger.info(f"      → Extracted JSON text for pattern analysis")
        
        import json
        return json.loads(json_text)
    except Exception as e:
        logger.error(f"analyze_trading_pattern: OPENAI API error: {str(e)}") # DEBUG
        return {
            "isAnomaly": False,
            "anomalyType": "none",
            "analysis": "Pattern analysis unavailable.",
            "riskLevel": "low"
        }


async def generate_risk_assessment_insights(
    entity_checks: Dict[str, str],
    pattern_analysis: str,
    blacklist_status: Dict[str, Any],
    flags: List[str]
) -> str:
    """
    Use GPT-4o to generate comprehensive AI insights combining all risk factors.
    """
    flags_text = "\n".join([f"- {flag}" for flag in flags]) if flags else "None"
    entity_checks_text = "\n".join([f"- {k}: {v}" for k, v in entity_checks.items()])
    
    prompt = f"""As a customs compliance AI assistant, synthesize this risk assessment data into comprehensive insights:

Entity Verification Results:
{entity_checks_text}

Blacklist Status:
- 60B List: {blacklist_status.get('list60B', False)}
- Approved Manufacturer: {blacklist_status.get('approvedManufacturer', False)}
- Other Flags: {', '.join(blacklist_status.get('otherFlags', []))}

Pattern Analysis:
{pattern_analysis}

Risk Flags Detected:
{flags_text}

Provide a comprehensive risk assessment summary (2-3 sentences) that:
1. Synthesizes all the risk factors
2. Explains the overall risk level
3. Highlights the most concerning aspects

Return only the summary text, no JSON."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a customs compliance expert. Provide clear, concise risk assessments."},
                {"role": "user", "content": prompt}
            ],
            # temperature=0.6
        )
        
        content = response.choices[0].message.content
        logger.info(f"generate_risk_assessment_insights: OPENAI RESPONSE: {content}") # DEBUG
        return content.strip() if content else "This shipment exhibits multiple risk factors that warrant careful review. The combination of entity verification results, blacklist status, and pattern analysis suggests elevated risk."
    except Exception as e:
        logger.error(f"generate_risk_assessment_insights: OPENAI API error: {str(e)}") # DEBUG
        return "This shipment exhibits multiple risk factors that warrant careful review. The combination of entity verification results, blacklist status, and pattern analysis suggests elevated risk."

