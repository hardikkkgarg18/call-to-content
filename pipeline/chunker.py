from __future__ import annotations
import re

_SPEAKER_TURN = re.compile(
    r'(?=\n(?:Speaker\s*\d+|Host|Guest|Customer|Prospect|Founder|Interviewer|You|Me)\s*:)',
    re.IGNORECASE
)
_OVERLAP_TURNS = 2


def chunk_transcript(transcript: str, max_chars: int = 12000) -> list[str]:
    if len(transcript) <= max_chars:
        return [transcript]

    turns = [t.strip() for t in _SPEAKER_TURN.split(transcript) if t.strip()]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for turn in turns:
        turn_len = len(turn)
        if current_len + turn_len > max_chars and current:
            chunks.append("\n\n".join(current))
            current = current[-_OVERLAP_TURNS:]
            current_len = sum(len(p) for p in current)
        current.append(turn)
        current_len += turn_len

    if current:
        chunks.append("\n\n".join(current))

    return chunks
