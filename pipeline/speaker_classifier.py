from __future__ import annotations
import json
import re
import openai
from dataclasses import dataclass

_MODEL = "gpt-4o-mini"

_SPEAKER_RE = re.compile(
    r'^([^\n:]{1,40}):\s*(.+?)(?=\n[^\n:]{1,40}:|\Z)',
    re.MULTILINE | re.DOTALL
)

_CLASSIFY_TOOL = {
    "type": "function",
    "function": {
        "name": "classify_speaker_roles",
        "description": "Classify each speaker in a B2B sales or discovery call as seller or prospect",
        "parameters": {
            "type": "object",
            "properties": {
                "speakers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "speaker": {"type": "string"},
                            "role": {
                                "type": "string",
                                "enum": ["seller", "prospect"],
                            },
                        },
                        "required": ["speaker", "role"],
                    },
                }
            },
            "required": ["speakers"],
        },
    },
}

_SYSTEM = """\
You are analyzing a B2B sales or discovery call transcript. Classify each speaker as:

- "seller": founders, AEs, solution engineers, anyone representing the product or company being sold.
  They ask discovery questions, pitch solutions, say "our product / our team / we built".

- "prospect": potential buyers, evaluators, customers. They describe their current problems,
  express frustrations, share internal context, ask about pricing or implementation.

There may be multiple sellers and multiple prospects. Classify every speaker listed.\
"""


@dataclass
class SpeakerTurn:
    speaker: str
    text: str


def _parse_turns(transcript: str) -> list[SpeakerTurn]:
    turns = []
    for m in _SPEAKER_RE.finditer(transcript):
        speaker = m.group(1).strip()
        text = m.group(2).strip()
        if text:
            turns.append(SpeakerTurn(speaker=speaker, text=text))
    return turns


def _build_speaker_samples(turns: list[SpeakerTurn], max_per_speaker: int = 3) -> dict[str, list[str]]:
    samples: dict[str, list[str]] = {}
    for turn in turns:
        bucket = samples.setdefault(turn.speaker, [])
        if len(bucket) < max_per_speaker:
            bucket.append(turn.text[:400])
    return samples


def classify_speakers(transcript: str, client: openai.OpenAI) -> dict[str, str]:
    """Return {speaker_name: 'seller'|'prospect'} for all speakers in the transcript."""
    turns = _parse_turns(transcript)
    if not turns:
        return {}

    samples = _build_speaker_samples(turns)
    context = "\n\n".join(
        f"Speaker: {spk}\n" + "\n".join(f"  - {u}" for u in utterances)
        for spk, utterances in samples.items()
    )

    response = client.chat.completions.create(
        model=_MODEL,
        tools=[_CLASSIFY_TOOL],
        tool_choice={"type": "function", "function": {"name": "classify_speaker_roles"}},
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Classify every speaker in this call:\n\n{context}"},
        ],
    )
    args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    return {s["speaker"]: s["role"] for s in args["speakers"]}


def _resolve_role(speaker: str, roles: dict[str, str]) -> str | None:
    """
    Match a turn's speaker label to the roles dict, tolerating name variations.
    e.g. "Alice (Founder)" matches classified key "Alice".
    """
    if speaker in roles:
        return roles[speaker]
    spk_lower = speaker.lower()
    for name, role in roles.items():
        if name.lower() in spk_lower or spk_lower in name.lower():
            return role
    return None


def filter_to_prospects(transcript: str, client: openai.OpenAI) -> tuple[str, dict[str, str]]:
    """
    Classify all speakers, then return only the prospect turns as a clean transcript.
    Also returns the full role map so callers can surface it to the user.

    If no speaker labels are detected, returns the original transcript unchanged
    and an empty role map — the caller should handle this gracefully.
    """
    turns = _parse_turns(transcript)
    if not turns:
        return transcript, {}

    roles = classify_speakers(transcript, client)

    prospect_turns = [
        f"{t.speaker}: {t.text}"
        for t in turns
        if _resolve_role(t.speaker, roles) == "prospect"
    ]

    if not prospect_turns:
        # Fallback: couldn't isolate prospects — return full transcript
        return transcript, roles

    return "\n\n".join(prospect_turns), roles
