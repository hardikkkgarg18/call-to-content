from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from schemas.signals import ExtractedSignals, AggregatedInsights
from schemas.content import ContentOutput


class FounderProfile(BaseModel):
    name: str
    linkedin_url: Optional[str] = None
    company_url: Optional[str] = None
    # Populated after enrichment — not user-facing input fields
    founder_summary: Optional[str] = None
    company_summary: Optional[str] = None
    icp_inference: Optional[str] = None
    tone_hints: Optional[str] = None


class EnrichProfileRequest(BaseModel):
    name: str
    linkedin_url: Optional[str] = None
    company_url: Optional[str] = None


class EnrichProfileResponse(BaseModel):
    founder_summary: str
    company_summary: str
    icp_inference: str
    tone_hints: str
    linkedin_fetched: bool
    company_fetched: bool


class AnalyzeRequest(BaseModel):
    transcript: str
    title: Optional[str] = None
    founder_profile: Optional[FounderProfile] = None


class AnalyzeResponse(BaseModel):
    signals: ExtractedSignals
    insights: AggregatedInsights
    content: ContentOutput
    speaker_roles: dict[str, str]
    processing_time_ms: float
