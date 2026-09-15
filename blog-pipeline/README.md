# blog-pipeline — long-form SEO/GEO content engine

A **Claude Code multi-agent system** that turns prospect-call insights + live
SERP data into technical, citation-backed blog posts optimized for both classic
search (SEO) and AI-answer engines (GEO — Generative Engine Optimization).

This is the long-form counterpart to [`../call-pipeline`](../call-pipeline)
(short-form LinkedIn content from calls). Both are how I run content for my
startup Paygent — one repo, two pipelines.

## How it's different from call-pipeline

`call-pipeline` is a **runtime service** — Python/FastAPI code that executes.
This pipeline is a **set of Claude Code subagents** (Markdown role definitions in
`.claude/agents/`) orchestrated by `CLAUDE.md`. It runs *inside* Claude Code, not
as a server. That's a deliberate choice: for long-form research-and-writing work
with human checkpoints, an agent system is the right tool; for a deterministic
request/response transform, a service is.

## The 13 agents

| Agent | Role |
|-------|------|
| `transcript-analyst` | Extracts pain points, quotes, and content angles from call transcripts |
| `pattern-synthesizer` | Finds cross-call patterns and themes |
| `seo-geo-researcher` | Pulls live SERP + keyword data (SEO) and AI-answer-engine gaps (GEO) |
| `competitive-researcher` | Maps how competitors rank and position |
| `content-brief-generator` | Turns research into tight, pickable briefs |
| `citation-researcher` | Finds authoritative sources before any writing |
| `citation-validator` | Verifies every citation actually supports the claim |
| `blog-writer` | Drafts the post from brief + citations |
| `blog-auditor` | Reviews drafts against the brief and quality bar |
| `blog-rewriter` | Applies audit feedback |
| `geo-auditor` | Checks the post is structured to be quoted by AI answer engines |
| `content-orchestrator` | Runs the pipeline, tracks state |
| `blog-improvement-orchestrator` | Coordinates the audit → rewrite loop |

## Pipeline order (enforced, no skipping)

```
transcript-analyst → pattern-synthesizer → seo-geo-researcher
  → content-brief-generator → [human picks one brief]
  → citation-researcher → citation-validator → blog-writer
  → blog-auditor → blog-rewriter → geo-auditor
```

The **human checkpoint** (picking which brief to write) and the **separate
citation-validation and GEO-audit passes** are the point: the system uses AI for
research, synthesis, and drafting, but never lets it publish an unverified claim
or an un-audited draft. That's the same principle as call-pipeline — AI for
judgment, guardrails where it can be confidently wrong.

## Running it

Open this folder in Claude Code and ask the `content-orchestrator` for a status
update, or start the pipeline on `data/transcripts/sample-transcript.md`. Live
SERP/GEO research uses DataForSEO and SerpAPI (keys are supplied locally and are
**not** included here).

> **Note on data:** the real prospect transcripts, drafts, competitive analysis,
> and pipeline state used to build Paygent's actual content are confidential and
> are **not** in this repo. Only the reusable agent system and one synthetic
> sample transcript are published.
