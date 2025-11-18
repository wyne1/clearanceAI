from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime


class ShipmentData(BaseModel):
    shipper: str
    importer: str
    manufacturer: Optional[str] = None
    commodity: str
    origin: str
    destination: Optional[str] = None
    value: Optional[float] = None
    weight: Optional[float] = None
    hsCode: Optional[str] = None
    notes: Optional[str] = None


class EntityCheck(BaseModel):
    entity: str
    status: str


class RiskAssessment(BaseModel):
    riskLevel: Literal["high", "medium", "low"]
    riskScore: int
    flags: List[str]
    entityChecks: dict[str, str]
    recommendations: List[str]
    patternAnalysis: str
    aiInsights: str


class EntityResearchRequest(BaseModel):
    name: str
    type: Literal["shipper", "importer", "manufacturer"]
    country: Optional[str] = None


class NewsItem(BaseModel):
    date: str
    source: str
    headline: str
    sentiment: Literal["negative", "neutral", "positive"]
    excerpt: str


class TradingPattern(BaseModel):
    commodity: str
    frequency: int
    lastShipment: str
    normalOrigins: List[str]


class BlacklistStatus(BaseModel):
    list60B: bool
    approvedManufacturer: bool
    otherFlags: List[str]


class EntityResearch(BaseModel):
    name: str
    type: str
    country: Optional[str]
    riskLevel: Literal["high", "medium", "low"]
    riskScore: int
    blacklistStatus: BlacklistStatus
    newsItems: List[NewsItem]
    tradingPatterns: List[TradingPattern]

