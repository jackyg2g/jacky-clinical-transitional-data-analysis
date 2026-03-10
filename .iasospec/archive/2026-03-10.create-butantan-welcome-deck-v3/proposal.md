# Proposal: Butantan Institute Welcome Deck V3 — Full Presentation with Welcome Speech & Small Talk

## Requirement Summary

Generate a 5-6 slide HTML presentation deck welcoming Butantan Institute (Brazil) representatives visiting IASO Bio, including a CEO welcome speech and culturally appropriate small talk topics, using the frontend-slides skill with the established Electric Studio Light visual style.

## Background and Motivation

Representatives from IASO Bio's partner, **Butantan Institute** (Instituto Butantan, Brazil), are visiting the company tomorrow (March 11, 2026). Butantan is one of the world's leading biomedical research institutions, focused on vaccines, antivenoms, and biopharmaceuticals — making them a natural partner for IASO Bio's cell therapy expertise.

A previous deck (V1) was generated at `output/butantan-welcome-deck.html` using an Electric Studio Light theme (white background, bold blue #4361ee accent, Manrope 800 font, split hero layout) confirmed by user preference via screenshot. A V2 proposal also exists but was not finalized into a generated file.

This V3 change consolidates all learnings and reference materials into a definitive, polished deck with three components:
1. A 5-6 page brief company introduction
2. A welcome speech (embedded as speaker notes on the title slide)
3. Small talk topics (embedded as a supplementary slide or speaker notes)

## Goals and Success Criteria

- Deliver a visually polished, 5-6 slide HTML presentation suitable for a first partner meeting
- Include relevant IASO images/graphics on every content slide (from website and deck assets)
- Provide a 1-2 minute CEO welcome speech as speaker notes
- Provide 4-6 culturally appropriate small talk topics for Butantan delegates
- Output as a **new file** (`output/butantan-welcome-deck-v3.html`) — NOT replacing existing files
- Use the `frontend-slides` skill for generation

**Success Criteria**:
- Deck opens in browser as a self-contained HTML file with keyboard navigation
- All 5-6 slides fit within 100vh (no scrolling)
- Images load from IASO website CDN or are embedded
- Speaker notes contain the welcome speech and small talk topics
- Visual style matches the approved Electric Studio Light theme from V1

## Scope and Boundaries

### In Scope

- Extract and synthesize key content from all 3 reference files (NDR PDF, IASO intro PPTX, website info MD)
- Generate 5-6 slide HTML presentation with the frontend-slides skill
- Embed CEO welcome speech as speaker notes on slide 1
- Include small talk topics as speaker notes on the final slide
- Use IASO website images for visual richness on every slide

### Out of Scope

- Modifying existing `output/butantan-welcome-deck.html` — must remain untouched
- Print materials, leave-behind documents, or separate speech documents
- Backend or API work
- Video or multimedia embedding beyond static images
- Detailed clinical data slides (this is a brief intro, not a full NDR)

## User/System Scenarios

### Scenario 1: CEO Presents to Butantan Delegation

- **Who**: IASO Bio CEO / senior executive
- **When/Condition**: Tomorrow (March 11, 2026), Butantan Institute representatives visiting IASO Bio offices
- **What**: Opens `output/butantan-welcome-deck-v3.html` in browser, presents 5-6 slides via keyboard navigation, references speaker notes for welcome speech and small talk
- **Result**: Butantan delegation receives a concise, visually impressive overview of IASO Bio — company profile, core product, pipeline, global reach, and partnership alignment — setting the stage for deeper collaboration discussions

## Constraints and Assumptions

### Constraints

- Must use the `frontend-slides` skill (`.claude/skills/frontend-slides/`)
- Must match Electric Studio Light visual theme (white bg, #4361ee blue, Manrope font)
- Every slide must fit 100vh — no scrolling (viewport fitting rules)
- Single self-contained HTML file with inline CSS/JS, zero dependencies
- All content in English

### Assumptions

- Butantan Institute is already a known partner/collaborator (per NDR deck page 13: "Bridging and multi-center studies: Japan and Brazil")
- The visit is a courtesy/relationship-building meeting, not a formal deal negotiation
- The CEO will present in person and may use speaker notes for the welcome speech
- Images from `en.iasobio.com` will be accessible at presentation time (or can be base64-encoded)

## Terms and Terminology

| Term/Abbreviation | Meaning | Notes |
|----------|------|------|
| Eque-cel | Equecabtagene Autoleucel | IASO's core BCMA CAR-T product, branded Fucaso |
| Fucaso | Brand name for eque-cel | Approved in China, HK, Macau for r/r MM |
| ATMP | Advanced Therapy Medicinal Product | Cell/gene therapies — IASO's sector |
| Butantan | Instituto Butantan | Brazilian biomedical research institute, potential partner |
| r/r MM | Relapsed/Refractory Multiple Myeloma | Primary approved indication |
| NDR | Non-Deal Roadshow | Type of investor presentation (source deck) |
| CAR-T | Chimeric Antigen Receptor T-cell | Core therapy modality |

## References and Links

- `reference/[ad hoc] Butantan-visit-deck/Cure_NDR_Deck_EN_vS4.pdf` — 62-page NDR deck (Jan 2026), source for company stats, pipeline, global strategy, milestones, manufacturing
- `reference/[ad hoc] Butantan-visit-deck/IASO introduction for J.pptx` — 11-slide intro deck (Feb 2026), source for concise company overview, patient story, global footprint
- `reference/[ad hoc] Butantan-visit-deck/website info.md` — Comprehensive website content extracted from iasobio.com
- `reference/[ad hoc] Butantan-visit-deck/ScreenShot_2026-03-10_012744_562.png` — Approved V1 visual style screenshot
- `output/butantan-welcome-deck.html` — Existing V1 deck (do not overwrite)
- `.claude/skills/frontend-slides/` — Skill to be used for HTML generation
