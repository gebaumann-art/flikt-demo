# Flikt.AI — Session Handoff Summary

**Date:** March 4, 2026
**Project:** Flikt.AI — AI-Powered Construction Plan Conflict Detection
**Contact:** info@flikt.ai | www.flikt.ai
**GitHub:** gebaumann-art
**GitHub Pages Demo:** https://gebaumann-art.github.io/flikt-demo/

---

## Project Location

All files are at: `C:\Users\GregBaumann\Desktop\FLIKTAI CLAUDE\Plan Sets Copy`

Key subfolders:
- `flikt-processor/` — Backend Python pipeline + web server
- `demo-portal/` — GitHub Pages static demo site
- `session-export/` — Fresh copies of all files updated in the last session

---

## Architecture Overview

Flikt.AI is a local web app that accepts construction plan PDFs, classifies them by discipline (Architectural, Structural, Electrical, Mechanical, Plumbing, Civil, Landscape), renders pages to images, sends them to Claude Vision API for cross-discipline conflict detection, scores conflicts on a 50-point severity model, and generates PDF reports.

**Stack:** Python 3 + FastAPI + Uvicorn (backend), embedded HTML/CSS/JS (frontend), Claude Vision API (Anthropic) for AI analysis, ReportLab for PDF generation, pdf2image/Pillow for rendering.

**To run locally:** `python server.py --port 9000` (default port is 8000 in code, but user runs on 9000)

---

## Files Updated This Session (in session-export/)

### 1. `process_plans.py` — Main Processing Pipeline
**What changed:**
- Added `_compress_image()` function — resizes images to max 1600px wide, converts to JPEG quality 75
- Rewrote `_run_simplified_detection()` with:
  - Dynamic per-discipline image limits (2 pages for 5+ disciplines, 3 otherwise)
  - Automatic batch splitting if payload exceeds 15MB (`MAX_BATCH_SIZE = 15_000_000`)
  - Each batch sent as separate Claude API call, conflicts merged
  - Debug logs per batch: `last_ai_response_batch{N}.txt`
- **Why:** Fixed 413 request_too_large error on Harbor Islands project (12 base64 images exceeded Claude API limit)

### 2. `server.py` — Web Server + Embedded UI
**What changed:**
- Added light/dark theme toggle with CSS custom properties
- Dark theme is default; light theme uses `[data-theme="light"]` selector
- Toggle button in header with sun/moon icon
- Theme preference persisted via localStorage (`flikt-theme` key)
- All UI elements updated to use CSS variables (cards, inputs, dropzone, progress bar, conflict cards, score chips, etc.)
- **Default port:** 8000 (`parser.add_argument("--port", type=int, default=8000)`)
- **User runs on port 9000** via `python server.py --port 9000`

### 3. `FliktAI_Roadmap.md` — Product Roadmap
**What changed:**
- Added "Blind Test Results — 980 Harbor Islands" section at top
- 6 critical improvement items identified from blind test gap analysis:
  1. OCR pre-processing for text-heavy sheets
  2. Material specification cross-referencing
  3. Quantity/SF comparison logic
  4. Scope completeness checks
  5. Targeted Civil ↔ Structural prompting
  6. Higher resolution for text-heavy sheets

### 4. `FliktAI_Blind_Test_980_Harbor_Islands.pdf` — Accuracy Comparison Report
- 5-page professional PDF comparing Flikt.AI results vs GC review comments
- Cover page with navy header band, summary stats
- GC Comments table (6 rows), Flikt.AI Findings table (5 rows)
- Gap analysis and improvement roadmap
- **Key finding:** 0/6 direct matches. GC found text-level material/scope mismatches; Flikt.AI found spatial/coordination conflicts. Both sets are valid but different.

### 5. Demo Portal HTML Files (for GitHub Pages)
**These need to replace the contents of the `demo-portal/` folder and be pushed to GitHub.**

- **`demo-index.html`** → should be saved as `index.html` in demo-portal/
  - Landing page with two project cards linking to individual demos
  - Light/dark toggle, Flikt.AI branding (navy/amber)

- **`oceanview.html`** — Genericized version of 9516 Bay Dr project
  - "Oceanview Residence — New Construction"
  - Address: "123 Oceanview Drive, Surfside, FL 33154"
  - 9 conflicts embedded (1 Critical, 6 Major, 2 Minor)
  - Full dashboard → progress animation → results view

- **`harbor-club.html`** — Genericized version of 980 Harbor Islands project
  - "Harbor Club — Community Renovation"
  - Address: "100 Harbor Club Blvd, Miami Beach, FL 33139"
  - 5 conflicts embedded (0 Critical, 4 Major, 1 Minor)
  - Full dashboard → progress animation → results view

---

## Blind Test Results Summary (980 Harbor Islands)

**GC's 6 Comments (text-level reading):**
1. Civil vs Structural material mismatches (asphalt vs concrete, pavers, sand)
2. SF discrepancies (9,044 vs 5,923)
3. Volleyball court scope missing from civil plans
4. Fencing scope unclear between disciplines
5. Additional material specification conflicts
6. Coordination gaps in scope documentation

**Flikt.AI's 5 Findings (visual/spatial detection):**
1. Site demolition conflicts with utility relocations (D-1 ↔ C-1) — Major
2. Electrical conduit conflicts with tree planting areas (E-1 ↔ L-2) — Major
3. Structural calculations missing for electrical equipment (S-2 ↔ E-1) — Major
4. Landscape irrigation conflicts with electrical underground (L-1 ↔ E-1) — Major
5. Wind load calculations missing for new site lighting (S-1 ↔ E-2) — Minor

**Gap:** Flikt.AI detects spatial/coordination conflicts well but misses text-level material specs and quantity mismatches. OCR + material cross-referencing needed.

---

## Scoring Model

50-point severity scale across 5 dimensions (10 points each):
- Constructability Impact
- Cost Impact
- Safety Risk
- Schedule Impact
- Downstream Risk

Severity thresholds: Critical (40-50), Major (25-39), Minor (10-24), Info (0-9)

---

## Pending Tasks for Next Session

1. **Push demo portal to GitHub Pages** — The 3 HTML files (demo-index.html → index.html, oceanview.html, harbor-club.html) need to be placed in the demo-portal/ folder and pushed via git to the `gebaumann-art/flikt-demo` repo
2. **Verify live site** at https://gebaumann-art.github.io/flikt-demo/
3. **Production improvements from blind test** (tracked in roadmap):
   - OCR pre-processing
   - Material specification cross-referencing
   - Quantity/SF comparison
   - Scope completeness checks
4. **Old files to clean up in demo-portal/**: `9516_Bay_Dr_Conflict_Report.pdf`, `demo_data.json`, `landing.html` (duplicate of index.html) can be removed

---

## User Preferences

- Ask questions first before starting work
- Shorter but detailed outputs preferred
- File formats: PDF or Excel-based reports
- Ensure margins are respected in tables/pages
- Always double-check work
