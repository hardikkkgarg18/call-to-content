from __future__ import annotations
import json
import openai
from schemas.signals import AggregatedInsights
from schemas.content import ContentOutput, LinkedInDraft
from schemas.api import FounderProfile

_MODEL = "gpt-4o-mini"

_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_founder_content",
        "description": "Generate founder-style LinkedIn content from structured market insights",
        "parameters": {
            "type": "object",
            "properties": {
                "hook": {
                    "type": "string",
                    "description": "Opening 1-2 sentences — surprising, counterintuitive, or pattern-breaking",
                },
                "body": {
                    "type": "string",
                    "description": "Main body — 3-5 short paragraphs sharing the market insight in founder voice",
                },
                "cta": {
                    "type": "string",
                    "description": "Closing observation or question — never a pitch",
                },
                "full_post": {
                    "type": "string",
                    "description": "Complete formatted LinkedIn post, ready to publish",
                },
                "key_phrases_for_copy": {
                    "type": "array",
                    "description": "Exact customer phrases to use verbatim in future marketing copy",
                    "items": {"type": "string"},
                },
            },
            "required": ["hook", "body", "cta", "full_post", "key_phrases_for_copy"],
        },
    },
}

_BASE_RULES = """\
Style rules:
- Write in first person as this specific founder — use their name, company context, and voice
- Lead with the most surprising or counterintuitive insight from the call
- Share the MARKET insight, not the product or solution
- Short paragraphs (1-3 sentences each)
- Use the customer's exact language where possible — do not sanitize it
- End with an observation or question, never a pitch
- Max 3 relevant hashtags — no hashtag spam
- Banned phrases: "I'm excited to share", "game-changer", "paradigm shift", "thrilled to announce"
- Target reaction: "I've felt this too" or "I never thought of it that way"\
"""


def _build_system_prompt(profile: FounderProfile | None) -> str:
    if not profile:
        return f"You are a founder who just finished a customer discovery call. Write a LinkedIn post.\n\n{_BASE_RULES}"

    context_lines = [f"You are {profile.name}."]

    if profile.founder_summary:
        context_lines.append(f"About you: {profile.founder_summary}")
    if profile.company_summary:
        context_lines.append(f"What you're building: {profile.company_summary}")
    if profile.icp_inference:
        context_lines.append(f"Your market: {profile.icp_inference}")
    if profile.tone_hints:
        context_lines.append(f"Your communication style: {profile.tone_hints}")

    context_lines.append("\nYou just finished a customer discovery call. Write a LinkedIn post sharing what you learned.")
    context_lines.append(f"\n{_BASE_RULES}")
    context_lines.append(
        f"\nImportant: Sound unmistakably like {profile.name} — "
        "specific to your market, not generic founder wisdom. "
        "Use the customer's exact phrases wherever they appear in the insights."
    )

    return "\n".join(context_lines)


def generate_content(
    insights: AggregatedInsights,
    client: openai.OpenAI,
    profile: FounderProfile | None = None,
) -> ContentOutput:
    system = _build_system_prompt(profile)

    response = client.chat.completions.create(
        model=_MODEL,
        tools=[_TOOL],
        tool_choice={"type": "function", "function": {"name": "generate_founder_content"}},
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    "Generate a LinkedIn post from these market insights. "
                    "Use the customer's exact phrases where they appear in the insights.\n\n"
                    f"{insights.model_dump_json(indent=2)}"
                ),
            },
        ],
    )
    args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    return ContentOutput(
        linkedin_draft=LinkedInDraft(
            hook=args["hook"],
            body=args["body"],
            cta=args["cta"],
            full_post=args["full_post"],
        ),
        key_phrases_for_copy=args.get("key_phrases_for_copy", []),
    )
