"""Generate 6 discipline-themed SVG placeholder sheets for the demo viewer pane.

Each SVG is ~1200x900 viewBox, ~5-10KB, looks like a credible engineering
drawing without containing any real customer content. Saved to
~/FLIKT/Coding/flikt-demo/sheets/ as demo_<discipline>_<sheet_id>.svg.

Run from repo root or from _build/:
    python3 _build/make_sheets.py
"""
from __future__ import annotations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "sheets"
OUT_DIR.mkdir(exist_ok=True)

# Common shell — light grid + title block + DEMO watermark.
# Inner content varies by discipline.
SHELL = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" preserveAspectRatio="xMidYMid meet">
<defs>
  <pattern id="grid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M40 0 L0 0 0 40" fill="none" stroke="#E2E8F0" stroke-width="0.5"/>
  </pattern>
  <pattern id="grid-major" x="0" y="0" width="200" height="200" patternUnits="userSpaceOnUse">
    <path d="M200 0 L0 0 0 200" fill="none" stroke="#CBD5E1" stroke-width="0.8"/>
  </pattern>
</defs>

<!-- Page background -->
<rect width="1200" height="900" fill="#FCFCFD"/>
<!-- Light grid (faint) -->
<rect width="1200" height="900" fill="url(#grid)" opacity="0.6"/>
<rect width="1200" height="900" fill="url(#grid-major)" opacity="0.45"/>

<!-- Outer border -->
<rect x="20" y="20" width="1160" height="860" fill="none" stroke="#0F172A" stroke-width="2"/>
<!-- Inner drawing border -->
<rect x="40" y="40" width="1120" height="820" fill="none" stroke="#0F172A" stroke-width="0.8"/>

{CONTENT}

<!-- Title block (bottom-right) -->
<g transform="translate(820, 720)">
  <rect width="340" height="140" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.2"/>
  <!-- Header bar -->
  <rect width="340" height="26" fill="#0a1929"/>
  <text x="12" y="18" fill="#E8A020" font-family="Inter, -apple-system, sans-serif" font-size="12" font-weight="700" letter-spacing="0.6">FLIKT.AI &#x2014; DEMO SHEET</text>
  <!-- Inner grid: project/sheet/date/scale -->
  <line x1="0" y1="26" x2="340" y2="26" stroke="#0F172A" stroke-width="0.8"/>
  <line x1="0" y1="62" x2="340" y2="62" stroke="#0F172A" stroke-width="0.5"/>
  <line x1="0" y1="98" x2="340" y2="98" stroke="#0F172A" stroke-width="0.5"/>
  <line x1="170" y1="62" x2="170" y2="140" stroke="#0F172A" stroke-width="0.5"/>
  <text x="10" y="42" fill="#64748B" font-family="Inter, sans-serif" font-size="8" letter-spacing="0.5">PROJECT</text>
  <text x="10" y="56" fill="#0F172A" font-family="Inter, sans-serif" font-size="11" font-weight="600">Demo Coordination Set</text>
  <text x="10" y="78" fill="#64748B" font-family="Inter, sans-serif" font-size="8" letter-spacing="0.5">SHEET</text>
  <text x="10" y="92" fill="#0F172A" font-family="Inter, sans-serif" font-size="13" font-weight="700">{SHEET_ID}</text>
  <text x="10" y="114" fill="#64748B" font-family="Inter, sans-serif" font-size="8" letter-spacing="0.5">TITLE</text>
  <text x="10" y="128" fill="#0F172A" font-family="Inter, sans-serif" font-size="9" font-weight="600">{SHEET_TITLE}</text>
  <text x="180" y="78" fill="#64748B" font-family="Inter, sans-serif" font-size="8" letter-spacing="0.5">DATE</text>
  <text x="180" y="92" fill="#0F172A" font-family="Inter, sans-serif" font-size="10" font-weight="600">2026-05-14</text>
  <text x="180" y="114" fill="#64748B" font-family="Inter, sans-serif" font-size="8" letter-spacing="0.5">SCALE</text>
  <text x="180" y="128" fill="#0F172A" font-family="Inter, sans-serif" font-size="10" font-weight="600">AS NOTED</text>
</g>

<!-- DEMO watermark (large, diagonal, very light) -->
<g transform="translate(600 450) rotate(-22)">
  <text x="0" y="0" text-anchor="middle" fill="#E2E8F0" opacity="0.55" font-family="Inter, sans-serif" font-size="180" font-weight="900" letter-spacing="20">DEMO</text>
</g>

<!-- Sheet label (top-right) -->
<g transform="translate(1100, 50)">
  <rect x="-60" y="-22" width="60" height="28" fill="#0a1929"/>
  <text x="-30" y="-3" text-anchor="middle" fill="#E8A020" font-family="Inter, sans-serif" font-size="14" font-weight="700">{SHEET_ID}</text>
</g>

<!-- Discipline tag (top-left) -->
<g transform="translate(50, 50)">
  <rect width="160" height="28" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="0.8"/>
  <text x="80" y="19" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">{DISC_TAG}</text>
</g>
</svg>
"""


def architectural_content() -> str:
    """Floor plan: room outlines, door swings, dimensions."""
    return """
<!-- Architectural floor plan -->
<g transform="translate(80, 110)">
  <!-- Outer building outline -->
  <rect x="0" y="0" width="720" height="540" fill="none" stroke="#0F172A" stroke-width="2.5"/>
  <!-- Interior walls -->
  <line x1="280" y1="0" x2="280" y2="320" stroke="#0F172A" stroke-width="1.8"/>
  <line x1="0" y1="320" x2="720" y2="320" stroke="#0F172A" stroke-width="1.8"/>
  <line x1="280" y1="180" x2="540" y2="180" stroke="#0F172A" stroke-width="1.4"/>
  <line x1="540" y1="0" x2="540" y2="180" stroke="#0F172A" stroke-width="1.4"/>
  <line x1="100" y1="320" x2="100" y2="540" stroke="#0F172A" stroke-width="1.4"/>
  <line x1="380" y1="320" x2="380" y2="540" stroke="#0F172A" stroke-width="1.4"/>
  <line x1="380" y1="430" x2="720" y2="430" stroke="#0F172A" stroke-width="1.4"/>
  <!-- Door swings (quarter arcs) -->
  <path d="M 60 320 A 40 40 0 0 0 100 280" fill="none" stroke="#64748B" stroke-width="0.8"/>
  <path d="M 280 100 A 40 40 0 0 1 320 60" fill="none" stroke="#64748B" stroke-width="0.8"/>
  <path d="M 380 380 A 40 40 0 0 0 420 340" fill="none" stroke="#64748B" stroke-width="0.8"/>
  <!-- Room labels -->
  <text x="140" y="160" fill="#475569" font-family="Inter, sans-serif" font-size="11" font-weight="600">LIVING</text>
  <text x="140" y="178" fill="#94A3B8" font-family="Inter, sans-serif" font-size="8">L-101  18&#39;-4&#34;</text>
  <text x="400" y="100" fill="#475569" font-family="Inter, sans-serif" font-size="11" font-weight="600">KITCHEN</text>
  <text x="400" y="118" fill="#94A3B8" font-family="Inter, sans-serif" font-size="8">K-102  14&#39;-2&#34;</text>
  <text x="600" y="100" fill="#475569" font-family="Inter, sans-serif" font-size="11" font-weight="600">DINING</text>
  <text x="600" y="118" fill="#94A3B8" font-family="Inter, sans-serif" font-size="8">D-103</text>
  <text x="400" y="260" fill="#475569" font-family="Inter, sans-serif" font-size="11" font-weight="600">CORRIDOR</text>
  <text x="40" y="430" fill="#475569" font-family="Inter, sans-serif" font-size="11" font-weight="600">BR-1</text>
  <text x="200" y="430" fill="#475569" font-family="Inter, sans-serif" font-size="11" font-weight="600">BATH</text>
  <text x="450" y="380" fill="#475569" font-family="Inter, sans-serif" font-size="11" font-weight="600">BR-2</text>
  <text x="450" y="490" fill="#475569" font-family="Inter, sans-serif" font-size="11" font-weight="600">MECH</text>
  <!-- Dimension callouts -->
  <line x1="0" y1="-20" x2="720" y2="-20" stroke="#64748B" stroke-width="0.5" stroke-dasharray="2 2"/>
  <text x="360" y="-26" text-anchor="middle" fill="#64748B" font-family="Inter, sans-serif" font-size="10">42&#39;-8&#34;</text>
  <!-- North arrow -->
  <g transform="translate(680, 60)">
    <circle cx="0" cy="0" r="22" fill="none" stroke="#0F172A" stroke-width="0.8"/>
    <polygon points="0,-18 6,8 0,2 -6,8" fill="#0F172A"/>
    <text x="0" y="-26" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="9" font-weight="700">N</text>
  </g>
</g>
"""


def plumbing_content() -> str:
    """Plumbing schedules: tables for fixtures + drain schedule."""
    rows = ""
    sample_rows = [
        ("WC-1", "WATER CLOSET (FLUSH VALVE)", "1.6 GPF", "2", '1/2"', '4"'),
        ("UR-1", "URINAL (FLUSH VALVE)", "0.5 GPF", "2", '1/2"', '2"'),
        ("LAV-1", "LAVATORY", "1.5 GPM", "2", '3/8"', '1-1/2"'),
        ("KS-1", "KITCHEN SINK (PRIVATE)", "2.2 GPM", "2", '3/8"', '1-1/2"'),
        ("SH-1", "SHOWER", "2.0 GPM", "2", '1/2"', '2"'),
        ("WB-1", "WASHER BOX", "4.0 GPM", "2", '1/2"', '2"'),
        ("HB-1", "HOSE BIBB", "3.0 GPM", "1", '3/4"', '—'),
    ]
    for i, (mark, desc, flow, hot, sup, dr) in enumerate(sample_rows):
        y = 60 + i * 26
        rows += f'''
  <rect x="0" y="{y-13}" width="700" height="26" fill="{'#F8FAFC' if i%2 else '#FFFFFF'}"/>
  <text x="14" y="{y+4}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11" font-weight="700">{mark}</text>
  <text x="80" y="{y+4}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{desc}</text>
  <text x="380" y="{y+4}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{flow}</text>
  <text x="490" y="{y+4}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{hot}</text>
  <text x="540" y="{y+4}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{sup}</text>
  <text x="620" y="{y+4}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{dr}</text>
  <line x1="0" y1="{y+13}" x2="700" y2="{y+13}" stroke="#E2E8F0" stroke-width="0.5"/>'''
    return f"""
<g transform="translate(80, 110)">
  <!-- Title -->
  <text x="0" y="-2" fill="#0F172A" font-family="Inter, sans-serif" font-size="14" font-weight="700">PLUMBING FIXTURE SCHEDULE</text>
  <!-- Header row -->
  <rect x="0" y="20" width="700" height="22" fill="#0a1929"/>
  <text x="14" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700" letter-spacing="0.5">MARK</text>
  <text x="80" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700" letter-spacing="0.5">DESCRIPTION</text>
  <text x="380" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700" letter-spacing="0.5">FLOW</text>
  <text x="490" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700" letter-spacing="0.5">HOT</text>
  <text x="540" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700" letter-spacing="0.5">SUPPLY</text>
  <text x="620" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700" letter-spacing="0.5">DRAIN</text>
  {rows}
  <!-- Table outer border -->
  <rect x="0" y="20" width="700" height="208" fill="none" stroke="#0F172A" stroke-width="1.2"/>
</g>

<!-- Second table: Drain Schedule -->
<g transform="translate(80, 410)">
  <text x="0" y="-2" fill="#0F172A" font-family="Inter, sans-serif" font-size="14" font-weight="700">PLUMBING DRAIN SCHEDULE</text>
  <rect x="0" y="20" width="700" height="22" fill="#0a1929"/>
  <text x="14" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">MARK</text>
  <text x="80" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">DESCRIPTION</text>
  <text x="320" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">MANUFACTURER</text>
  <text x="500" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">MODEL</text>
  <text x="620" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">SIZE</text>
  {''.join(f'<rect x="0" y="{42+i*26}" width="700" height="26" fill="{"#F8FAFC" if i%2 else "#FFFFFF"}"/><text x="14" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11" font-weight="700">{m}</text><text x="80" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{d}</text><text x="320" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{mf}</text><text x="500" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{md}</text><text x="620" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{sz}</text>' for i,(m,d,mf,md,sz) in enumerate([('FD-1','FLOOR DRAIN','ZURN','Z556',chr(0x32)+chr(0x22)),('FD-2','FLOOR DRAIN (LIGHT DUTY)','ZURN','Z415B',chr(0x32)+chr(0x22)),('HD-1','HUB DRAIN','ZURN','Z211',chr(0x33)+chr(0x22)),('RD-1','ROOF DRAIN','ZURN','Z164',chr(0x34)+chr(0x22))]))}
  <rect x="0" y="20" width="700" height="130" fill="none" stroke="#0F172A" stroke-width="1.2"/>
</g>
"""


def electrical_content() -> str:
    """Panel schedule: circuits table."""
    rows = ""
    sample = [
        (1, "LIGHTING - CORRIDOR", "20A/1P", "780", "120"),
        (3, "LIGHTING - LOBBY", "20A/1P", "920", "120"),
        (5, "RECEPT - CORRIDOR", "20A/1P", "540", "120"),
        (7, "RECEPT - MECH RM", "20A/1P", "1200", "120"),
        (9, "EXHAUST FAN EF-1", "20A/1P", "640", "120"),
        (11, "BOOSTER PUMP P-1", "30A/2P", "2400", "208"),
        (13, "WATER HEATER WH-1", "40A/2P", "4500", "208"),
        (15, "MAKEUP AIR MAU-1", "50A/3P", "8200", "480"),
        (17, "AHU-1", "60A/3P", "12000", "480"),
        (19, "ELEVATOR EL-1", "100A/3P", "18000", "480"),
        (21, "EMERGENCY LIGHTING", "20A/1P", "420", "120"),
        (23, "FIRE ALARM", "20A/1P", "350", "120"),
    ]
    for i, (ckt, desc, br, va, v) in enumerate(sample):
        y = 60 + i * 22
        bg = '#F8FAFC' if i % 2 else '#FFFFFF'
        rows += f'''
  <rect x="0" y="{y-12}" width="700" height="22" fill="{bg}"/>
  <text x="14" y="{y+3}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11" font-weight="700">{ckt}</text>
  <text x="60" y="{y+3}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{desc}</text>
  <text x="380" y="{y+3}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{br}</text>
  <text x="490" y="{y+3}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{va} VA</text>
  <text x="610" y="{y+3}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{v}V</text>'''
    return f"""
<g transform="translate(80, 110)">
  <text x="0" y="-2" fill="#0F172A" font-family="Inter, sans-serif" font-size="14" font-weight="700">PANEL &#39;LP-1&#39; SCHEDULE  &#x2014;  208/120V 3-PHASE 4-WIRE 225A MLO</text>
  <rect x="0" y="20" width="700" height="22" fill="#0a1929"/>
  <text x="14" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">CKT</text>
  <text x="60" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">DESCRIPTION</text>
  <text x="380" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">BREAKER</text>
  <text x="490" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">LOAD</text>
  <text x="610" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">VOLT</text>
  {rows}
  <rect x="0" y="20" width="700" height="278" fill="none" stroke="#0F172A" stroke-width="1.2"/>
</g>

<!-- One-line diagram callout -->
<g transform="translate(80, 460)">
  <text x="0" y="-2" fill="#0F172A" font-family="Inter, sans-serif" font-size="14" font-weight="700">ONE-LINE DIAGRAM (PARTIAL)</text>
  <!-- Utility -->
  <circle cx="40" cy="70" r="22" fill="none" stroke="#0F172A" stroke-width="1.5"/>
  <text x="40" y="74" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="13" font-weight="700">U</text>
  <text x="40" y="110" text-anchor="middle" fill="#475569" font-family="Inter, sans-serif" font-size="9">UTILITY</text>
  <!-- Service disconnect -->
  <line x1="62" y1="70" x2="140" y2="70" stroke="#0F172A" stroke-width="1.5"/>
  <rect x="140" y="55" width="60" height="30" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.5"/>
  <text x="170" y="74" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="10">800A</text>
  <text x="170" y="105" text-anchor="middle" fill="#475569" font-family="Inter, sans-serif" font-size="9">MAIN DISC.</text>
  <!-- Bus -->
  <line x1="200" y1="70" x2="600" y2="70" stroke="#0F172A" stroke-width="2.5"/>
  <!-- Branch panels -->
  <line x1="280" y1="70" x2="280" y2="120" stroke="#0F172A" stroke-width="1.5"/>
  <rect x="250" y="120" width="60" height="40" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.5"/>
  <text x="280" y="142" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="11" font-weight="700">LP-1</text>
  <text x="280" y="175" text-anchor="middle" fill="#475569" font-family="Inter, sans-serif" font-size="9">225A</text>
  <line x1="420" y1="70" x2="420" y2="120" stroke="#0F172A" stroke-width="1.5"/>
  <rect x="390" y="120" width="60" height="40" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.5"/>
  <text x="420" y="142" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="11" font-weight="700">LP-2</text>
  <text x="420" y="175" text-anchor="middle" fill="#475569" font-family="Inter, sans-serif" font-size="9">225A</text>
  <line x1="560" y1="70" x2="560" y2="120" stroke="#0F172A" stroke-width="1.5"/>
  <rect x="530" y="120" width="60" height="40" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.5"/>
  <text x="560" y="142" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="11" font-weight="700">DP-1</text>
  <text x="560" y="175" text-anchor="middle" fill="#475569" font-family="Inter, sans-serif" font-size="9">100A 480V</text>
</g>
"""


def structural_content() -> str:
    """Column grid + beam framing plan."""
    grid_rows = ['A', 'B', 'C', 'D', 'E']
    cols = list(range(1, 8))
    cells = ""
    for ri, r in enumerate(grid_rows):
        for ci, c in enumerate(cols):
            x = 100 + ci * 100
            y = 110 + ri * 110
            cells += f'''
  <circle cx="{x}" cy="{y}" r="6" fill="#0F172A"/>
  <text x="{x-14}" y="{y+4}" fill="#0F172A" font-family="Inter, sans-serif" font-size="10" font-weight="700">{r}-{c}</text>'''
    # Beam lines
    beams = ""
    for ci in range(len(cols)-1):
        for ri in range(len(grid_rows)):
            x1 = 100 + ci*100; x2 = 100 + (ci+1)*100; y = 110 + ri*110
            beams += f'<line x1="{x1+8}" y1="{y}" x2="{x2-8}" y2="{y}" stroke="#0F172A" stroke-width="1.4"/>'
    for ri in range(len(grid_rows)-1):
        for ci in range(len(cols)):
            x = 100 + ci*100; y1 = 110 + ri*110; y2 = 110 + (ri+1)*110
            beams += f'<line x1="{x}" y1="{y1+8}" x2="{x}" y2="{y2-8}" stroke="#0F172A" stroke-width="1.4"/>'
    return f"""
<g transform="translate(60, 90)">
  <text x="0" y="-2" fill="#0F172A" font-family="Inter, sans-serif" font-size="14" font-weight="700">LEVEL 2 FRAMING PLAN  &#x2014;  W12x26 TYP. U.N.O.</text>
  {beams}
  {cells}
  <!-- Beam size callouts -->
  <text x="155" y="106" fill="#475569" font-family="Inter, sans-serif" font-size="8">W12x26</text>
  <text x="255" y="106" fill="#475569" font-family="Inter, sans-serif" font-size="8">W14x30</text>
  <text x="355" y="106" fill="#475569" font-family="Inter, sans-serif" font-size="8">W16x36</text>
  <text x="155" y="216" fill="#475569" font-family="Inter, sans-serif" font-size="8">W12x26</text>
  <text x="255" y="216" fill="#475569" font-family="Inter, sans-serif" font-size="8">W12x26</text>
  <text x="355" y="216" fill="#475569" font-family="Inter, sans-serif" font-size="8">W12x26</text>
  <!-- Slab outline -->
  <rect x="80" y="90" width="640" height="450" fill="none" stroke="#94A3B8" stroke-width="0.8" stroke-dasharray="6 4"/>
</g>

<!-- Detail callout boxes -->
<g transform="translate(80, 580)">
  <text x="0" y="-4" fill="#0F172A" font-family="Inter, sans-serif" font-size="13" font-weight="700">TYPICAL CONNECTION DETAILS</text>
  <rect x="0" y="10" width="220" height="100" fill="#FFFFFF" stroke="#0F172A" stroke-width="1"/>
  <text x="14" y="32" fill="#0F172A" font-family="Inter, sans-serif" font-size="10" font-weight="700">BEAM-TO-COLUMN</text>
  <text x="14" y="48" fill="#64748B" font-family="Inter, sans-serif" font-size="9">DOUBLE-ANGLE SHEAR TAB</text>
  <text x="14" y="62" fill="#64748B" font-family="Inter, sans-serif" font-size="9">A325-N BOLTS, TYP.</text>
  <text x="14" y="95" fill="#94A3B8" font-family="Inter, sans-serif" font-size="9">REF. 1/S-501</text>
  <rect x="240" y="10" width="220" height="100" fill="#FFFFFF" stroke="#0F172A" stroke-width="1"/>
  <text x="254" y="32" fill="#0F172A" font-family="Inter, sans-serif" font-size="10" font-weight="700">BASE PLATE</text>
  <text x="254" y="48" fill="#64748B" font-family="Inter, sans-serif" font-size="9">1&#34; A572 GR.50</text>
  <text x="254" y="62" fill="#64748B" font-family="Inter, sans-serif" font-size="9">4 x 1-1/4&#34; ANCHOR ROD</text>
  <text x="254" y="95" fill="#94A3B8" font-family="Inter, sans-serif" font-size="9">REF. 2/S-501</text>
  <rect x="480" y="10" width="220" height="100" fill="#FFFFFF" stroke="#0F172A" stroke-width="1"/>
  <text x="494" y="32" fill="#0F172A" font-family="Inter, sans-serif" font-size="10" font-weight="700">SLAB EDGE</text>
  <text x="494" y="48" fill="#64748B" font-family="Inter, sans-serif" font-size="9">5&#34; CONC. NWT</text>
  <text x="494" y="62" fill="#64748B" font-family="Inter, sans-serif" font-size="9">3VLI20 DECK</text>
  <text x="494" y="95" fill="#94A3B8" font-family="Inter, sans-serif" font-size="9">REF. 3/S-501</text>
</g>
"""


def mechanical_content() -> str:
    """HVAC duct layout + equipment schedule."""
    return """
<!-- Duct layout (top half) -->
<g transform="translate(80, 110)">
  <text x="0" y="-2" fill="#0F172A" font-family="Inter, sans-serif" font-size="14" font-weight="700">LEVEL 2 HVAC LAYOUT  &#x2014;  RTU-1 SUPPLY/RETURN</text>
  <!-- Outer building -->
  <rect x="0" y="20" width="720" height="320" fill="none" stroke="#0F172A" stroke-width="2"/>
  <!-- Main supply duct (red-ish line for SA) -->
  <rect x="20" y="60" width="680" height="14" fill="#FEF3C7" stroke="#D97706" stroke-width="1"/>
  <text x="350" y="71" text-anchor="middle" fill="#9A6E0F" font-family="Inter, sans-serif" font-size="9" font-weight="700">SA  24x12</text>
  <!-- Branch supply ducts -->
  <rect x="120" y="74" width="10" height="80" fill="#FEF3C7" stroke="#D97706" stroke-width="0.8"/>
  <rect x="280" y="74" width="10" height="120" fill="#FEF3C7" stroke="#D97706" stroke-width="0.8"/>
  <rect x="440" y="74" width="10" height="100" fill="#FEF3C7" stroke="#D97706" stroke-width="0.8"/>
  <rect x="600" y="74" width="10" height="140" fill="#FEF3C7" stroke="#D97706" stroke-width="0.8"/>
  <!-- Return air -->
  <rect x="20" y="280" width="680" height="14" fill="#DBEAFE" stroke="#2563EB" stroke-width="1"/>
  <text x="350" y="291" text-anchor="middle" fill="#1E40AF" font-family="Inter, sans-serif" font-size="9" font-weight="700">RA  24x16</text>
  <!-- VAV boxes -->
  <rect x="105" y="150" width="40" height="30" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.2"/>
  <text x="125" y="170" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="9" font-weight="700">VAV-1</text>
  <rect x="265" y="190" width="40" height="30" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.2"/>
  <text x="285" y="210" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="9" font-weight="700">VAV-2</text>
  <rect x="425" y="170" width="40" height="30" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.2"/>
  <text x="445" y="190" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="9" font-weight="700">VAV-3</text>
  <rect x="585" y="210" width="40" height="30" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.2"/>
  <text x="605" y="230" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="9" font-weight="700">VAV-4</text>
  <!-- Diffusers -->
  <g fill="#FFFFFF" stroke="#0F172A" stroke-width="0.8">
    <rect x="60" y="220" width="24" height="24"/><line x1="60" y1="220" x2="84" y2="244"/><line x1="60" y1="244" x2="84" y2="220"/>
    <rect x="180" y="220" width="24" height="24"/><line x1="180" y1="220" x2="204" y2="244"/><line x1="180" y1="244" x2="204" y2="220"/>
    <rect x="340" y="240" width="24" height="24"/><line x1="340" y1="240" x2="364" y2="264"/><line x1="340" y1="264" x2="364" y2="240"/>
    <rect x="500" y="230" width="24" height="24"/><line x1="500" y1="230" x2="524" y2="254"/><line x1="500" y1="254" x2="524" y2="230"/>
    <rect x="640" y="230" width="24" height="24"/><line x1="640" y1="230" x2="664" y2="254"/><line x1="640" y1="254" x2="664" y2="230"/>
  </g>
</g>

<!-- Equipment schedule (bottom) -->
<g transform="translate(80, 470)">
  <text x="0" y="-2" fill="#0F172A" font-family="Inter, sans-serif" font-size="14" font-weight="700">MECHANICAL EQUIPMENT SCHEDULE</text>
  <rect x="0" y="20" width="700" height="22" fill="#0a1929"/>
  <text x="14" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">TAG</text>
  <text x="80" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">DESCRIPTION</text>
  <text x="340" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">CAPACITY</text>
  <text x="490" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">MFR.</text>
  <text x="610" y="35" fill="#E8A020" font-family="Inter, sans-serif" font-size="10" font-weight="700">MODEL</text>
""" + "".join(f'<rect x="0" y="{42+i*26}" width="700" height="26" fill="{"#F8FAFC" if i%2 else "#FFFFFF"}"/><text x="14" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11" font-weight="700">{t}</text><text x="80" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{d}</text><text x="340" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{c}</text><text x="490" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{mf}</text><text x="610" y="{42+i*26+17}" fill="#0F172A" font-family="Inter, sans-serif" font-size="11">{md}</text>'
                for i, (t,d,c,mf,md) in enumerate([
    ("RTU-1", "ROOFTOP UNIT (PACKAGED)", "12 TONS / 144 MBH", "TRANE", "WSC120"),
    ("VAV-1", "VAV BOX W/ HOT WATER COIL", "400 CFM", "TITUS", "DESV"),
    ("EF-1",  "EXHAUST FAN", "600 CFM @ 0.4 IN", "GREENHECK", "CUE-100"),
    ("WH-1",  "GAS WATER HEATER", "199 MBH / 75 GAL", "RHEEM", "G75-200"),
])) + """
  <rect x="0" y="20" width="700" height="130" fill="none" stroke="#0F172A" stroke-width="1.2"/>
</g>
"""


def civil_content() -> str:
    """Site plan: building footprint + landscape."""
    return """
<g transform="translate(60, 90)">
  <text x="0" y="-2" fill="#0F172A" font-family="Inter, sans-serif" font-size="14" font-weight="700">SITE PLAN  &#x2014;  GRADING &amp; UTILITIES</text>
  <!-- Site boundary -->
  <rect x="0" y="20" width="720" height="540" fill="#FAFCFA" stroke="#0F172A" stroke-width="2" stroke-dasharray="14 6"/>
  <!-- Building footprint -->
  <rect x="160" y="120" width="400" height="240" fill="#F1F5F9" stroke="#0F172A" stroke-width="2"/>
  <text x="360" y="248" text-anchor="middle" fill="#475569" font-family="Inter, sans-serif" font-size="14" font-weight="700">PROPOSED</text>
  <text x="360" y="266" text-anchor="middle" fill="#475569" font-family="Inter, sans-serif" font-size="14" font-weight="700">BUILDING</text>
  <text x="360" y="282" text-anchor="middle" fill="#94A3B8" font-family="Inter, sans-serif" font-size="10">FFE 12.50</text>
  <!-- Sidewalks -->
  <rect x="160" y="370" width="400" height="20" fill="#FFFFFF" stroke="#94A3B8" stroke-width="0.8" stroke-dasharray="4 3"/>
  <text x="360" y="384" text-anchor="middle" fill="#94A3B8" font-family="Inter, sans-serif" font-size="9">CONCRETE WALK (TYP.)</text>
  <!-- Parking spaces -->
  <g stroke="#0F172A" stroke-width="0.8">
    <line x1="0" y1="420" x2="720" y2="420"/>
    <line x1="0" y1="500" x2="720" y2="500"/>""" + "".join(f'<line x1="{30+i*40}" y1="420" x2="{30+i*40}" y2="500"/>' for i in range(18)) + """
  </g>
  <text x="20" y="486" fill="#94A3B8" font-family="Inter, sans-serif" font-size="9">PARKING (18 SPACES)</text>
  <!-- Utility lines -->
  <line x1="0" y1="80" x2="720" y2="80" stroke="#2563EB" stroke-width="1.4" stroke-dasharray="10 4"/>
  <text x="14" y="74" fill="#1E40AF" font-family="Inter, sans-serif" font-size="9" font-weight="700">DOMESTIC WATER (DW)  6&#34;</text>
  <line x1="0" y1="100" x2="720" y2="100" stroke="#D97706" stroke-width="1.4" stroke-dasharray="6 6"/>
  <text x="14" y="94" fill="#9A6E0F" font-family="Inter, sans-serif" font-size="9" font-weight="700">GAS LINE (G)  4&#34;</text>
  <line x1="0" y1="540" x2="720" y2="540" stroke="#16A34A" stroke-width="1.4" stroke-dasharray="3 3"/>
  <text x="14" y="534" fill="#0F5E2D" font-family="Inter, sans-serif" font-size="9" font-weight="700">SANITARY (SAN)  8&#34;</text>
  <!-- Contour lines -->
  <path d="M 0 200 Q 200 180, 360 200 T 720 220" fill="none" stroke="#94A3B8" stroke-width="0.6"/>
  <path d="M 0 330 Q 240 310, 400 330 T 720 350" fill="none" stroke="#94A3B8" stroke-width="0.6"/>
  <text x="100" y="195" fill="#94A3B8" font-family="Inter, sans-serif" font-size="8">12.0</text>
  <text x="100" y="325" fill="#94A3B8" font-family="Inter, sans-serif" font-size="8">11.0</text>
  <!-- North arrow -->
  <g transform="translate(650, 70)">
    <circle cx="0" cy="0" r="22" fill="#FFFFFF" stroke="#0F172A" stroke-width="0.8"/>
    <polygon points="0,-18 6,8 0,2 -6,8" fill="#0F172A"/>
    <text x="0" y="-26" text-anchor="middle" fill="#0F172A" font-family="Inter, sans-serif" font-size="9" font-weight="700">N</text>
  </g>
</g>
"""


# Map: (filename, sheet_id, sheet_title, discipline_tag, content_fn)
VARIANTS = [
    ("demo_arch_01.svg",     "A-201",  "FLOOR PLAN — LEVEL 1",         "ARCHITECTURAL", architectural_content),
    ("demo_plumb_01.svg",    "P-501",  "PLUMBING SCHEDULES",           "PLUMBING",      plumbing_content),
    ("demo_elec_01.svg",     "E-101",  "POWER PLAN & PANEL SCHEDULE",  "ELECTRICAL",    electrical_content),
    ("demo_struc_01.svg",    "S-201",  "FRAMING PLAN — LEVEL 2",       "STRUCTURAL",    structural_content),
    ("demo_mech_01.svg",     "M-201",  "HVAC LAYOUT — LEVEL 2",        "MECHANICAL",    mechanical_content),
    ("demo_civil_01.svg",    "C-101",  "SITE PLAN — GRADING & UTIL.",  "CIVIL",         civil_content),
]


def main() -> int:
    print(f"Writing 6 SVG sheets to {OUT_DIR}")
    for fname, sheet_id, sheet_title, disc, content_fn in VARIANTS:
        svg = SHELL.format(
            CONTENT=content_fn(),
            SHEET_ID=sheet_id,
            SHEET_TITLE=sheet_title,
            DISC_TAG=disc,
        )
        (OUT_DIR / fname).write_text(svg)
        kb = (OUT_DIR / fname).stat().st_size / 1024
        print(f"  wrote {fname:<24}  {kb:5.1f} KB  ({disc} / {sheet_id})")
    print(f"\nDone. {len(VARIANTS)} sheets in {OUT_DIR}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
