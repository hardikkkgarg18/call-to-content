from __future__ import annotations
import json
import openai
from schemas.signals import ExtractedSignals, PainPoint, Objection, BuyingSignal

_MODEL = "gpt-4o-mini"

_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_conversation_signals",
        "description": "Extract structured customer intelligence signals from a B2B sales or discovery call transcript.",
        "parameters": {
            "type": "object",
            "properties": {
                "pain_points": {
                    "type": "array",
                    "description": "Explicit problems, frustrations, or challenges the customer expresses",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "intensity": {"type": "string", "enum": ["low", "medium", "high"]},
                            "exact_quote": {"type": "string"},
                        },
                        "required": ["description", "intensity"],
                    },
                },
                "objections": {
                    "type": "array",
                    "description": "Reasons for hesitation, pushback, concerns, or resistance",
                    "items": {
                        "type": "object",
                        "properties": {
                            "objection": {"type": "string"},
                            "context": {"type": "string"},
                        },
                        "required": ["objection", "context"],
                    },
                },
                "quotes": {
                    "type": "array",
                    "description": "Exact verbatim customer phrases — memorable, revealing, or copy-worthy",
                    "items": {"type": "string"},
                },
                "buying_signals": {
                    "type": "array",
                    "description": "Indicators of purchase intent, urgency, or genuine interest",
                    "items": {
                        "type": "object",
                        "properties": {
                            "signal": {"type": "string"},
                            "strength": {"type": "string", "enum": ["weak", "moderate", "strong"]},
                        },
                        "required": ["signal", "strength"],
                    },
                },
                "confidence_score": {
                    "type": "number",
                    "description": "Extraction quality based on transcript clarity (0.0–1.0)",
                },
            },
            "required": ["pain_points", "objections", "quotes", "buying_signals", "confidence_score"],
        },
    },
}

_SYSTEM = """\
You are a specialized customer intelligence analyst. Extract signals from B2B call transcripts.

Rules:
- Extract REAL pain points the customer expresses, not what the seller assumes
- Capture EXACT customer quotes verbatim — do not paraphrase or clean up their language
- Distinguish customer voice from seller voice — only customer signals matter
- Buying signals must be genuine (budget mentions, urgency, next-step asks, executive buy-in)
- If transcript quality is poor, reflect it in a low confidence_score
- Do not invent or infer signals not present in the text\
"""


def extract_signals(transcript: str, client: openai.OpenAI) -> ExtractedSignals:
    response = client.chat.completions.create(
        model=_MODEL,
        tools=[_TOOL],
        tool_choice={"type": "function", "function": {"name": "extract_conversation_signals"}},
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Extract all customer intelligence signals from this transcript:\n\n{transcript}"},
        ],
    )
    args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    return ExtractedSignals(
        pain_points=[PainPoint(**p) for p in args.get("pain_points", [])],
        objections=[Objection(**o) for o in args.get("objections", [])],
        quotes=args.get("quotes", []),
        buying_signals=[BuyingSignal(**b) for b in args.get("buying_signals", [])],
        confidence_score=args.get("confidence_score", 0.5),
    )
