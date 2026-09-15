"""Quick validation script — run while the server is up: python test_pipeline.py"""
from __future__ import annotations
import asyncio
import json
import httpx

BASE_URL = "http://localhost:8001/api/v1"

# Real-feeling sample transcript for validation
SAMPLE_TRANSCRIPT = """\
Host: Tell me about your current workflow for understanding what your customers want.

Customer: Honestly, it's a mess. We do calls all day but nothing sticks. Like, I'll have a great
discovery call on Monday, learn something crucial about why people churn, and by Thursday when
we're writing the email campaign nobody remembers what was said. It's in someone's notes, maybe.
Or maybe not.

Host: How do you currently capture those insights?

Customer: We have a Notion doc that's supposed to be the customer insight repository. Three people
have edit access and nobody updates it. I think the last entry is from February. We've tried Otter,
we've tried Gong lite — they give us transcripts and that's it. Transcripts don't tell me what's
actually important.

Host: What would tell you what's actually important?

Customer: If I could read 10 calls and know — okay, the number one thing blocking people from
converting is X, that would change everything. Right now I spend an hour every week reading through
random transcripts hoping to spot patterns. It's not scalable. And I'm the founder, I shouldn't
be doing this.

Host: What's the cost of not solving this?

Customer: We're running campaigns based on what we THINK the customer wants. Not what they actually
said. We had a product launch last month — completely missed. The messaging was off. In hindsight,
three customers had literally told us the exact problem in calls two months earlier. We just didn't
connect the dots.

Host: Have you looked at solutions?

Customer: Chorus, Gong — too expensive and too enterprise. They're built for 50-person sales teams
with CRM integrations and coaching workflows. We're 4 people. We don't need call coaching. We need
signal extraction. There's a gap in the market for something lighter.

Host: What would you pay for something that solved this?

Customer: Honestly if it actually worked? We'd pay $200-300 a month without thinking twice. The
value of knowing what your market actually wants — that's priceless. But I need to see it work first.
"""


async def run():
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("Checking health...")
        health = await client.get(f"{BASE_URL}/health")
        print(f"  {health.json()}\n")

        print("Analyzing transcript...")
        response = await client.post(
            f"{BASE_URL}/analyze",
            json={
                "transcript": SAMPLE_TRANSCRIPT,
                "title": "Discovery Call — Early Stage SaaS Founder",
            },
        )

        if response.status_code != 200:
            print(f"ERROR {response.status_code}: {response.text}")
            return

        result = response.json()

        print("=" * 60)
        print("SIGNALS")
        print("=" * 60)
        print(json.dumps(result["signals"], indent=2))

        print("\n" + "=" * 60)
        print("INSIGHTS")
        print("=" * 60)
        print(json.dumps(result["insights"], indent=2))

        print("\n" + "=" * 60)
        print("LINKEDIN DRAFT")
        print("=" * 60)
        print(result["content"]["linkedin_draft"]["full_post"])

        print("\n" + "=" * 60)
        print("KEY PHRASES FOR COPY")
        print("=" * 60)
        for phrase in result["content"]["key_phrases_for_copy"]:
            print(f'  • "{phrase}"')

        print(f"\nProcessing time: {result['processing_time_ms']}ms")


if __name__ == "__main__":
    asyncio.run(run())
