#!/usr/bin/env python3
"""Flikt.AI demo page builder.

Loads the configured real results.json files -> replays current FP/severity
gates -> anonymizes -> regenerates the per-project HTML pages + landing
index.html.

Usage:
  cd ~/FLIKT/Plan\\ Sets\\ Copy/demo-portal && python3 _build/build_demo.py

Prerequisites:
  - FLIKT pipeline at ~/FLIKT/Coding/pipeline/ (for report_generator.py)
  - reportlab installed in the active Python environment

Output goes into the parent demo-portal/ directory.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# --- Path wiring -------------------------------------------------------------

BUILD_DIR = Path(__file__).parent.resolve()
DEMO_PORTAL = BUILD_DIR.parent
FLIKT_ROOT = DEMO_PORTAL.parent.parent  # ~/FLIKT/
PIPELINE_RESULTS = FLIKT_ROOT / "Pipeline Results"
PIPELINE_CODE = FLIKT_ROOT / "Coding" / "pipeline"

# Make pipeline modules importable
sys.path.insert(0, str(PIPELINE_CODE))
sys.path.insert(0, str(BUILD_DIR))

from anonymization_rules import (  # noqa: E402
    PROJECT_RULES,
    anonymize_conflict,
    anonymize_sheet_list,
    anonymize_text,
    get_project_metadata,
    leak_scan,
)
from gc_filter import filter_and_annotate  # noqa: E402
from page_template import PAGE_TEMPLATE  # noqa: E402
from current_gates import apply_current_gates, print_report  # noqa: E402
from vocab_gate import (  # noqa: E402
    INTERNAL_CONFLICT_FIELDS,
    selftest,
    vocab_scan,
)

# --- Source configuration ----------------------------------------------------

PROJECTS = [
    {
        # S347 (2026-08-12): NEW featured project. Source is Sunny Cove
        # (smoke_test_sunny_cove, run 2026-06-21) — a current-era pipeline run,
        # cleared for public use by Greg 2026-08-04 during sample-report
        # selection. 329 sheets / 10 disciplines / 45 conflicts. Replaces
        # Eastside Lofts as the featured card (see retirement block below).
        "source_key": "cypress_bend",
        "source_dir": "smoke_test_sunny_cove",
        "slug": "cypress-bend",
        "pdf_name": "FliktAI_Cypress_Bend_Report.pdf",
        "apply_gc_filter": False,
        "render_cap": 9999,
        # S347c: Sunny Cove is cleared for public use (Greg 2026-08-04), so the
        # viewer shows REAL page renders from the cached run — landscape
        # drawing sheets only, title-block strip redacted, DEMO-watermarked.
        # Greg-approved 2026-08-12 (portal-clone + redacted real sheets).
        "real_sheets": True,
    },
    # ------------------------------------------------------------------
    # Eastside Lofts (source: Millenium Apartments S180) was RETIRED
    # 2026-08-12 (S347, Greg's call).
    #
    # The source was frozen 2026-05-15 and no post-S180 cached run exists;
    # even after current_gates cleanup it advertised ~2x the volume the
    # current pipeline emits, and refreshing the 703-sheet fixture is the
    # one path that costs API money. Rather than pay to refresh a demo
    # fixture, the featured slot moved to Sunny Cove (above), which has a
    # genuine current-era cached run.
    #
    # Its anonymization rules are RETAINED in anonymization_rules.py under
    # "eastside_lofts" so it can be restored — after a paid re-run — by
    # re-adding this block:
    #
    #   {"source_key": "eastside_lofts",
    #    "source_dir": "Millenium_Apartments_S180_run1",  # <- replace with fresh run
    #    "slug": "eastside-lofts",
    #    "pdf_name": "FliktAI_Eastside_Lofts_Report.pdf",
    #    "apply_gc_filter": False, "render_cap": 100},
    #
    # eastside-lofts.html on the live site is now a redirect stub to
    # index.html (old shared links must not 404); the retired page itself
    # is archived in ~/FLIKT/Deprecated/.
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Metro Salon Studios (source: Salon Lofts) was RETIRED 2026-07-31.
    #
    # It was repointed to the 2026-07-14 cached run, which is correct,
    # current-pipeline output — but at that precision the project yields only
    # 17 conflicts / 1 Critical. That is honest and it is not a data problem;
    # it simply no longer carries enough volume to work as a demo. Greg's call.
    #
    # Its anonymization rules are deliberately RETAINED in
    # anonymization_rules.py under "metro_salon_studios" so the project can be
    # restored by re-adding the config block below. Nothing else references it.
    #
    #   {"source_key": "metro_salon_studios",
    #    "source_dir": "smoke_test_salon_lofts",
    #    "slug": "metro-salon",
    #    "pdf_name": "FliktAI_Metro_Salon_Studios_Report.pdf",
    #    "apply_gc_filter": False, "render_cap": 9999},
    # ------------------------------------------------------------------
    {
        # S336 refresh (2026-07-31): repointed from LHermitage_S173_phase1 to
        # the 2026-06-20 cached run (73 vs 76 sheets, 29 -> 22 conflicts).
        "source_key": "the_atrium",
        "source_dir": "smoke_test_lhermitage",
        "slug": "the-atrium",
        "pdf_name": "FliktAI_The_Atrium_Report.pdf",
        "apply_gc_filter": False,
        "render_cap": 9999,
    },
    {
        # 9332 Carlyle (luxury single-family renovation & addition), 7 disciplines.
        # S336: smoke_test_carlyle predates this run (2026-05-11 vs 05-15), so the
        # S180 source is retained and cleaned by current_gates.
        "source_key": "meridian_residence",
        "source_dir": "Carlyle_S180_run1",
        "slug": "meridian-residence",
        "pdf_name": "FliktAI_Meridian_Residence_Report.pdf",
        "apply_gc_filter": False,
        "render_cap": 9999,
    },
]

REPORT_DATE = "August 12, 2026"

# --- Real sheet renders (S347c) ----------------------------------------------
#
# For sources flagged real_sheets, cited sheet refs are matched to the run's
# page_images/ renders. Only LANDSCAPE pages qualify (portrait pages in these
# sets are document/binder pages, not drawings). Each used render gets the
# title-block strip painted over (right edge carries project name, firm,
# address), a diagonal DEMO watermark, and a downscale before being copied
# into the published site. Output filenames derive from the ANONYMIZED sheet
# label, never the source filename.

REDACT_RIGHT_FRAC = 0.115   # title block strip width (fraction of page width)
REDACT_LEFT_FRAC = 0.028    # left-margin rotated fine print carries the firm name
SHEET_MAX_W = 1800
SHEET_JPEG_Q = 72

_CODE_RE = re.compile(r"^([A-Za-z]{1,3})[-_ ]?(\d[\d.]*)([A-Za-z]?)")


def _sheet_code(s: str):
    m = _CODE_RE.match(s.strip())
    if not m:
        return None
    return (m.group(1).upper(), re.sub(r"\D", "", m.group(2)), m.group(3).upper())


def _label_slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") or "sheet"


def _process_render(src: Path, dst: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont
    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        draw = ImageDraw.Draw(im)
        # Redact title-block strip (right edge) + left-margin fine print
        # (verified S347c: the rotated copyright text names the architect and
        # stays legible after downscale).
        draw.rectangle([int(w * (1 - REDACT_RIGHT_FRAC)), 0, w, h], fill="white")
        draw.rectangle([0, 0, int(w * REDACT_LEFT_FRAC), h], fill="white")
        if w > SHEET_MAX_W:
            im = im.resize((SHEET_MAX_W, int(h * SHEET_MAX_W / w)), Image.LANCZOS)
        # Diagonal DEMO watermark.
        overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(im.width * 0.16))
        except Exception:
            font = ImageFont.load_default()
        od.text((im.width * 0.5, im.height * 0.5), "DEMO", font=font,
                fill=(15, 23, 42, 26), anchor="mm")
        overlay = overlay.rotate(30, center=(im.width * 0.5, im.height * 0.5))
        im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "JPEG", quality=SHEET_JPEG_Q, optimize=True)


def build_real_sheet_map(cfg: Dict, raw_conflicts: List[Dict]) -> Dict[str, str]:
    """Return {anonymized_sheet_label: site-relative jpg path}.

    Matching is strict on (discipline letters, digits): 'A-101' matches
    'A101_p1.jpg' or 'A101C_-_...jpg', never 'A114...'. Unmatched or
    portrait refs simply stay off the map (viewer falls back to placeholder).
    """
    from PIL import Image
    source_key = cfg["source_key"]
    img_dir = PIPELINE_RESULTS / cfg["source_dir"] / "page_images"
    if not img_dir.is_dir():
        print(f"  [real-sheets] no page_images dir for {cfg['slug']} — skipping")
        return {}

    img_by_code: Dict[tuple, str] = {}
    for f in sorted(img_dir.iterdir()):
        code = _sheet_code(f.name)
        if code and f.suffix.lower() in (".jpg", ".jpeg", ".png"):
            img_by_code.setdefault(code, f.name)

    def match(ref: str):
        code = _sheet_code(ref)
        if not code:
            return None
        if code in img_by_code:
            return img_by_code[code]
        for k, fname in img_by_code.items():
            if k[0] == code[0] and k[1] == code[1]:
                return fname
        return None

    out_dir = DEMO_PORTAL / "sheets" / cfg["slug"]
    label_map: Dict[str, str] = {}
    processed = 0
    for c in raw_conflicts:
        for ref in (c.get("sheets") or []):
            if not isinstance(ref, str):
                continue
            labels = anonymize_sheet_list([ref], source_key)
            if not labels:
                continue
            label = labels[0]
            if label in label_map:
                continue
            fname = match(ref)
            if not fname:
                continue
            src = img_dir / fname
            with Image.open(src) as im:
                if im.width <= im.height:  # portrait = document page, skip
                    continue
            dst = out_dir / f"{_label_slug(label)}.jpg"
            _process_render(src, dst)
            label_map[label] = f"sheets/{cfg['slug']}/{dst.name}"
            processed += 1
    print(f"  [real-sheets] {cfg['slug']}: {processed} renders published "
          f"(redacted right {int(REDACT_RIGHT_FRAC*100)}%, max {SHEET_MAX_W}px)")
    return label_map


# --- Summary recomputation ---------------------------------------------------
#
# NOTE (2026-08-19): the discipline-pair COUNT was removed from the summary.
# It reached two public surfaces — the analysis log and the embedded DATA JSON
# in page source — and "discipline pair(s)" is forbidden internal vocabulary
# per the customer-secrecy doctrine. Per-finding `disc_a`/`disc_b` stay: the
# real portal shows the same "A ↔ S" badge on every finding card, so which two
# trades collide is legitimately customer-facing. It is the AGGREGATE
# comparison-matrix framing that reveals how the pipeline works.

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def recompute_summary(conflicts: List[Dict]) -> Dict:
    sev_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    cost_low = 0
    cost_high = 0
    for c in conflicts:
        s = c.get("severity", "Low")
        sev_counts[s] = sev_counts.get(s, 0) + 1
        cost_low += int(c.get("cost_low", 0) or 0)
        cost_high += int(c.get("cost_high", 0) or 0)
    return {
        "total_conflicts": len(conflicts),
        "critical": sev_counts["Critical"],
        "high": sev_counts["High"],
        "medium": sev_counts["Medium"],
        "low": sev_counts["Low"],
        "cost_low": cost_low,
        "cost_high": cost_high,
    }


# --- Disciplines -------------------------------------------------------------

def anonymize_disciplines(raw: Dict[str, List[str]], source_key: str) -> Dict[str, List[str]]:
    """Anonymize each discipline's sheet list; keep discipline names as-is."""
    out = {}
    for name, sheets in raw.items():
        out[name] = anonymize_sheet_list(sheets or [], source_key)
    return out


# --- Stages generator --------------------------------------------------------

def make_stages(project_name: str, total_sheets: int, disciplines: List[str], summary: Dict) -> List[Dict]:
    """Build a realistic-looking analysis activity log for the Progress view."""
    stages: List[Dict] = []
    stages.append({"pct": 3, "text": f"Loading plan set ({total_sheets} sheets)...",
                   "log": f"Loaded {project_name} plan set \u2014 {total_sheets} construction documents"})
    stages.append({"pct": 6, "text": "Classifying sheet disciplines...",
                   "log": f"Identified {len(disciplines)} disciplines: {', '.join(disciplines)}"})
    stages.append({"pct": 12, "text": "Rendering architectural plans...",
                   "log": "Architectural: extracting floor plans, elevations, details"})
    if "Structural" in disciplines:
        stages.append({"pct": 18, "text": "Processing structural sheets...",
                       "log": "Structural: extracting framing, foundations, shear walls"})
    if any(d in disciplines for d in ("Mechanical", "Electrical", "Plumbing")):
        stages.append({"pct": 26, "text": "Extracting MEP elements...",
                       "log": "MEP: identifying equipment, panels, circuits, fixtures"})
    if "Fire Protection" in disciplines:
        stages.append({"pct": 32, "text": "Processing fire protection plans...",
                       "log": "Fire Protection: sprinkler risers, flow switches, device layout"})
    if "Civil" in disciplines or "Landscape" in disciplines:
        stages.append({"pct": 38, "text": "Extracting civil and landscape...",
                       "log": "Civil / Landscape: grading, utilities, site coordination"})
    if "Specifications" in disciplines:
        stages.append({"pct": 44, "text": "Parsing specification book...",
                       "log": "Specifications: cross-referencing CSI divisions against plans"})
    stages.append({"pct": 52, "text": "Cross-discipline coordination...",
                   "log": "Comparing elements across every trade combination in the set"})
    stages.append({"pct": 60, "text": "Checking code compliance...",
                   "log": "\u26A0 Detecting building-code + accessibility issues"})
    stages.append({"pct": 68, "text": "Detecting spatial clashes...",
                   "log": "\u26A0 Scanning for geometric conflicts between disciplines"})
    stages.append({"pct": 75, "text": "Checking MEP coordination gaps...",
                   "log": "\u26A0 Identifying missing equipment circuits, routing conflicts"})
    stages.append({"pct": 82, "text": "Prioritizing findings by severity...",
                   "log": (f"{summary['total_conflicts']} findings prioritized: "
                           f"{summary['critical']} Critical, {summary['high']} High, "
                           f"{summary['medium']} Medium, {summary['low']} Low")})
    stages.append({"pct": 92, "text": "Estimating cost and schedule impacts...",
                   "log": f"Total cost exposure: ${summary['cost_low']:,} \u2013 ${summary['cost_high']:,}"})
    stages.append({"pct": 100, "text": "Analysis complete!",
                   "log": (f"Report generated \u2014 {summary['total_conflicts']} findings "
                           f"across {len(disciplines)} disciplines")})
    return stages


# --- Per-project processing --------------------------------------------------

def process_project(cfg: Dict) -> Dict:
    """Load, filter, anonymize, and package one project's data."""
    source_key = cfg["source_key"]
    source_path = PIPELINE_RESULTS / cfg["source_dir"] / "results.json"
    with open(source_path) as f:
        raw = json.load(f)

    conflicts = raw["conflicts"]
    gc_report = None
    if cfg["apply_gc_filter"]:
        conflicts, gc_report = filter_and_annotate(conflicts)

    # S336: replay CURRENT production FP + severity gates over the cached
    # source. Two of the four sources predate ~150 sessions of precision work;
    # this keeps the public demo from advertising findings (and Critical
    # counts) the product would no longer emit. See _build/current_gates.py.
    conflicts, gate_report = apply_current_gates(conflicts, label=cfg["slug"])
    print_report(gate_report)

    # Real sheet renders (S347c): map anonymized sheet labels to published
    # redacted renders. Built from the raw (pre-gate) conflict list so the
    # map is a superset; keyed by anonymized label so filenames can't leak.
    sheet_img_map: Dict[str, str] = {}
    if cfg.get("real_sheets"):
        sheet_img_map = build_real_sheet_map(cfg, raw["conflicts"])

    # Anonymize every conflict
    anonymized = [anonymize_conflict(c, source_key) for c in conflicts]

    # Attach per-conflict sheet_images aligned with the anonymized sheets
    # list; order real-imaged sheets first so the viewer opens on a drawing.
    if sheet_img_map:
        for c in anonymized:
            labels = c.get("sheets") or []
            if not isinstance(labels, list):
                continue
            imaged = [l for l in labels if l in sheet_img_map]
            bare = [l for l in labels if l not in sheet_img_map]
            c["sheets"] = imaged + bare
            c["sheet_images"] = [sheet_img_map.get(l) for l in c["sheets"]]

    # Anonymize project metadata from source + overlay handoff-defined metadata
    source_disciplines = raw.get("project", {}).get("disciplines", {}) or {}
    anon_disciplines = anonymize_disciplines(source_disciplines, source_key)
    total_sheets = raw.get("project", {}).get("total_sheets", 0)

    # Authoritative metadata from handoff (overrides any residual source fields)
    meta = get_project_metadata(source_key)
    project = {
        **meta,
        "disciplines": anon_disciplines,
        "total_sheets": total_sheets,
    }

    summary = recompute_summary(anonymized)

    return {
        "source_key": source_key,
        "cfg": cfg,
        "project": project,
        "conflicts": anonymized,
        "summary": summary,
        "gc_report": gc_report,
        "total_sheets": total_sheets,
    }


# --- HTML generation ---------------------------------------------------------

# Conflict fields that must never reach the embedded DATA JSON. The demo page
# ships this blob verbatim in page source, so anything here is world-readable
# even when nothing renders it. Found published 2026-08-19:
#   consensus                 -> {"runs_detected": 5, "total_runs": 5, ...}
#                                reveals the multi-run voting design outright
#   scores                    -> the 5-axis severity model by name
#                                (constructability/cost/safety/schedule/downstream)
#   severity_downgrade_reason -> names internal gates ("S2 routine-coordination gate")
#   source                    -> internal module names, e.g. "spec_processor_api"
#   flags                     -> internal flag slugs, e.g. "structural_detail_missing"
# Denylist rather than allowlist deliberately: an allowlist here would silently
# drop any new field the template starts rendering. The vocab gate over the
# rendered HTML is the backstop for anything this list misses.
INTERNAL_CONFLICT_FIELDS = {
    "consensus",
    "scores",
    "severity_downgrade_reason",
    "source",
    "flags",
}


def strip_internal_fields(conflicts: List[Dict]) -> List[Dict]:
    """Drop internal-only fields before a conflict reaches a public page."""
    return [
        {k: v for k, v in c.items() if k not in INTERNAL_CONFLICT_FIELDS}
        for c in conflicts
    ]


def build_page_html(data: Dict) -> str:
    cfg = data["cfg"]
    project = data["project"]
    summary = data["summary"]
    disciplines_list = list(project["disciplines"].keys())
    stages = make_stages(project["name"], data["total_sheets"], disciplines_list, summary)

    data_json = json.dumps({
        "project": project,
        "summary": summary,
        "conflicts": strip_internal_fields(data["conflicts"]),
    }, ensure_ascii=False)
    stages_json = json.dumps(stages, ensure_ascii=False)

    return PAGE_TEMPLATE.format(
        TITLE=project["name"],
        DATA_JSON=data_json,
        STAGES_JSON=stages_json,
        RENDER_CAP=cfg["render_cap"],
        PDF_FILENAME=cfg["pdf_name"],
        REPORT_DATE=REPORT_DATE,
    )


LANDING_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flikt.AI &mdash; Plan Conflict &amp; Coordination Demo</title>
<meta name="description" content="AI-powered plan conflict detection for multifamily, commercial, and residential construction. Real coordination issues found across disciplines, anonymized for demo.">
<meta property="og:type" content="website">
<meta property="og:title" content="Flikt.AI &mdash; Plan Conflict Detection Demo">
<meta property="og:description" content="AI-powered plan conflict detection. Real coordination issues found across 10 disciplines.">
<meta property="og:url" content="https://demo.flikt.ai/">
<meta property="og:site_name" content="Flikt.AI">
<meta property="og:image" content="og_final_demo.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Flikt.AI &mdash; Plan Conflict Detection Demo">
<meta name="twitter:description" content="AI-powered plan conflict detection. Real coordination issues across disciplines.">
<meta name="twitter:image" content="og_final_demo.png">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script>
(function(){try{var s=localStorage.getItem('flikt-theme');
if(!s){s=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}
document.documentElement.setAttribute('data-theme',s)}catch(e){}})();
</script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#0a1929;--navy-dark:#141F36;--amber:#E8A020;--amber-light:#F5C96B;
--critical:#B91C1C;--high:#C2410C;--medium:#A16207;--low:#15803D;
--bg:#F5F7FA;--card:#FFFFFF;--card-hover:#F8FAFC;
--text:#0F172A;--text-muted:#64748B;--border:#E2E8F0;
--mono:'IBM Plex Mono',ui-monospace,'SF Mono',Menlo,monospace;
--chip-bg:#F1F5F9;--stat-bg:#F8FAFC}
:root[data-theme="dark"]{--bg:#0F1723;--card:#1A2540;--card-hover:#223050;
--text:#E8ECF1;--text-muted:#8896A8;--border:#2A3A55;
--chip-bg:#0a1929;--stat-bg:rgba(255,255,255,0.03)}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
background:var(--bg);color:var(--text);line-height:1.5;overflow-x:hidden}
a{color:inherit;text-decoration:none}
.header{background:var(--navy-dark);border-bottom:2px solid var(--amber);padding:12px 32px;
display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}
.logo{display:flex;align-items:center;gap:10px;font-size:22px;font-weight:700;letter-spacing:.2px;color:white;text-decoration:none}
.logo-icon{height:32px;width:32px;display:block;flex-shrink:0}
.logo-wm{color:white;white-space:nowrap}
.logo-accent{color:var(--amber)}
.header-right{display:flex;align-items:center;gap:12px}
.real-ai-badge{font-family:var(--mono);font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.6px;
color:var(--amber);background:rgba(232,160,32,0.1);border:1px solid rgba(232,160,32,0.3);
padding:5px 10px;border-radius:14px}
.theme-toggle{background:transparent;border:1px solid rgba(255,255,255,0.18);
border-radius:8px;width:34px;height:34px;display:flex;align-items:center;justify-content:center;
cursor:pointer;color:#fff;transition:background .15s ease,border-color .15s ease;padding:0}
.theme-toggle:hover{background:rgba(255,255,255,0.08);border-color:rgba(255,255,255,0.35)}
.theme-toggle svg{width:16px;height:16px;display:block}
.theme-toggle .sun{display:none}
.theme-toggle .moon{display:block}
:root[data-theme="dark"] .theme-toggle .sun{display:block}
:root[data-theme="dark"] .theme-toggle .moon{display:none}
.hero{text-align:center;margin:56px 32px 16px}
.hero h1{font-size:44px;font-weight:800;letter-spacing:-0.03em;line-height:1.1;margin-bottom:12px}
.hero p{color:var(--text-muted);font-size:16px;max-width:620px;margin:0 auto}
.projects{max-width:1200px;margin:32px auto;padding:0 32px;display:flex;flex-direction:column;gap:24px}
.projects-row{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.project-card{background:var(--card);border:1px solid var(--border);border-radius:12px;
padding:28px 28px 24px;transition:all .25s ease;cursor:pointer;position:relative;overflow:hidden;
display:flex;flex-direction:column}
.project-card:hover{border-color:var(--amber);transform:translateY(-3px);
box-shadow:0 8px 32px rgba(232,160,32,0.12)}
.project-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;
background:var(--amber);transform:scaleX(0);transition:transform .25s ease}
.project-card:hover::after{transform:scaleX(1)}
.project-card.featured{flex-direction:row;gap:36px;align-items:center;padding:32px 36px}
.featured .card-left{flex:1;min-width:0}
.featured .card-right{flex:0 0 340px;display:flex;flex-direction:column;gap:14px}
.card-header{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-start;margin-bottom:12px;gap:8px 12px}
.card-header h2{font-size:18px;font-weight:700;color:var(--amber);line-height:1.3;flex:1;min-width:0}
.featured .card-header{flex-direction:column;align-items:flex-start}
.featured .card-header h2{font-size:22px}
.card-type{font-family:var(--mono);font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.6px;
color:var(--text-muted);background:var(--chip-bg);padding:4px 10px;border-radius:4px;
white-space:normal;flex-shrink:0;max-width:100%}
.card-address{font-size:13px;color:var(--text-muted);margin-bottom:16px}
.card-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px}
.card-stat{text-align:center;padding:10px 6px;background:var(--stat-bg);border-radius:8px}
.card-stat .num{font-size:18px;font-weight:800}
.card-stat .lbl{font-family:var(--mono);font-size:9.5px;text-transform:uppercase;letter-spacing:.7px;color:var(--text-muted);margin-top:2px}
.featured .card-stat .num{font-size:24px}
.featured .card-stats{margin-bottom:0}
.disciplines-list{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:18px}
.disc-tag{background:var(--chip-bg);padding:3px 10px;border-radius:14px;font-size:11px;
border:1px solid var(--border);color:var(--text-muted)}
.card-cta{color:var(--amber);font-size:13px;font-weight:700;transition:all .25s ease;margin-top:auto}
.project-card:hover .card-cta{transform:translateX(4px)}
.featured .card-cta{font-size:14px}
.footer{text-align:center;padding:48px 32px 32px;color:var(--text-muted);font-size:12px}
@media(max-width:960px){
.projects-row{grid-template-columns:1fr 1fr}
.project-card.featured{flex-direction:column;padding:28px 28px 24px}
.featured .card-right{flex:auto}
.featured .card-header h2{font-size:20px}
}
@media(max-width:640px){
.projects-row{grid-template-columns:1fr}
}
@media(max-width:480px){
.projects{padding:0 16px}
.hero{margin:32px 16px 8px}
.hero h1{font-size:24px}
}
</style>
</head>
<body>
<div class="header">
  <a href="index.html" class="logo" aria-label="Flikt.AI home">
    <img src="flikt-icon.svg" alt="" class="logo-icon">
    <span class="logo-wm">Flikt<span class="logo-accent">.AI</span></span>
  </a>
  <div class="header-right">
    <span class="real-ai-badge">Real AI analysis</span>
    <button class="theme-toggle" type="button" aria-label="Toggle dark mode" title="Toggle dark mode" onclick="(function(){var r=document.documentElement;var n=r.getAttribute('data-theme')==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('flikt-theme',n)}catch(e){}})()">
      <svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
    </button>
  </div>
</div>

<div class="hero">
  <h1>AI-Powered Plan Coordination</h1>
  <p>Upload construction plans. Detect coordination conflicts. Save thousands in rework. Every conflict below comes from a real pipeline run &mdash; project identities anonymized.</p>
</div>

<div class="projects">

  {FEATURED_CARD}

  <div class="projects-row">
    {GRID_CARDS}
  </div>

</div>

<div class="footer">
  Flikt.AI &mdash; Automated Plan Conflict Detection for Construction
  <div style="margin-top:6px;opacity:0.75">&copy; 2026 Flikt.AI &middot; Patents Pending</div>
</div>

</body>
</html>
"""


def _abbreviate_value(value: int) -> str:
    """Format construction value for card display: 42000000 -> $42M, 3200000 -> $3.2M, 285000 -> $285K."""
    if value >= 1_000_000:
        m = value / 1_000_000
        return f"${m:.1f}M".replace(".0M", "M")  # Drop trailing .0 (e.g. $42.0M -> $42M)
    if value >= 1_000:
        return f"${value // 1_000}K"
    return f"${value}"


def build_featured_card(data: Dict) -> str:
    project = data["project"]
    summary = data["summary"]
    cfg = data["cfg"]
    disc_tags = "".join(
        f'<span class="disc-tag">{name}</span>'
        for name in project["disciplines"].keys()
    )
    value_short = _abbreviate_value(project["construction_value"])
    return f"""<a href="{cfg['slug']}.html" class="project-card featured">
    <div class="card-left">
      <div class="card-header">
        <h2>{project['name']}</h2>
        <span class="card-type">{project['type']}</span>
      </div>
      <div class="card-address">{project['address']}</div>
      <div class="disciplines-list">{disc_tags}</div>
      <div class="card-cta">Run Analysis &rarr;</div>
    </div>
    <div class="card-right">
      <div class="card-stats">
        <div class="card-stat"><div class="num">{value_short}</div><div class="lbl">Construction Value</div></div>
        <div class="card-stat"><div class="num">{data['total_sheets']}</div><div class="lbl">Total Sheets</div></div>
        <div class="card-stat"><div class="num">{len(project['disciplines'])}</div><div class="lbl">Disciplines</div></div>
      </div>
    </div>
  </a>"""


def build_grid_card(data: Dict) -> str:
    project = data["project"]
    cfg = data["cfg"]
    disc_tags = "".join(
        f'<span class="disc-tag">{name}</span>'
        for name in project["disciplines"].keys()
    )
    value_short = _abbreviate_value(project["construction_value"])
    return f"""<a href="{cfg['slug']}.html" class="project-card">
      <div class="card-header">
        <h2>{project['name']}</h2>
        <span class="card-type">{project['type']}</span>
      </div>
      <div class="card-address">{project['address']}</div>
      <div class="card-stats">
        <div class="card-stat"><div class="num">{value_short}</div><div class="lbl">Value</div></div>
        <div class="card-stat"><div class="num">{data['total_sheets']}</div><div class="lbl">Sheets</div></div>
        <div class="card-stat"><div class="num">{len(project['disciplines'])}</div><div class="lbl">Disciplines</div></div>
      </div>
      <div class="disciplines-list">{disc_tags}</div>
      <div class="card-cta">Run Analysis &rarr;</div>
    </a>"""


def build_landing_html(projects: List[Dict]) -> str:
    featured = build_featured_card(projects[0])  # Cypress Bend (Sunny Cove)
    grid = "\n    ".join(build_grid_card(p) for p in projects[1:])
    return LANDING_TEMPLATE.replace("{FEATURED_CARD}", featured).replace("{GRID_CARDS}", grid)


# --- PDF generation ----------------------------------------------------------

def generate_pdf_for_project(data: Dict) -> Path:
    """Generate the anonymized conflict report PDF using pipeline's report_generator."""
    from report_generator import generate_report  # imported here so failures surface per-project

    project_name = data["project"]["name"]
    out_path = DEMO_PORTAL / data["cfg"]["pdf_name"]
    generate_report(
        project_name=project_name,
        client_name="",
        conflicts=data["conflicts"],
        output_path=str(out_path),
        date=REPORT_DATE,
        analyst="Flikt.AI Automated Analysis",
    )
    return out_path


# --- Leak detection ----------------------------------------------------------

def final_leak_scan(data: Dict) -> List[Tuple[str, List[str]]]:
    """Scan the full anonymized output for surviving identifiers."""
    blob = json.dumps({
        "project": data["project"],
        "conflicts": data["conflicts"],
    }, ensure_ascii=False)
    return leak_scan(blob, data["source_key"])


# --- Main orchestration ------------------------------------------------------

def main() -> int:
    print("=" * 70)
    print("Flikt.AI Demo Builder")
    print("=" * 70)
    print(f"Source root:  {PIPELINE_RESULTS}")
    print(f"Output root:  {DEMO_PORTAL}")
    print()

    all_data: List[Dict] = []

    # --- Phase 1: load + filter + anonymize ---
    for cfg in PROJECTS:
        print(f"[{cfg['source_key']}] Loading {cfg['source_dir']}...")
        try:
            data = process_project(cfg)
        except FileNotFoundError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            return 1

        s = data["summary"]
        print(
            f"  conflicts={s['total_conflicts']} "
            f"(C={s['critical']} H={s['high']} M={s['medium']} L={s['low']})  "
            f"cost=${s['cost_low']:,}-${s['cost_high']:,}"
        )
        if data["gc_report"]:
            r = data["gc_report"]
            print(
                f"  GC filter: input={r['input_count']} output={r['output_count']} "
                f"dropped={r['total_dropped']} "
                f"(index_conflation={len(r['dropped_index_conflation'])}, "
                f"phantoms={len(r['dropped_phantom_sheets']) + len(r['dropped_phantom_by_id'])}, "
                f"spec_markup={len(r['dropped_spec_markup_missing'])}, "
                f"index_inversion={len(r['dropped_index_inversion'])}, "
                f"disputed={len(r['dropped_disputed'])}); "
                f"n471_deduped={len(r['n471_deduped'])}"
            )

        # Leak scan
        hits = final_leak_scan(data)
        if hits:
            print(f"  LEAK DETECTED in {cfg['source_key']}:", file=sys.stderr)
            for pattern, samples in hits:
                print(f"    {pattern!r} -> {samples}", file=sys.stderr)
            return 2
        print("  leak-scan: clean")

        all_data.append(data)

    # --- Phase 2: write HTML pages ---
    print()
    rendered: List[Tuple[Path, str]] = []
    for data in all_data:
        slug = data["cfg"]["slug"]
        rendered.append((DEMO_PORTAL / f"{slug}.html", build_page_html(data)))
    rendered.append((DEMO_PORTAL / "index.html", build_landing_html(all_data)))

    # Vocabulary gate — runs BEFORE anything is written, so a leak cannot ship
    # even if the operator ignores the console.
    vocab_failed = False
    for path, html in rendered:
        vhits = vocab_scan(html)
        if vhits:
            vocab_failed = True
            print(f"  VOCAB LEAK in {path.name}:", file=sys.stderr)
            for pattern, samples in vhits:
                print(f"    {pattern} -> {samples}", file=sys.stderr)
    if vocab_failed:
        print(
            "\nBUILD FAILED: forbidden internal vocabulary in rendered HTML.\n"
            "Nothing was written. Fix the strings (remember CSS/JS comments\n"
            "inside PAGE_TEMPLATE are published too) and re-run.",
            file=sys.stderr,
        )
        return 4

    for path, html in rendered:
        path.write_text(html, encoding="utf-8")
        print(f"  wrote {path.name} ({len(html):,} bytes)")
    print("  vocab-scan: clean")

    # --- Phase 4: PDF generation (DISABLED S181 — Greg removed PDF downloads
    # from demo. Function kept for easy revert; just re-enable this block).
    # for data in all_data:
    #     try:
    #         pdf_path = generate_pdf_for_project(data)
    #         size = pdf_path.stat().st_size
    #         print(f"  generated {pdf_path.name} ({size:,} bytes)")
    #     except Exception as e:
    #         print(f"  PDF ERROR for {data['cfg']['slug']}: {e}", file=sys.stderr)
    #         import traceback
    #         traceback.print_exc()
    #         return 3

    print()
    print("=" * 70)
    print("BUILD COMPLETE")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
