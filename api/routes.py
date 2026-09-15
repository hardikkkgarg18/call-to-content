from __future__ import annotations
import os
import time
import openai
from fastapi import APIRouter, HTTPException
from schemas.api import (
    AnalyzeRequest, AnalyzeResponse,
    EnrichProfileRequest, EnrichProfileResponse,
)
from pipeline.normalizer import normalize_transcript
from pipeline.chunker import chunk_transcript
from pipeline.speaker_classifier import filter_to_prospects
from pipeline.signal_extractor import extract_signals
from pipeline.insight_aggregator import aggregate_insights
from pipeline.content_generator import generate_content
from pipeline.profile_enricher import enrich_profile
from schemas.signals import ExtractedSignals, PainPoint, Objection, BuyingSignal

router = APIRouter()


def _get_client() -> openai.OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    return openai.OpenAI(api_key=api_key)


def _merge_signals(all_signals: list[ExtractedSignals]) -> ExtractedSignals:
    if len(all_signals) == 1:
        return all_signals[0]
    pain_points: list[PainPoint] = []
    objections: list[Objection] = []
    quotes: list[str] = []
    buying_signals: list[BuyingSignal] = []
    for s in all_signals:
        pain_points.extend(s.pain_points)
        objections.extend(s.objections)
        quotes.extend(s.quotes)
        buying_signals.extend(s.buying_signals)
    avg_confidence = sum(s.confidence_score for s in all_signals) / len(all_signals)
    return ExtractedSignals(
        pain_points=pain_points,
        objections=objections,
        quotes=list(dict.fromkeys(quotes)),
        buying_signals=buying_signals,
        confidence_score=round(avg_confidence, 3),
    )


@router.post("/enrich-profile", response_model=EnrichProfileResponse)
async def enrich_founder_profile(request: EnrichProfileRequest) -> EnrichProfileResponse:
    if not request.linkedin_url and not request.company_url:
        raise HTTPException(status_code=400, detail="Provide at least one URL")
    client = _get_client()
    result = enrich_profile(
        name=request.name,
        linkedin_url=request.linkedin_url,
        company_url=request.company_url,
        client=client,
    )
    return EnrichProfileResponse(**result)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_transcript(request: AnalyzeRequest) -> AnalyzeResponse:
    if len(request.transcript.strip()) < 100:
        raise HTTPException(status_code=400, detail="Transcript too short to analyze")

    client = _get_client()
    start = time.perf_counter()

    normalized = normalize_transcript(request.transcript)
    prospect_transcript, speaker_roles = filter_to_prospects(normalized, client)
    chunks = chunk_transcript(prospect_transcript)
    chunk_signals = [extract_signals(chunk, client) for chunk in chunks]
    merged = _merge_signals(chunk_signals)
    insights = aggregate_insights(merged, client)
    content = generate_content(insights, client, profile=request.founder_profile)

    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
    return AnalyzeResponse(
        signals=merged,
        insights=insights,
        content=content,
        speaker_roles=speaker_roles,
        processing_time_ms=elapsed_ms,
    )


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}
