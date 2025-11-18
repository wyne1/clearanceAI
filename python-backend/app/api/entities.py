import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import EntityResearchRequest, EntityResearch
from app.services.entity_research import research_entity

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/entities/research", response_model=EntityResearch)
async def research_entity_endpoint(request: EntityResearchRequest):
    """
    Research a specific entity (shipper, importer, or manufacturer).
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"📥 NEW REQUEST: Entity Research")
    logger.info(f"   Entity: {request.name}")
    logger.info(f"   Type: {request.type}")
    logger.info(f"   Country: {request.country or 'Not specified'}")
    logger.info(f"{'='*60}\n")
    
    try:
        result = await research_entity(
            entity_name=request.name,
            entity_type=request.type,
            country=request.country
        )
        
        logger.info(f"✅ Request completed successfully for {request.name}\n")
        return result
    except Exception as e:
        logger.error(f"✗ Request failed for {request.name}: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Entity research failed: {str(e)}")

