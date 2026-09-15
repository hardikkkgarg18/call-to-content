from __future__ import annotations
from pydantic import BaseModel


class LinkedInDraft(BaseModel):
    hook: str
    body: str
    cta: str
    full_post: str


class ContentOutput(BaseModel):
    linkedin_draft: LinkedInDraft
    key_phrases_for_copy: list[str]
