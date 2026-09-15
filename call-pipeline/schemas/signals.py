from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class IntensityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class SignalStrength(str, Enum):
    weak = "weak"
    moderate = "moderate"
    strong = "strong"


class PainPoint(BaseModel):
    description: str
    intensity: IntensityLevel
    exact_quote: Optional[str] = None


class Objection(BaseModel):
    objection: str
    context: str


class BuyingSignal(BaseModel):
    signal: str
    strength: SignalStrength


class ExtractedSignals(BaseModel):
    pain_points: list[PainPoint] = Field(default_factory=list)
    objections: list[Objection] = Field(default_factory=list)
    quotes: list[str] = Field(default_factory=list)
    buying_signals: list[BuyingSignal] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)


class MarketInsight(BaseModel):
    insight: str
    supporting_signals: list[str]


class AggregatedInsights(BaseModel):
    primary_pain_theme: str
    key_objection_pattern: Optional[str] = None
    strongest_quotes: list[str] = Field(default_factory=list)
    market_insights: list[MarketInsight] = Field(default_factory=list)
    icp_signals: list[str] = Field(default_factory=list)
    urgency_score: float = Field(ge=0.0, le=1.0)
