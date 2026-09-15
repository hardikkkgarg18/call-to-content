# Paygent Content OS

**What:** Turns prospect conversations + real SEO data into content that generates inbound leads.
**Paygent:** Billing infrastructure for AI agent companies — "Stripe for AI agents."
**Audience:** Founders + CTOs of 5-30 person AI agent companies managing billing manually.

## Always Start Here
Read `content/pipeline-state.md` before doing anything — it has current state, blockers, and next actions.

## File Map
| Folder | Purpose |
|--------|---------|
| `content/pipeline-state.md` | Single source of truth — read every session |
| `data/transcripts/` | Prospect conversation insights (one file per company) |
| `analysis/` | Messaging map, prospect language, SEO research |
| `content/briefs/INDEX.md` | Lightweight content briefs (topic + 5 key points only) |
| `content/citations/` | Citation research — required before any writing |
| `content/drafts/` | Final output: blog + LinkedIn per piece |
| `.claude/agents/` | 12 subagents — see individual files for roles |

## Pipeline (strict order, no skipping)
`transcript-analyst` → `pattern-synthesizer` → `seo-geo-researcher` → `content-brief-generator` → **USER PICKS ONE** → `citation-researcher` → `blog-writer`

For detailed rules, see the CLAUDE.md in each sub-folder.
