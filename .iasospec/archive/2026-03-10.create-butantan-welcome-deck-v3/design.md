## Context

IASO Bio needs a concise, visually polished welcome presentation for Butantan Institute (Brazil) representatives visiting tomorrow. This is the third iteration — V1 was generated and approved stylistically (Electric Studio Light theme), V2 was proposed but not finalized. V3 consolidates all learnings with updated reference materials (NDR deck, IASO intro PPTX, website info).

## Goals / Non-Goals

### Goals

- Create a 5-6 slide deck that tells a compelling, brief story of IASO Bio
- Include relevant images on every slide from IASO's web assets
- Embed a CEO welcome speech and small talk topics as speaker notes
- Match the approved Electric Studio Light visual style
- Output to a new file path without disturbing existing outputs

### Non-Goals

- Full investor-grade presentation (this is a brief welcome, not an NDR)
- Detailed clinical data tables or financial information
- Interactive data visualizations or charts
- Multi-language support

## Decisions

### 1. Slide Structure and Narrative Arc

**Decision**: 6 slides with the following structure:

| # | Slide | Key Content | Image Source |
|---|-------|-------------|--------------|
| 1 | **Welcome & Title** | "Welcome to IASO Biotherapeutics" + Butantan mention. Speaker notes: full welcome speech | Hero image from IASO website (laboratory/science aesthetic) |
| 2 | **Company Snapshot** | Founded 2017, Nanjing. Commercial-stage ATMP company. Key stats: 600+ patients, 10 pipeline candidates, 5 platforms, 480+ employees, 4 global sites | IASO overview graphic or facility photo |
| 3 | **Our Core Product: Fucaso** | Eque-cel (BCMA CAR-T), first fully human CAR-T approved in China. World's first BCMA-targeted CAR-T. 7-year cancer-free patient story. Single dose for potential cure | CAR-T cell mechanism illustration or patient story imagery |
| 4 | **Pipeline & Platforms** | 10 clinical candidates across hematologic malignancies and autoimmune diseases. 5 technology platforms. Expanding from oncology to autoimmune (MG, MS, SLE) | Pipeline overview image from website |
| 5 | **Global Reach & Partnerships** | Global registration strategy (China, HK, Macau, Singapore, Japan, Korea, Saudi Arabia, UAE, Brazil). Key partners: Innovent, Sana, Cabaletta, Umoja, GC Cell. Highlight Brazil as bridging study market | World map / global footprint from NDR deck |
| 6 | **Looking Forward Together** | Partnership vision with Butantan. "Products out, Patients in" global strategy. Bringing curative cell therapies to Latin America. Speaker notes: small talk topics | IASO facility or collaborative imagery |

**Rationale**: This arc moves from warm welcome → who we are → what we've achieved → where we're going → why we're excited about Butantan. It mirrors the IASO intro PPTX structure but is condensed and personalized for the visit.

**Alternatives Considered**:
- 5 slides (merging pipeline+global): Rejected because global reach deserves emphasis given Butantan is an international partner
- 7+ slides (adding clinical data): Rejected — this is a welcome, not a deep dive

### 2. Visual Style: Electric Studio Light (Reuse V1)

**Decision**: Reuse the exact same Electric Studio Light CSS variables and theme from `output/butantan-welcome-deck.html` — white background, #4361ee blue accent strip, Manrope 800 font, mint dot accent.

**Rationale**: User already approved this style via screenshot. Consistency with V1 if they end up using either version.

### 3. Image Strategy

**Decision**: Use IASO website CDN images (https://en.iasobio.com/uploads/...) referenced in `website info.md`, supplemented by key images from the NDR deck where the website doesn't have equivalent visuals. All images via `<img>` tags with CDN URLs (no base64 to keep file small).

**Rationale**: Website images are high quality and publicly accessible. CDN URLs keep the HTML file lightweight.

**Key images to use**:
- Slide 1: Homepage banner — `https://en.iasobio.com/uploads/2021-07/10/_1625885420_8543.jpg` (cell therapy hero image with CAR-T cell and DNA helix)
- Slide 2: Integrated capabilities background — `https://en.iasobio.com/uploads/2025-11/24/_1763951518_6300.jpg`; or facility photos: Shanghai R&D center `https://en.iasobio.com/uploads/2025-07/02/_1751387252_4567.jpg`, Nanjing GMP `https://en.iasobio.com/uploads/2026-01/09/_1767929422_5285.jpg`
- Slide 3: Antibody discovery platform photo — `https://en.iasobio.com/uploads/2025-11/26/_1764138317_1995.jpg`; or CAR-T mechanism from NDR page 19
- Slide 4: Pipeline chart — `https://en.iasobio.com/uploads/2025-12/18/_1766042039_5910.png`
- Slide 5: Global map from NDR page 16 (registration map); or use partner logos from website
- Slide 6: Shanghai or Nanjing facility exterior — `https://en.iasobio.com/uploads/2025-07/02/_1751387252_4567.jpg`

### 4. Welcome Speech Content

**Decision**: A warm, 1-2 minute speech emphasizing:
- Personal welcome to Shanghai/IASO facilities
- Acknowledgment of Butantan's 125+ year legacy in biomedical research
- Shared mission: bringing curative therapies to patients worldwide
- Excitement about potential collaboration in cell therapy for Latin America
- Brief mention of IASO's journey from 2017 startup to commercial-stage leader
- Invitation to explore partnership possibilities

### 5. Small Talk Topics

**Decision**: 6 culturally appropriate topics:
1. **Butantan's history**: Ask about their 125+ year journey, snake farm origins, COVID vaccine contributions
2. **Brazil–China biotech bridge**: Growing bilateral cooperation in health sciences
3. **São Paulo as a biotech hub**: Butantan's role in making São Paulo a center of excellence
4. **CAR-T therapy landscape in Latin America**: Emerging access and regulatory pathways
5. **Shanghai impressions**: First-time visitors — food, culture, city highlights
6. **Football (soccer)**: A universally safe and enjoyable topic with Brazilian visitors

## Risks / Trade-offs

### Risk: CDN Image Availability

**Risk**: IASO website images are loaded via CDN URLs and require internet access during presentation.

**Mitigation**:
- Test presentation before the meeting with internet access
- If offline needed, swap to base64-encoded images in a follow-up edit

### Trade-off: Brevity vs. Comprehensiveness

**Decision**: Prioritize brevity (6 slides) over comprehensiveness. This is a welcome deck, not a due diligence presentation.

**Impact**: Some details (financial data, detailed clinical results, management team bios) are intentionally omitted. These can be shared in follow-up materials.

## Open Questions

1. **Does the CEO need a printed copy of the welcome speech?**
   - Assumption: No — speaker notes in the HTML file are sufficient
   - Can be extracted if needed

2. **Will there be a Q&A session?**
   - Assumption: Informal discussion after the brief presentation
   - Small talk topics serve as conversation bridges

## References

- `reference/[ad hoc] Butantan-visit-deck/Cure_NDR_Deck_EN_vS4.pdf` — Key pages: 5-6 (overview, stats), 8 (milestones), 10 (pipeline), 13 (global strategy), 15-16 (commercialization, registration map), 19 (eque-cel mechanism), 31 (manufacturing), 36 (potential milestones)
- `reference/[ad hoc] Butantan-visit-deck/IASO introduction for J.pptx` — Key slides: 4 (IASO overview), 5 (global footprint), 6 (pipeline), 7 (patient story), 9 (global registration)
- `reference/[ad hoc] Butantan-visit-deck/website info.md` — Company overview, culture, history, technology platforms, partnerships, image URLs
- `.claude/skills/frontend-slides/SKILL.md` — Skill specification for HTML generation
