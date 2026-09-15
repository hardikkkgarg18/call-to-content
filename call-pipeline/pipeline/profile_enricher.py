from __future__ import annotations
import json
import os
import re
import httpx
import openai

_MODEL = "gpt-4o-mini"


# ── LinkedIn ────────────────────────────────────────────────────────────────

def _slug_from_url(url: str) -> str | None:
    """Extract profile slug from a LinkedIn URL."""
    m = re.search(r'linkedin\.com/in/([^/?#]+)', url)
    return m.group(1).rstrip('/') if m else None


def _fetch_linkedin(slug: str) -> dict | None:
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        return None
    try:
        # Imported lazily so the core /analyze pipeline runs even if the
        # optional linkedin-api package isn't installed. Only /enrich-profile
        # needs it.
        from linkedin_api import Linkedin
        api = Linkedin(email, password)
        return api.get_profile(slug)
    except Exception:
        return None


def _parse_linkedin(data: dict) -> str:
    """Convert raw linkedin-api profile dict into readable text for GPT."""
    parts: list[str] = []

    name = " ".join(filter(None, [data.get("firstName"), data.get("lastName")]))
    if name:
        parts.append(f"Name: {name}")

    headline = data.get("headline", "")
    if headline:
        parts.append(f"Headline: {headline}")

    summary = data.get("summary", "")
    if summary:
        parts.append(f"About:\n{summary}")

    experiences = data.get("experience", [])
    if experiences:
        exp_lines = ["Experience:"]
        for e in experiences[:4]:
            title = e.get("title", "")
            company = e.get("companyName", "")
            desc = e.get("description", "")
            line = f"  - {title} at {company}"
            if desc:
                line += f": {desc[:200]}"
            exp_lines.append(line)
        parts.append("\n".join(exp_lines))

    skills = [s.get("name", "") for s in data.get("skills", [])[:10] if s.get("name")]
    if skills:
        parts.append(f"Skills: {', '.join(skills)}")

    return "\n\n".join(parts)


# ── Company website ──────────────────────────────────────────────────────────

def _fetch_website(url: str) -> str:
    """
    Fetch company website via Jina.ai reader — handles JS-heavy SPAs,
    returns clean markdown. Falls back to direct httpx fetch.
    """
    jina_url = f"https://r.jina.ai/{url}"
    try:
        with httpx.Client(timeout=15, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/plain",
        }) as client:
            r = client.get(jina_url)
            if r.status_code == 200 and len(r.text) > 200:
                return r.text[:6000]
    except Exception:
        pass

    # Direct fallback
    try:
        with httpx.Client(timeout=10, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }) as client:
            r = client.get(url)
            if r.status_code == 200:
                text = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", "", r.text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<[^>]+>", " ", text)
                text = re.sub(r"\s+", " ", text).strip()
                return text[:6000]
    except Exception:
        pass

    return ""


# ── GPT extraction ───────────────────────────────────────────────────────────

_EXTRACT_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_founder_profile",
        "description": "Extract structured founder and company context from raw profile/website text",
        "parameters": {
            "type": "object",
            "properties": {
                "founder_summary": {
                    "type": "string",
                    "description": "Who this founder is: background, what they've built, what drives them. 2-3 sentences.",
                },
                "company_summary": {
                    "type": "string",
                    "description": "What the company does, who it's for, what problem it solves. 2-3 sentences.",
                },
                "icp_inference": {
                    "type": "string",
                    "description": "Inferred ideal customer profile from the content.",
                },
                "tone_hints": {
                    "type": "string",
                    "description": "How this founder communicates — direct, technical, storytelling, contrarian, etc. Infer from their About section and writing.",
                },
            },
            "required": ["founder_summary", "company_summary", "icp_inference", "tone_hints"],
        },
    },
}


def _gpt_extract(name: str, context: str, client: openai.OpenAI) -> dict:
    response = client.chat.completions.create(
        model=_MODEL,
        tools=[_EXTRACT_TOOL],
        tool_choice={"type": "function", "function": {"name": "extract_founder_profile"}},
        messages=[{
            "role": "user",
            "content": (
                f"Extract founder and company context for {name}. "
                f"Focus on details that would help write authentic LinkedIn posts in their voice.\n\n"
                f"{context}"
            ),
        }],
    )
    return json.loads(response.choices[0].message.tool_calls[0].function.arguments)


# ── Public API ───────────────────────────────────────────────────────────────

def enrich_profile(
    name: str,
    linkedin_url: str | None,
    company_url: str | None,
    client: openai.OpenAI,
) -> dict:
    sections: list[str] = []
    linkedin_fetched = False
    company_fetched = False

    # LinkedIn
    if linkedin_url:
        slug = _slug_from_url(linkedin_url)
        if slug:
            data = _fetch_linkedin(slug)
            if data:
                text = _parse_linkedin(data)
                if text:
                    sections.append(f"=== LINKEDIN PROFILE ===\n{text}")
                    linkedin_fetched = True

    # Company website
    if company_url:
        text = _fetch_website(company_url)
        if text:
            sections.append(f"=== COMPANY WEBSITE ===\n{text}")
            company_fetched = True

    if not sections:
        return {
            "founder_summary": f"{name} is a founder.",
            "company_summary": "",
            "icp_inference": "",
            "tone_hints": "",
            "linkedin_fetched": False,
            "company_fetched": False,
        }

    extracted = _gpt_extract(name, "\n\n".join(sections), client)
    extracted["linkedin_fetched"] = linkedin_fetched
    extracted["company_fetched"] = company_fetched
    return extracted
