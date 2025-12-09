from pydantic import BaseModel
from typing import List, Optional, Literal


class OrderCreateRequest(BaseModel):
    """Request schema for creating a new order with pre-check."""
    # Shipper (seller) details
    shipper_name: str
    shipper_country: str
    
    # Buyer details
    buyer_name: str
    buyer_country: str
    
    # Order details
    commodity: str
    origin: str
    value: Optional[float] = None
    order_reference: Optional[str] = None


class EntityRiskSummary(BaseModel):
    """Summary of risk assessment for a single entity."""
    name: str
    country: str
    entity_type: str
    risk_level: Literal["high", "medium", "low"]
    risk_score: int
    is_blacklisted: bool
    flags: List[str]
    news_summary: Optional[str] = None


class OrderAssessmentResponse(BaseModel):
    """Response schema for order pre-check assessment."""
    order_id: str
    overall_risk_level: Literal["high", "medium", "low"]
    overall_risk_score: int
    requires_approval: bool
    approval_status: Literal["pending_approval", "auto_approved", "approved", "rejected"]
    
    shipper_assessment: EntityRiskSummary
    buyer_assessment: EntityRiskSummary
    
    flags: List[str]
    recommendations: List[str]
    ai_summary: str

