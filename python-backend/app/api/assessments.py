import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import ShipmentData, RiskAssessment
from app.services.risk_scoring import calculate_risk_score

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/assess", response_model=RiskAssessment)
async def assess_shipment(shipment_data: ShipmentData):
    """
    Perform comprehensive risk assessment on a shipment.
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"📥 NEW REQUEST: Shipment Assessment")
    logger.info(f"   Shipper: {shipment_data.shipper}")
    logger.info(f"   Importer: {shipment_data.importer}")
    logger.info(f"   Commodity: {shipment_data.commodity}")
    logger.info(f"   Origin: {shipment_data.origin}")
    logger.info(f"{'='*60}\n")
    
    try:
        # Convert Pydantic model to dict
        shipment_dict = shipment_data.model_dump()
        
        # Calculate risk score
        assessment = await calculate_risk_score(shipment_dict)
        
        logger.info(f"✅ Assessment complete: {assessment.riskLevel.upper()} risk (score: {assessment.riskScore})\n")
        return assessment
    except Exception as e:
        logger.error(f"✗ Assessment failed: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

