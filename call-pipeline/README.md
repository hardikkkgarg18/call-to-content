# call-pipeline

Turn a raw sales/discovery-call transcript into a ready-to-post, founder-voiced
**LinkedIn draft** — plus the structured customer intelligence behind it. The
short-form half of the [content engine](../README.md); the long-form SEO/GEO blog
half is [`../blog-pipeline`](../blog-pipeline).

Built to automate a real problem at Paygent: the founder does prospect calls all
day, and turning them into content — insights, LinkedIn posts in the founder's
voice — by hand after every call is slow, so it never happened. This does it in
one call.

## How it works

`POST /api/v1/analyze` runs a **7-stage pipeline**, each stage its own module in
`pipeline/`. The key design decision is *what's AI and what isn't*:

| Stage | Module | AI? | What it does |
|-------|--------|-----|--------------|
| 1. Normalize | `normalizer.py` | No | Cleans messy exports (Google Meet `[Name] HH:MM`, Otter, Fireflies, `Speaker:`), strips timestamps, merges fragmented caption lines. Deterministic → plain regex. |
| 2. Classify speakers | `speaker_classifier.py` | Yes | LLM labels each speaker `seller` vs `prospect`, then keeps **only the prospect's turns** — so the analysis is about what the customer said, not what was pitched. |
| 3. Chunk | `chunker.py` | No | Splits long transcripts on speaker turns with a 2-turn overlap so nothing is lost at boundaries. Deterministic → plain code. |
| 4. Extract signals | `signal_extractor.py` | Yes | Per chunk, extracts pain points (with intensity + exact quote), objections, verbatim quotes, buying signals — via structured tool-calling so output is typed, not guessed. |
| 5. Merge | `api/routes.py` | No | Recombines per-chunk signals, dedupes quotes, averages confidence. |
| 6. Aggregate | `insight_aggregator.py` | Yes | Lifts raw signals into market-level insight: dominant pain theme, objection pattern, top quotes, ICP signals, urgency. |
| 7. Generate | `content_generator.py` | Yes | Writes the LinkedIn post in the founder's voice, with an explicit style guide (short paragraphs, insight-not-pitch, banned buzzwords, use the customer's exact language). |

A second endpoint, `POST /api/v1/enrich-profile`, scrapes a founder's LinkedIn +
company site and extracts voice/tone hints that feed stage 7. (Optional — the
core `/analyze` flow doesn't need it.)

Everything flows through **Pydantic schemas** (`schemas/`) so each stage's output
is validated and typed.

## Stack

- **Python** + **FastAPI** (`main.py`, `api/routes.py`)
- **OpenAI** `gpt-4o-mini` with function/tool-calling for structured extraction
- **Pydantic v2** for typed schemas
- **httpx** + [Jina.ai reader](https://jina.ai) for website fetching; `linkedin-api` (optional) for profiles
- Single-page **HTML** frontend (`index.html`)

## Run it

Requires Python 3.10+. From this folder (`call-pipeline/`):

```bash
pip install -r requirements.txt

cp .env.example .env        # add your OpenAI key
uvicorn main:app --reload --port 8001

# In another terminal — sends a real sample transcript through /analyze:
python test_pipeline.py
```

Or open `index.html` in a browser to use the UI against the running server.
Interactive API docs: http://localhost:8001/docs
