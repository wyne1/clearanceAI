import logging
from fastapi import APIRouter, HTTPException
from app.models.order_schemas import OrderCreateRequest, OrderAssessmentResponse
from app.services.order_assessment import assess_order

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/orders/create", response_model=OrderAssessmentResponse)
async def create_order_with_precheck(request: OrderCreateRequest):
    """
    Create a new order with automated pre-check.
    Assesses both shipper and buyer for risk factors.
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"📥 NEW REQUEST: Order Creation Pre-Check")
    logger.info(f"   Shipper: {request.shipper_name} ({request.shipper_country})")
    logger.info(f"   Buyer: {request.buyer_name} ({request.buyer_country})")
    logger.info(f"   Commodity: {request.commodity}")
    logger.info(f"   Origin: {request.origin}")
    if request.order_reference:
        logger.info(f"   Reference: {request.order_reference}")
    logger.info(f"{'='*60}\n")
    
    try:
        result = await assess_order(request)
        
        logger.info(f"✅ Order pre-check completed: {result.order_id}")
        logger.info(f"   Status: {result.approval_status}")
        logger.info(f"   Risk: {result.overall_risk_level.upper()}\n")
        
        return result
    except Exception as e:
        logger.error(f"✗ Order pre-check failed: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Order pre-check failed: {str(e)}")

