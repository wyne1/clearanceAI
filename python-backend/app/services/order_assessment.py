import logging
import uuid
from typing import List, Literal
from app.models.order_schemas import (
    OrderCreateRequest,
    OrderAssessmentResponse,
    EntityRiskSummary
)
from app.services.entity_research import research_entity
from app.services.blacklist_service import get_blacklist_status
from app.services.ai_service import generate_risk_assessment_insights

logger = logging.getLogger(__name__)


async def assess_entity_for_order(
    entity_name: str,
    entity_country: str,
    entity_type: str
) -> EntityRiskSummary:
    """
    Assess a single entity (shipper or buyer) for order pre-check.
    """
    logger.info(f"   📋 Assessing {entity_type}: {entity_name} ({entity_country})")
    
    # Get blacklist status
    blacklist_status = get_blacklist_status(entity_name, entity_type)
    is_blacklisted = blacklist_status.get("list60B", False)
    
    logger.info(f"      - Blacklist check: {'FLAGGED' if is_blacklisted else 'Clear'}")
    
    # Research entity using AI
    research_result = await research_entity(entity_name, entity_type, entity_country)
    
    # Compile flags
    flags = []
    if is_blacklisted:
        flags.append(f"{entity_type.capitalize()} is on 60B tax blacklist")
    flags.extend(blacklist_status.get("otherFlags", []))
    
    # Add flags from research
    for news in research_result.newsItems:
        if news.sentiment == "negative":
            flags.append(f"Negative news: {news.headline[:50]}...")
    
    # Generate news summary
    news_summary = None
    if research_result.newsItems:
        news_summary = "; ".join([
            f"{n.headline} ({n.sentiment})" 
            for n in research_result.newsItems[:3]
        ])
    
    logger.info(f"      - Risk level: {research_result.riskLevel.upper()}")
    logger.info(f"      - Flags found: {len(flags)}")
    
    return EntityRiskSummary(
        name=entity_name,
        country=entity_country,
        entity_type=entity_type,
        risk_level=research_result.riskLevel,
        risk_score=research_result.riskScore,
        is_blacklisted=is_blacklisted,
        flags=flags,
        news_summary=news_summary
    )


async def assess_order(request: OrderCreateRequest) -> OrderAssessmentResponse:
    """
    Perform comprehensive pre-check assessment on an order.
    Checks both shipper and buyer entities.
    """
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🔍 ORDER PRE-CHECK: {order_id}")
    logger.info(f"   Shipper: {request.shipper_name} ({request.shipper_country})")
    logger.info(f"   Buyer: {request.buyer_name} ({request.buyer_country})")
    logger.info(f"   Commodity: {request.commodity} from {request.origin}")
    logger.info(f"{'='*60}\n")
    
    # Step 1: Assess shipper
    logger.info("📦 Step 1/3: Assessing shipper...")
    shipper_assessment = await assess_entity_for_order(
        request.shipper_name,
        request.shipper_country,
        "shipper"
    )
    
    # Step 2: Assess buyer
    logger.info("\n🏢 Step 2/3: Assessing buyer...")
    buyer_assessment = await assess_entity_for_order(
        request.buyer_name,
        request.buyer_country,
        "buyer"
    )
    
    # Step 3: Calculate combined risk
    logger.info("\n⚖️  Step 3/3: Calculating combined risk...")
    
    # Combine flags from both entities
    all_flags = []
    all_flags.extend([f"[Shipper] {f}" for f in shipper_assessment.flags])
    all_flags.extend([f"[Buyer] {f}" for f in buyer_assessment.flags])
    
    # Calculate overall risk score (weighted average + penalty for blacklisted)
    combined_score = (shipper_assessment.risk_score + buyer_assessment.risk_score) // 2
    
    # Add penalty if either is blacklisted
    if shipper_assessment.is_blacklisted or buyer_assessment.is_blacklisted:
        combined_score = min(combined_score + 20, 100)
    
    # Determine overall risk level
    overall_risk_level: Literal["high", "medium", "low"]
    if combined_score >= 70 or shipper_assessment.risk_level == "high" or buyer_assessment.risk_level == "high":
        overall_risk_level = "high"
    elif combined_score >= 40 or shipper_assessment.risk_level == "medium" or buyer_assessment.risk_level == "medium":
        overall_risk_level = "medium"
    else:
        overall_risk_level = "low"
    
    # Determine if approval is required
    requires_approval = (
        overall_risk_level == "high" or
        shipper_assessment.is_blacklisted or
        buyer_assessment.is_blacklisted
    )
    
    # Set approval status
    approval_status: Literal["pending_approval", "auto_approved", "approved", "rejected"]
    if requires_approval:
        approval_status = "pending_approval"
    else:
        approval_status = "auto_approved"
    
    # Generate recommendations
    recommendations = []
    if shipper_assessment.is_blacklisted:
        recommendations.append("CRITICAL: Shipper is on 60B blacklist - consider rejecting order")
    if buyer_assessment.is_blacklisted:
        recommendations.append("CRITICAL: Buyer is on 60B blacklist - consider rejecting order")
    if shipper_assessment.risk_level == "high":
        recommendations.append("Request additional documentation from shipper")
    if buyer_assessment.risk_level == "high":
        recommendations.append("Verify buyer's payment history and creditworthiness")
    if overall_risk_level == "high":
        recommendations.append("Escalate to legal department for review")
        recommendations.append("Consider physical inspection of goods")
    elif overall_risk_level == "medium":
        recommendations.append("Proceed with enhanced monitoring")
    else:
        recommendations.append("Order appears low risk - proceed with standard process")
    
    # Generate AI summary
    entity_checks = {
        "shipper": f"{shipper_assessment.risk_level} risk (score: {shipper_assessment.risk_score})",
        "buyer": f"{buyer_assessment.risk_level} risk (score: {buyer_assessment.risk_score})"
    }
    blacklist_status = {
        "list60B": shipper_assessment.is_blacklisted or buyer_assessment.is_blacklisted,
        "approvedManufacturer": False,
        "otherFlags": all_flags
    }
    
    ai_summary = await generate_risk_assessment_insights(
        entity_checks,
        f"Order for {request.commodity} from {request.origin}. Shipper: {request.shipper_name}, Buyer: {request.buyer_name}",
        blacklist_status,
        all_flags
    )
    
    logger.info(f"\n✅ ORDER PRE-CHECK COMPLETE: {order_id}")
    logger.info(f"   - Overall Risk: {overall_risk_level.upper()} (score: {combined_score})")
    logger.info(f"   - Requires Approval: {requires_approval}")
    logger.info(f"   - Status: {approval_status}")
    logger.info(f"   - Total Flags: {len(all_flags)}")
    logger.info(f"{'='*60}\n")
    
    return OrderAssessmentResponse(
        order_id=order_id,
        overall_risk_level=overall_risk_level,
        overall_risk_score=combined_score,
        requires_approval=requires_approval,
        approval_status=approval_status,
        shipper_assessment=shipper_assessment,
        buyer_assessment=buyer_assessment,
        flags=all_flags,
        recommendations=recommendations,
        ai_summary=ai_summary
    )

