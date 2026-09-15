from __future__ import annotations
import json
import openai
from schemas.signals import ExtractedSignals, AggregatedInsights, MarketInsight

_MODEL = "gpt-4o-mini"

_TOOL = {
    "type": "function",
    "function": {
        "name": "aggregate_market_insights",
        "description": "Synthesize extracted call signals into higher-order market insights",
        "parameters": {
            "type": "object",
            "properties": {
                "primary_pain_theme": {
                    "type": "string",
                    "description": "Single dominant pain theme unifying all pain points",
                },
                "key_objection_pattern": {
                    "type": "string",
                    "description": "Most significant or recurring objection pattern (omit if none)",
                },
                "strongest_quotes": {
                    "type": "array",
                    "description": "Top 3 most powerful or revealing customer quotes",
                    "items": {"type": "string"},
                },
                "market_insights": {
                    "type": "array",
                    "description": "Synthesized market-level insights — what signals reveal about the market, not just this call",
                    "items": {
                        "type": "object",
                        "properties": {
                            "insight": {"type": "string"},
                            "supporting_signals": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["insight", "supporting_signals"],
                    },
                },
                "icp_signals": {
                    "type": "array",
                    "description": "Characteristics that reveal this customer's ideal customer profile",
                    "items": {"type": "string"},
                },
                "urgency_score": {
                    "type": "number",
                    "description": "How urgently this prospect needs a solution (0.0–1.0)",
                },
            },
            "required": ["primary_pain_theme", "strongest_quotes", "market_insights", "icp_signals", "urgency_score"],
        },
    },
}


def aggregate_insights(
    signals: ExtractedSignals,
    client: openai.OpenAI,
) -> AggregatedInsights:
    response = client.chat.completions.create(
        model=_MODEL,
        tools=[_TOOL],
        tool_choice={"type": "function", "function": {"name": "aggregate_market_insights"}},
        messages=[{
            "role": "user",
            "content": (
                "Synthesize these extracted call signals into higher-order market insights. "
                "Focus on patterns and what they reveal about the market, not just this call.\n\n"
                f"{signals.model_dump_json(indent=2)}"
            ),
        }],
    )
    args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    return AggregatedInsights(
        primary_pain_theme=args["primary_pain_theme"],
        key_objection_pattern=args.get("key_objection_pattern"),
        strongest_quotes=args.get("strongest_quotes", [])[:3],
        market_insights=[MarketInsight(**m) for m in args.get("market_insights", [])],
        icp_signals=args.get("icp_signals", []),
        urgency_score=args.get("urgency_score", 0.5),
    )
