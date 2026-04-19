# Demo Builder (`_build/`)

Toolchain that generates the 4 anonymized demo project pages + PDFs from real
pipeline results. Introduced in Cowork S114 / Claude Code session April 2026.

GitHub Pages (Jekyll default) auto-excludes this folder because the name starts
with `_`. Nothing in here is served to the public — it's a build tool, checked
into the repo for reproducibility.

## Layout

| File | Role |
|------|------|
| `build_demo.py` | Orchestrator. Loads 4 `results.json` → filters → anonymizes → writes HTMLs + PDFs. |
| `anonymization_rules.py` | Per-project scrub patterns, sheet normalization, firm-name heuristics, leak scanner. |
| `gc_filter.py` | NE Construction dispositions applied to Eastside Lofts only (drops ~74 FPs/disputes, flags NE-validated TPs). |
| `page_template.py` | HTML template for per-project pages, filled by `build_demo.py`. |
| `cloudflare_worker.js` | Worker script that proxies `flikt.ai/demo/*` → GitHub Pages. Deploy via Cloudflare dashboard. |

## Running the builder

```bash
cd ~/FLIKT/Plan\ Sets\ Copy/demo-portal
source ~/flikt-env/bin/activate   # need reportlab + fitz from the pipeline env
python3 _build/build_demo.py
```

The builder is idempotent: running it twice produces the same outputs.

Outputs (all written to the parent `demo-portal/` directory):
- `eastside-lofts.html`, `metro-salon.html`, `the-atrium.html`, `meridian-residence.html`
- `FliktAI_Eastside_Lofts_Report.pdf`, `FliktAI_Metro_Salon_Studios_Report.pdf`, `FliktAI_The_Atrium_Report.pdf`, `FliktAI_Meridian_Residence_Report.pdf`
- `index.html` (landing page with 4 cards)

## Sources

Canonical mappings (see handoff `~/FLIKT/Session Handoffs/FliktAI_Demo_Refresh_Handoff_Cowork_S114.pdf`):

| Anonymized identity | Source `results.json` |
|---|---|
| Eastside Lofts (San Antonio, TX) | `Pipeline Results/Parkway_Lofts_Demo_S110_20260415_1849/` |
| Metro Salon Studios (Maitland, FL) | `Pipeline Results/400N_Salon_Lofts/` |
| The Atrium (Miami Beach, FL) | `Pipeline Results/La_Hermitage_Lobby_5Run/` |
| Meridian Residence (Surfside, FL) | `Pipeline Results/9272_Abbott_Ave_Construction_Documents/` |

## GC filter (Eastside only)

Drives off `~/FLIKT/Analysis/NE_Feedback_Analysis_S112.pdf`. Drops:
- ~22 civil/arch index-conflation FPs (NE confirmed sheets ARE listed in arch index)
- 10+ phantom/hallucinated sheets (A813, P1, L9, F-8, FB-7, RC-1, etc.)
- ~5 spec-referenced conflicts with no actual spec-section citation
- A-001 / A-002 "index missing from index" logical-inversion bug
- 8 substantive disputes (CV508, N467, N471, GEO525, GEO527, N457, N463, N465, T460)
- 2 amendment-citation corrections (C376/C377 → text patched, not dropped)
- 6 NE-confirmed TPs promoted with `ne_validated: true` flag (renders a "✓ NE-VALIDATED" badge)

Expected result: 509 raw → ~435 kept.

## Leak detection

Every build runs a regex pass over the final anonymized JSON. If any
project-specific identifier survives (e.g. "Parkway", "Hermitage", "Abbott"),
the build exits non-zero with the offending conflicts listed. Do not ship a
build that fails this check.

## Deploying the Cloudflare Worker

Copy `cloudflare_worker.js` into the Cloudflare dashboard:
1. **Workers & Pages** → **Create Worker** → paste script → **Deploy**.
2. **Worker** → **Triggers** → **Add route**: `flikt.ai/demo*` → select this Worker.
3. No DNS changes, no SSL changes — `flikt.ai` already proxies through Cloudflare
   and the wildcard cert covers the bare domain.

The Worker proxies `flikt.ai/demo/*` to `gebaumann-art.github.io/flikt-demo/*`.
WordPress at `flikt.ai/` is untouched.

## Re-running after a pipeline results update

When a new `results.json` lands for any of the 4 source projects, simply re-run
`build_demo.py`. The anonymization rules and GC filter are data-independent —
they apply whatever patterns match the new content. The `ne_validated` flag
only promotes IDs that still exist after filtering; if NE's validated IDs
aren't in the new run, the badge disappears cleanly.

If NE reviews a different project, extend `NE_VALIDATED_IDS` and the various
drop-lists in `gc_filter.py` and gate them on `source_key` the same way the
current filters gate on Eastside only.
