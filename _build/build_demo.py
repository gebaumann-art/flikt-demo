#!/usr/bin/env python3
"""Flikt.AI demo page builder.

Loads 4 real results.json files -> applies GC filter (Eastside only) ->
anonymizes -> regenerates 4 HTML pages + 4 PDF reports + landing index.html.

Usage:
  cd ~/FLIKT/Plan\\ Sets\\ Copy/demo-portal && python3 _build/build_demo.py

Prerequisites:
  - FLIKT pipeline at ~/FLIKT/Coding/pipeline/ (for report_generator.py)
  - reportlab installed in the active Python environment

Output goes into the parent demo-portal/ directory.
"""
from __future__ import annotations

import json
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

# --- Source configuration ----------------------------------------------------

PROJECTS = [
    {
        # S180 refresh: source is Millenium Apartments (M2 at Millenia) run on
        # the current S180 production pipeline. 703 sheets, 14 disciplines,
        # 160 conflicts (11 C / 80 H / 59 M / 10 L), ~$1.18M-$3.45M exposure.
        "source_key": "eastside_lofts",
        "source_dir": "Millenium_Apartments_S180_run1",
        "slug": "eastside-lofts",
        "pdf_name": "FliktAI_Eastside_Lofts_Report.pdf",
        "apply_gc_filter": False,  # Source already filtered upstream in S180
        "render_cap": 100,         # Top 100 by severity (large set)
    },
    {
        # S180 refresh: same Salon Lofts source as before, but on the current
        # S180 pipeline. 25 sheets, 4 disciplines, 44 conflicts (8 C / 15 H).
        "source_key": "metro_salon_studios",
        "source_dir": "Salon_Lofts_S180_run1",
        "slug": "metro-salon",
        "pdf_name": "FliktAI_Metro_Salon_Studios_Report.pdf",
        "apply_gc_filter": False,
        "render_cap": 9999,
    },
    {
        # S180 refresh: L'Hermitage S173 phase1 consensus run (F1=0.919).
        # 31 sheets, 5 disciplines, 29 conflicts (5 C / 11 H), $145K-$322K.
        "source_key": "the_atrium",
        "source_dir": "LHermitage_S173_phase1",
        "slug": "the-atrium",
        "pdf_name": "FliktAI_The_Atrium_Report.pdf",
        "apply_gc_filter": False,
        "render_cap": 9999,
    },
    {
        # S180 refresh: 9332 Carlyle (luxury single-family renovation & addition).
        # 64 sheets, 7 disciplines, 44 conflicts (4 C / 21 H), $91K-$216K.
        "source_key": "meridian_residence",
        "source_dir": "Carlyle_S180_run1",
        "slug": "meridian-residence",
        "pdf_name": "FliktAI_Meridian_Residence_Report.pdf",
        "apply_gc_filter": False,
        "render_cap": 9999,
    },
]

REPORT_DATE = "May 14, 2026"

# --- Discipline-pair + summary recomputation ---------------------------------

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def _count_discipline_pairs(conflicts: List[Dict]) -> int:
    pairs = set()
    for c in conflicts:
        a = (c.get("disc_a") or "").strip()
        b = (c.get("disc_b") or "").strip()
        if a and b:
            pairs.add(tuple(sorted([a, b])))
    return len(pairs)


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
        "discipline_pairs": _count_discipline_pairs(conflicts),
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
    stages.append({"pct": 52, "text": "Running cross-discipline conflict detection...",
                   "log": f"Comparing elements across {summary['discipline_pairs']} discipline pairs"})
    stages.append({"pct": 60, "text": "Checking code compliance...",
                   "log": "\u26A0 Detecting building-code + accessibility issues"})
    stages.append({"pct": 68, "text": "Detecting spatial clashes...",
                   "log": "\u26A0 Scanning for geometric conflicts between disciplines"})
    stages.append({"pct": 75, "text": "Checking MEP coordination gaps...",
                   "log": "\u26A0 Identifying missing equipment circuits, routing conflicts"})
    stages.append({"pct": 82, "text": "Scoring severity (50-point model)...",
                   "log": (f"Scored {summary['total_conflicts']} conflicts: "
                           f"{summary['critical']} Critical, {summary['high']} High, "
                           f"{summary['medium']} Medium, {summary['low']} Low")})
    stages.append({"pct": 92, "text": "Estimating cost and schedule impacts...",
                   "log": f"Total cost exposure: ${summary['cost_low']:,} \u2013 ${summary['cost_high']:,}"})
    stages.append({"pct": 100, "text": "Analysis complete!",
                   "log": (f"Report generated \u2014 {summary['total_conflicts']} conflicts "
                           f"across {summary['discipline_pairs']} discipline pairs")})
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

    # Anonymize every conflict
    anonymized = [anonymize_conflict(c, source_key) for c in conflicts]

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

def build_page_html(data: Dict) -> str:
    cfg = data["cfg"]
    project = data["project"]
    summary = data["summary"]
    disciplines_list = list(project["disciplines"].keys())
    stages = make_stages(project["name"], data["total_sheets"], disciplines_list, summary)

    data_json = json.dumps({
        "project": project,
        "summary": summary,
        "conflicts": data["conflicts"],
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
<script>
(function(){try{var s=localStorage.getItem('flikt-theme');
if(!s){s=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}
document.documentElement.setAttribute('data-theme',s)}catch(e){}})();
</script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#0a1929;--navy-dark:#141F36;--amber:#E8A020;--amber-light:#F5C96B;
--critical:#DC2626;--high:#EA580C;--medium:#D97706;--low:#16A34A;
--bg:#F5F7FA;--card:#FFFFFF;--card-hover:#F8FAFC;
--text:#0F172A;--text-muted:#64748B;--border:#E2E8F0;
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
.real-ai-badge{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;
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
.hero{text-align:center;margin:48px 32px 12px}
.hero h1{font-size:32px;font-weight:700;margin-bottom:8px}
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
.card-type{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;
color:var(--text-muted);background:var(--chip-bg);padding:4px 10px;border-radius:4px;
white-space:normal;flex-shrink:0;max-width:100%}
.card-address{font-size:13px;color:var(--text-muted);margin-bottom:16px}
.card-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px}
.card-stat{text-align:center;padding:10px 6px;background:var(--stat-bg);border-radius:8px}
.card-stat .num{font-size:18px;font-weight:800}
.card-stat .lbl{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--text-muted);margin-top:2px}
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
    featured = build_featured_card(projects[0])  # Eastside
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
            f"cost=${s['cost_low']:,}-${s['cost_high']:,}  pairs={s['discipline_pairs']}"
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
    for data in all_data:
        slug = data["cfg"]["slug"]
        html = build_page_html(data)
        out = DEMO_PORTAL / f"{slug}.html"
        out.write_text(html, encoding="utf-8")
        print(f"  wrote {out.name} ({len(html):,} bytes)")

    # --- Phase 3: write landing page ---
    landing = build_landing_html(all_data)
    landing_path = DEMO_PORTAL / "index.html"
    landing_path.write_text(landing, encoding="utf-8")
    print(f"  wrote index.html ({len(landing):,} bytes)")

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
    sys.exit(main())
