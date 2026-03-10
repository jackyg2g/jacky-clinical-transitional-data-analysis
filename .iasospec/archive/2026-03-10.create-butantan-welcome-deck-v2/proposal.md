# Butantan Institute Welcome Deck V2 — Enhanced Presentation with Welcome Speech & Small Talk

## Background

Representatives from IASO Bio's partner, **Butantan Institute (Brazil)**, are visiting the company tomorrow. The CEO needs an AI-generated presentation deck consisting of:

1. **5-6 page brief company introduction** — concise, visually polished, suitable for a first partner meeting
2. **A welcome speech** — embedded as speaker notes or a dedicated opening slide
3. **Small talk topics** — culturally appropriate conversation starters for the visit

## Source Materials

This V2 deck draws from **new and updated reference materials**, distinct from the V1 deck:

- `reference/[ad hoc] Butantan-visit-deck/Cure_NDR_Deck_EN_vS4.pdf` — NDR (Non-Deal Roadshow) English deck, likely contains updated company positioning, financials, and narrative
- `reference/[ad hoc] Butantan-visit-deck/IASO introduction for J.pptx` — IASO introduction PowerPoint, likely a shorter company intro tailored for a specific audience
- `reference/[ad hoc] Butantan-visit-deck/website info.md` — Comprehensive English website content (previously used in V1)

## Key Requirements

1. **New output file** — must NOT overwrite the existing `output/butantan-welcome-deck.html`. Use a new filename (e.g., `output/butantan-welcome-deck-v2.html`).
2. **Use frontend-slides skill** — `.claude/skills/frontend-slides` for the HTML presentation generation.
3. **Match the approved visual style** — Electric Studio Light theme (white background, bold blue #4361ee accent strip, Manrope 800 font, split hero layout) as established in the V1 deck and confirmed by user preference via `ScreenShot_2026-03-10_012744_562.png`.
4. **All content in English** — any Chinese source material must be translated.
5. **Images on every slide** — reference suitable images from IASO's English website and local deck assets.
6. **Welcome speech** — a prepared opening speech (1-2 minutes) for the CEO.
7. **Small talk topics** — 4-6 culturally relevant conversation starters for engaging Butantan representatives.

## Scope

- Extract and synthesize content from the 3 reference files
- Generate a 5-6 slide HTML presentation + welcome speech + small talk section
- Output as a single self-contained HTML file at a new path

## Out of Scope

- Modifying the existing `output/butantan-welcome-deck.html`
- Print materials or leave-behind documents
- Backend or API work
