# Content Engine

The content system I built to run marketing for my startup (Paygent). Two
pipelines, one idea: turn real conversations into content, and be deliberate
about where AI helps versus where it can quietly go wrong.

| Pipeline | Input → Output | What it is |
|----------|----------------|------------|
| [**call-pipeline**](./call-pipeline) | Call transcript → founder-voiced **LinkedIn post** | A runnable **Python/FastAPI** service |
| [**blog-pipeline**](./blog-pipeline) | Transcript + live SERP data → citation-backed **SEO/GEO blog** | A **Claude Code multi-agent** system (13 agents) |

## Why two different shapes

They solve different problems, so they're built differently — on purpose:

- **call-pipeline** is a deterministic request→response transform, so it's a
  service: you POST a transcript, it returns a draft. It runs the moment you
  clone it. See its [README](./call-pipeline/README.md) for the 7-stage pipeline
  and stack.
- **blog-pipeline** is long-form research-and-writing with human checkpoints, so
  it's an orchestrated set of Claude Code subagents (research → brief → cited
  draft → audit → GEO-audit). See its [README](./blog-pipeline/README.md).

## The shared principle

Both pipelines split the same way: **use the LLM for judgment** (who's the
customer, what matters, how they talk, is this claim well-sourced) and **use
plain code or hard guardrails for anything that can be confidently wrong**
(parsing formats, chunking, validating citations, a human picking the brief). AI
where it's genuinely better; guardrails where it isn't.

## Note on data

The real prospect transcripts and the content produced from them are
confidential and are **not** in this repo. call-pipeline ships a synthetic
sample; blog-pipeline ships one synthetic transcript and the reusable agent
system only.

## Built with

Claude as a coding/authoring tool throughout. The architecture decisions — which
stages are AI, where the guardrails go, how each pipeline is shaped — are the
part a model won't make for you.
