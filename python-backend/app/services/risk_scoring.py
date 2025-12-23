from typing import Dict, List, Optional
from app.services.blacklist_service import get_blacklist_status
from app.services.pattern_service import check_commodity_origin_match, analyze_trading_pattern_anomaly
from app.services.entity_research import research_entity
from app.services.ai_service import generate_risk_assessment_insights, analyze_trading_pattern
from app.models.schemas import RiskAssessment, EntityCheck


async def calculate_risk_score(shipment_data: Dict[str, any]) -> RiskAssessment:
    """
    Comprehensive risk assessment combining:
    - Entity research (shipper, importer, manufacturer)
    - Blacklist checks
    - Pattern analysis (commodity-origin matching)
    - Trading pattern anomalies
    """
    shipper = shipment_data.get("shipper", "")
    importer = shipment_data.get("importer", "")
    manufacturer = shipment_data.get("manufacturer")
    commodity = shipment_data.get("commodity", "")
    origin = shipment_data.get("origin", "")
    
    flags: List[str] = []
    entity_checks: Dict[str, str] = {}
    recommendations: List[str] = []
    risk_score = 0
    
    # Research shipper
    shipper_research = await research_entity(shipper, "shipper")
    shipper_blacklist = shipper_research.blacklistStatus
    
    if shipper_blacklist.list60B:
        flags.append(f"Shipper on 60B List: {shipper}")
        risk_score += 30
        recommendations.append("Reject shipment - shipper is on tax blacklist")
    elif len(shipper_blacklist.otherFlags) > 0:
        flags.extend(shipper_blacklist.otherFlags)
        risk_score += 15
    
    if shipper_research.riskLevel == "high":
        risk_score += 25
        flags.append(f"High-risk shipper: {shipper}")
    elif shipper_research.riskLevel == "medium":
        risk_score += 10
    
    entity_checks["shipper"] = (
        "Clean - No blacklist entries" if not shipper_blacklist.list60B and shipper_research.riskLevel == "low"
        else f"Warning - {shipper_research.riskLevel} risk entity"
    )
    
    # Research importer
    importer_research = await research_entity(importer, "importer")
    importer_blacklist = importer_research.blacklistStatus
    
    if importer_blacklist.list60B:
        flags.append(f"Importer on 60B List: {importer}")
        risk_score += 30
        recommendations.append("Reject shipment - importer is on tax blacklist")
    elif len(importer_blacklist.otherFlags) > 0:
        flags.extend(importer_blacklist.otherFlags)
        risk_score += 15
    
    if importer_research.riskLevel == "high":
        risk_score += 20
    elif importer_research.riskLevel == "medium":
        risk_score += 8
    
    entity_checks["importer"] = (
        "Clean - No issues found" if not importer_blacklist.list60B and importer_research.riskLevel == "low"
        else f"Warning - {importer_research.riskLevel} risk entity"
    )
    
    # Check manufacturer if provided
    if manufacturer:
        manufacturer_blacklist = get_blacklist_status(manufacturer, "manufacturer", commodity)
        if manufacturer_blacklist.get("list60B"):
            flags.append(f"Manufacturer on 60B List: {manufacturer}")
            risk_score += 25
        elif not manufacturer_blacklist.get("approvedManufacturer"):
            flags.append(f"Manufacturer not on approved list for {commodity}")
            risk_score += 10
            recommendations.append("Request manufacturer certification")
        
        entity_checks["manufacturer"] = (
            "Verified" if manufacturer_blacklist.get("approvedManufacturer")
            else "Not on approved manufacturer list for this commodity"
        )
    else:
        entity_checks["manufacturer"] = "Not provided"
    
    # Pattern analysis: commodity-origin matching
    origin_check = check_commodity_origin_match(commodity, origin)
    if not origin_check.get("match", True):
        flags.append(origin_check.get("flag", "Commodity Origin Mismatch"))
        if origin_check.get("riskLevel") == "high":
            risk_score += 25
            recommendations.append("Request additional documentation on manufacturing origin")
        else:
            risk_score += 15
            recommendations.append("Verify origin documentation")
    
    # Trading pattern analysis using OpenAI
    shipper_patterns = [
        {
            "commodity": p.commodity,
            "frequency": p.frequency,
            "normalOrigins": p.normalOrigins
        }
        for p in shipper_research.tradingPatterns
    ]
    
    pattern_analysis_result = await analyze_trading_pattern(
        shipper,
        commodity,
        origin,
        shipper_patterns
    )
    
    pattern_analysis_text = pattern_analysis_result.get("analysis", "")
    if pattern_analysis_result.get("isAnomaly", False):
        anomaly_type = pattern_analysis_result.get("anomalyType", "unknown")
        if anomaly_type != "none":
            flags.append(f"Trading Pattern Anomaly: {anomaly_type}")
            risk_score += 15
    
    # If no specific pattern analysis, use the origin check analysis
    if not pattern_analysis_text:
        pattern_analysis_text = origin_check.get("analysis", "Pattern analysis unavailable.")
    
    # Generate comprehensive pattern analysis text
    if shipper_patterns:
        typical_commodities = [p.get("commodity") for p in shipper_patterns]
        if commodity not in typical_commodities:
            pattern_analysis_text = (
                f"Shipper typically handles {', '.join(typical_commodities)}. "
                f"This commodity ({commodity}) represents significant deviation from normal trading pattern."
            )
    
    # Generate AI insights combining all factors
    combined_blacklist_status = {
        "list60B": shipper_blacklist.list60B or importer_blacklist.list60B,
        "approvedManufacturer": manufacturer_blacklist.get("approvedManufacturer", False) if manufacturer else False,
        "otherFlags": shipper_blacklist.otherFlags + importer_blacklist.otherFlags
    }
    
    ai_insights = await generate_risk_assessment_insights(
        entity_checks,
        pattern_analysis_text,
        combined_blacklist_status,
        flags
    )
    
    # Determine risk level based on score
    if risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Add default recommendations if none exist
    if not recommendations:
        if risk_level == "high":
            recommendations.append("Require additional documentation and verification")
            recommendations.append("Consider physical inspection of cargo")
        elif risk_level == "medium":
            recommendations.append("Proceed with standard documentation review")
            recommendations.append("Monitor for any additional red flags")
        else:
            recommendations.append("Proceed with standard documentation review")
            recommendations.append("No additional inspection required")
    
    # Cap score at 100
    risk_score = min(risk_score, 100)
    
    return RiskAssessment(
        riskLevel=risk_level,
        riskScore=risk_score,
        flags=flags,
        entityChecks=entity_checks,
        recommendations=recommendations,
        patternAnalysis=pattern_analysis_text,
        aiInsights=ai_insights
    )

