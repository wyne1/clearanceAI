import logging
from typing import Dict, List, Optional, Any, Literal
from app.services.openai_service import research_entity_news
from app.services.blacklist_service import get_blacklist_status
from app.models.schemas import EntityResearch, NewsItem, TradingPattern, BlacklistStatus

logger = logging.getLogger(__name__)


async def research_entity(
    entity_name: str,
    entity_type: str,
    country: Optional[str] = None,
    historical_patterns: Optional[List[Dict[str, Any]]] = None
) -> EntityResearch:
    """
    Comprehensive entity research combining OpenAI news analysis and blacklist checks.
    """
    logger.info(f"🔍 Starting entity research for: {entity_name} (type: {entity_type}, country: {country or 'Unknown'})")
    
    # Get blacklist status
    logger.info(f"📋 Step 1/4: Checking blacklist status for {entity_name}...")
    blacklist_status_dict = get_blacklist_status(entity_name, entity_type)
    blacklist_status = BlacklistStatus(
        list60B=blacklist_status_dict.get("list60B", False),
        approvedManufacturer=blacklist_status_dict.get("approvedManufacturer", False),
        otherFlags=blacklist_status_dict.get("otherFlags", [])
    )
    
    logger.info(f"   ✓ Blacklist check complete:")
    logger.info(f"     - 60B List: {'FLAGGED' if blacklist_status.list60B else 'Clear'}")
    logger.info(f"     - Approved Manufacturer: {'Yes' if blacklist_status.approvedManufacturer else 'No'}")
    logger.info(f"     - Other Flags: {len(blacklist_status.otherFlags)}")
    
    # Research entity news using OpenAI
    logger.info(f"🤖 Step 2/4: Researching entity news using OpenAI GPT-4o for {entity_name}...")
    logger.info(f"   (This may take 10-30 seconds)")
    news_data = await research_entity_news(entity_name, entity_type, country)
    
    # Convert news items to schema
    logger.info(f"   ✓ OpenAI research complete. Processing {len(news_data.get('newsItems', []))} news items...")
    news_items = [
        NewsItem(
            date=item.get("date", "2024-11-15"),
            source=item.get("source", "Unknown"),
            headline=item.get("headline", ""),
            sentiment=item.get("sentiment", "neutral"),
            excerpt=item.get("excerpt", "")
        )
        for item in news_data.get("newsItems", [])
    ]
    
    negative_news_count = len([n for n in news_items if n.sentiment == "negative"])
    logger.info(f"   ✓ Found {len(news_items)} news items ({negative_news_count} negative, {len([n for n in news_items if n.sentiment == 'positive'])} positive)")
    
    # Convert historical patterns to schema
    logger.info(f"📊 Step 3/4: Processing trading patterns...")
    trading_patterns = []
    if historical_patterns:
        for pattern in historical_patterns:
            trading_patterns.append(
                TradingPattern(
                    commodity=pattern.get("commodity", ""),
                    frequency=pattern.get("frequency", 0),
                    lastShipment=pattern.get("lastShipment", "2024-11-15"),
                    normalOrigins=pattern.get("normalOrigins", [])
                )
            )
        logger.info(f"   ✓ Loaded {len(trading_patterns)} historical trading patterns")
    else:
        logger.info(f"   ✓ No historical patterns provided")
    
    # Calculate risk level and score based on findings
    logger.info(f"⚖️  Step 4/4: Calculating risk score...")
    risk_flags = news_data.get("riskFlags", [])
    if blacklist_status.list60B:
        risk_flags.append("Entity on 60B tax blacklist")
    risk_flags.extend(blacklist_status.otherFlags)
    
    # Determine risk level
    risk_level: Literal["high", "medium", "low"]
    if blacklist_status.list60B or len([n for n in news_items if n.sentiment == "negative"]) >= 2:
        risk_level = "high"
        risk_score = 85 + len(risk_flags) * 2
        logger.info(f"   ✓ Risk level: HIGH (base: 85, flags: {len(risk_flags)})")
    elif len([n for n in news_items if n.sentiment == "negative"]) >= 1 or len(risk_flags) > 0:
        risk_level = "medium"
        risk_score = 50 + len(risk_flags) * 5
        logger.info(f"   ✓ Risk level: MEDIUM (base: 50, flags: {len(risk_flags)})")
    else:
        risk_level = "low"
        risk_score = 15 + len(risk_flags) * 3
        logger.info(f"   ✓ Risk level: LOW (base: 15, flags: {len(risk_flags)})")
    
    # Cap score at 100
    risk_score = min(risk_score, 100)
    
    logger.info(f"✅ Entity research complete for {entity_name}:")
    logger.info(f"   - Final Risk Level: {risk_level.upper()}")
    logger.info(f"   - Final Risk Score: {risk_score}/100")
    logger.info(f"   - Total Risk Flags: {len(risk_flags)}")
    logger.info(f"   - News Items: {len(news_items)}")
    logger.info(f"   - Trading Patterns: {len(trading_patterns)}")
    logger.info("=" * 60)
    
    return EntityResearch(
        name=entity_name,
        type=entity_type,
        country=country,
        riskLevel=risk_level,
        riskScore=risk_score,
        blacklistStatus=blacklist_status,
        newsItems=news_items,
        tradingPatterns=trading_patterns
    )

