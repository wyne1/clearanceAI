import logging
from typing import List, Dict, Any, Optional
from app.services.llm_provider import get_provider
from app.services.pricing_tracker import get_pricing_tracker
from app.services.response_normalizer import normalize_error

logger = logging.getLogger(__name__)

# Get the configured provider (OpenAI or Gemini)
_provider = None

def _get_provider():
    """Lazy initialization of provider."""
    global _provider
    if _provider is None:
        _provider = get_provider()
    return _provider

async def research_entity_news(entity_name: str, entity_type: str, country: Optional[str] = None) -> Dict[str, Any]:
    """
    Use LLM (OpenAI or Gemini) to research an entity and find potential risk indicators.
    Returns news items, sentiment, and risk flags.
    """
    provider = _get_provider()
    country_context = f" based in {country}" if country else ""
    
    prompt = f"""You are a compliance research assistant for Mexican customs brokers. Research the entity "{entity_name}" ({entity_type}{country_context}) and identify any potential risk indicators.

IMPORTANT INSTRUCTIONS:
- Use web search to find REAL, ACTUAL news articles and information about this entity
- ONLY return information you find from actual web searches
- DO NOT create, simulate, or generate fake news items
- If you cannot find any real information about this entity, return an EMPTY newsItems array
- Be specific with your search queries - try variations of the entity name, include the country, and search for terms like "fraud", "investigation", "customs", "tax", etc.

Search for and analyze:
1. Negative news articles (criminal associations, tax issues, fraud, legal problems)
2. Compliance violations or customs issues
3. Regulatory problems or investigations
4. Suspicious business practices

Return your findings as a JSON object with this structure:
{{
    "newsItems": [
        {{
            "headline": "Article headline (from actual search results)",
            "source": "News source name (actual source)",
            "date": "YYYY-MM-DD (actual date from article)",
            "sentiment": "negative|neutral|positive",
            "excerpt": "Brief summary of the actual article"
        }}
    ],
    "riskFlags": ["flag1", "flag2"],
    "summary": "Overall risk assessment summary. If no news was found, state that clearly."
}}

CRITICAL: If you cannot find any real information about "{entity_name}" through web search, return:
{{
    "newsItems": [],
    "riskFlags": [],
    "summary": "No real-world information found about this entity through web search. No risk indicators identified."
}}"""

    try:
        # Enhanced system instruction for providers with web search
        if provider.provider_name == "gemini":
            system_instruction = """You are a compliance research assistant with access to web search. 
            - ALWAYS use web search to find REAL information about entities
            - NEVER create, simulate, or generate fake news
            - If web search returns no results, return empty newsItems array
            - Only return information you actually find through web search
            - Always return valid JSON"""
        else:
            system_instruction = "You are a compliance research assistant. Always return valid JSON."
        
        logger.info(f"      → Using {provider.provider_name} for entity research")
        result, pricing_info = await provider.generate_json(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.7
        )
        
        # Track pricing
        if pricing_info:
            tracker = get_pricing_tracker()
            tracker.record_request(pricing_info, "research_entity_news")
        
        logger.info(f"      → Parsed JSON response successfully")
        return result
    except Exception as e:
        error_msg = normalize_error(e, provider.provider_name)
        logger.error(f"research_entity_news: {provider.provider_name.upper()} API error: {error_msg}")
        logger.warning(f"      → Using fallback response")
        # Fallback response if LLM fails
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
        provider = _get_provider()
        system_instruction = "You are a trade pattern analyst. Always return valid JSON."
        result, pricing_info = await provider.generate_json(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.5
        )
        
        # Track pricing
        if pricing_info:
            tracker = get_pricing_tracker()
            tracker.record_request(pricing_info, "analyze_trading_pattern")
        
        logger.info(f"      → Parsed JSON response successfully")
        return result
    except Exception as e:
        provider = _get_provider()
        error_msg = normalize_error(e, provider.provider_name)
        logger.error(f"analyze_trading_pattern: {provider.provider_name.upper()} API error: {error_msg}")
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
        provider = _get_provider()
        system_instruction = "You are a customs compliance expert. Provide clear, concise risk assessments."
        result, pricing_info = await provider.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.6
        )
        
        # Track pricing
        if pricing_info:
            tracker = get_pricing_tracker()
            tracker.record_request(pricing_info, "generate_risk_assessment_insights")
        
        return result if result else "This shipment exhibits multiple risk factors that warrant careful review. The combination of entity verification results, blacklist status, and pattern analysis suggests elevated risk."
    except Exception as e:
        provider = _get_provider()
        error_msg = normalize_error(e, provider.provider_name)
        logger.error(f"generate_risk_assessment_insights: {provider.provider_name.upper()} API error: {error_msg}")
        return "This shipment exhibits multiple risk factors that warrant careful review. The combination of entity verification results, blacklist status, and pattern analysis suggests elevated risk."

