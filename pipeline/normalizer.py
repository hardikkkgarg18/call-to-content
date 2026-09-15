from __future__ import annotations
import re

# Matches [Name] HH:MM lines (Google Meet / Fireflies / Otter export format)
_BRACKET_HEADER = re.compile(r'^\[([^\]]+)\]\s+\d{1,2}:\d{2}\s*$', re.MULTILINE)

# Matches standard Speaker: text format
_STANDARD_SPEAKER = re.compile(
    r'^\s*((?:Speaker\s*\d+|Host|Guest|Customer|Prospect|Founder|Interviewer|You|Me))\s*:',
    re.MULTILINE | re.IGNORECASE,
)


def _convert_bracket_format(text: str) -> str:
    """
    Convert [Name] HH:MM\\ntext format → Name: text, merging consecutive
    turns from the same speaker (Google Meet captions split mid-sentence).
    """
    lines = text.splitlines()
    turns: list[tuple[str, list[str]]] = []  # [(speaker, [text_parts])]

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r'^\[([^\]]+)\]\s+\d{1,2}:\d{2}\s*$', line)
        if m:
            speaker = m.group(1).strip()
            # Merge with previous turn if same speaker (fragmented captions)
            if turns and turns[-1][0] == speaker:
                pass  # just continue appending to the last turn
            else:
                turns.append((speaker, []))
        else:
            if line and turns:
                turns[-1][1].append(line)
        i += 1

    result = []
    for speaker, parts in turns:
        text_body = ' '.join(parts).strip()
        if text_body:
            result.append(f"{speaker}: {text_body}")

    return '\n\n'.join(result)


def normalize_transcript(raw: str) -> str:
    text = raw.strip()

    # Detect bracket format first — takes priority
    if _BRACKET_HEADER.search(text):
        return _convert_bracket_format(text)

    # Standard format: strip bare timestamps (00:00 / [00:00] / (00:00))
    text = re.sub(r'[\[\(]?\d{1,2}:\d{2}(?::\d{2})?[\]\)]?', '', text)
    # Normalize known speaker labels to consistent newline-prefixed format
    text = _STANDARD_SPEAKER.sub(lambda m: f"\n{m.group(1).strip()}:", text)
    # Collapse excess blank lines and spaces
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()
