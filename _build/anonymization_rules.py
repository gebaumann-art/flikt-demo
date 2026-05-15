"""Anonymization rules for Flikt.AI demo content.

Rules are organized per-source-project because:
  - Metro Salon Studios keeps "Maitland" (anonymized address matches real city)
  - Meridian Residence keeps "Surfside" (same)
  - Eastside Lofts scrubs "Corinth" (moved to San Antonio)
  - The Atrium scrubs "Hermitage" (renamed)

Each entry in PROJECT_RULES["<source>"] has:
  - "scrub":   [(regex, replacement), ...]  applied to every string field
  - "leaks":   [regex, ...]                 leak-detector patterns (must not survive)
  - "project": {anonymized project metadata}

See handoff §3 (`FliktAI_Demo_Refresh_Handoff_Cowork_S114.pdf`) and §4 for the
canonical source-to-anonymized mapping.
"""
import re
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Per-project anonymization rule sets
# ---------------------------------------------------------------------------

PROJECT_RULES: Dict[str, Dict] = {
    "eastside_lofts": {
        "scrub": [
            # S180 refresh: source is Millenium Apartments (M2 at Millenia).
            # Anonymized address is San Antonio, TX -- so Maitland would be
            # a cross-ref leak. Scrub defensively.
            (r"\bMillenium\s+Apartments[_ ]?run\d+\b", "Eastside_Lofts_run1"),
            (r"\bMillen+ium\s+Apartments\b", "Eastside Lofts"),
            (r"\bM2[_ ]at[_ ]Millenia\b", "the project"),
            (r"\bMillenia\b", "the project area"),
            (r"\bMillen+ium\b", "the site"),
            (r"\bMaitland\b", "the city"),
            # Legacy Parkway rules (harmless when not present in source):
            (r"\bParkway[_ ]Lofts[_ ]Demo[_ ]S\d+\b", "Eastside_Lofts"),
            (r"\bParkway Lofts\b", "Eastside Lofts"),
            (r"\bParkway\b", "the site"),
            (r"\b1671\s*Residential\b", "the project"),
            (r"\b1671\b", ""),
            (r"\bCity of Corinth\b", "the jurisdiction"),
            (r"\bCorinth_[A-Za-z0-9_]+", "site_document"),
            (r"\bCorinth\b", "the site"),
        ],
        "leaks": [
            r"\bMillenium\b", r"\bMillennium\b", r"\bMillenia\b",
            r"\bMaitland\b",
            r"\bParkway\b", r"\b1671\b", r"\bCorinth\b",
        ],
        "project": {
            "id": "demo-eastside",
            "name": "Eastside Lofts",
            "name_long": "Eastside Lofts — New Construction",
            "address": "1850 Eastside Blvd, San Antonio, TX 78215",
            "type": "Multifamily New Construction — 320 Units",
            "construction_value": 42_000_000,
            "construction_value_display": "$42,000,000",
        },
    },
    "metro_salon_studios": {
        "scrub": [
            # S180 refresh: source name is "Salon Lofts S180_run1".
            (r"\bSalon\s+Lofts\s+S\d+(?:_run\d+)?\b", "Metro Salon Studios"),
            # Legacy 400N source variants:
            (r"\b400N[_ ]Salon[_ ]Lofts\b", "Metro Salon Studios"),
            (r"\b400N Salon Lofts\b", "Metro Salon Studios"),
            (r"\b400 North Salon Lofts\b", "Metro Salon Studios"),
            (r"\bSalon Lofts\b", "Metro Salon Studios"),
            (r"\b400N\b", "the tenant space"),
            (r"\b400 North\b", "the tenant space"),
            # Intentionally NOT scrubbing "Maitland" -- anonymized address is
            # also in Maitland per handoff §3.2, so no cross-ref leak.
        ],
        "leaks": [
            r"\b400N\b", r"\b400 North\b", r"\bSalon Lofts\b",
        ],
        "project": {
            "id": "demo-metro-salon",
            "name": "Metro Salon Studios",
            "name_long": "Metro Salon Studios — Commercial Tenant Fit-Out",
            "address": "400 Metro Center Blvd, Suite 112, Maitland, FL 32751",
            "type": "Commercial Tenant Fit-Out",
            "construction_value": 285_000,
            "construction_value_display": "$285,000",
        },
    },
    "the_atrium": {
        "scrub": [
            (r"\bLa[_ ]Hermitage[_ ]Lobby[_ ]Terminal\b", "The Atrium Lobby"),
            (r"\bLa[_ ]Hermitage[_ ]Lobby\b", "The Atrium Lobby"),
            (r"\bLa[_ ]Hermitage\b", "The Atrium"),
            (r"\bL['\u2019]Hermitage\b", "The Atrium"),
            (r"\bHermitage\b", "The Atrium"),
            (r"\bPenthouse\b", "upper unit"),
        ],
        "leaks": [
            r"\bHermitage\b", r"\bPenthouse\b",
        ],
        "project": {
            "id": "demo-the-atrium",
            "name": "The Atrium",
            "name_long": "The Atrium — Lobby Renovation",
            "address": "2500 Bayshore Drive, Miami Beach, FL 33140",
            "type": "Multifamily Common Area Renovation",
            "construction_value": 1_200_000,
            "construction_value_display": "$1,200,000",
        },
    },
    "meridian_residence": {
        "scrub": [
            # S180 refresh: source is 9332 Carlyle Ave (single-family
            # renovation & addition). Conflict sheets contain raw filenames
            # like "0bcb3cc9_Greenblatt-Itenberg-E4.pdf" -- normalize those to
            # the bare sheet code first, then scrub residual identifiers.
            (r"\b[a-f0-9]{8}_Greenblatt[-_]Itenberg[-_]([A-Za-z][A-Za-z0-9.\-]*?)(?:_p\d+)?\.(?:pdf|jpg|jpeg|png)\b",
             r"\1"),
            (r"\b[a-f0-9]{8}_Greenblatt[-_]Itenberg(?:_[A-Za-z_]+)?\.(?:pdf|jpg|jpeg|png)\b",
             "the architect's reference"),
            (r"\b9332[_ ]Carlyle[_ ]run\d+\b", "Meridian_Residence_run1"),
            (r"\b9332\s*Carlyle\s*Ave\b", "425 Meridian Ave"),
            (r"\b9332\s*Carlyle\b", "Meridian Residence"),
            (r"\bGreenblatt[-_ ]Itenberg\s+Residence\b", "the residence"),
            (r"\bGreenblatt[-_ ]Itenberg\b", "the architect"),
            (r"\bGreenblatt\b", "the architect"),
            (r"\bItenberg\b", "the architect"),
            (r"\bCarlyle\s+Ave(?:nue)?\b", "Meridian Ave"),
            (r"\bCarlyle\b", "the residence"),
            (r"\b9332\b", "425"),
            # Legacy Abbott rules (harmless when not present in source):
            (r"\b9272[_ ]Abbott[_ ]Ave[_ ]Construction[_ ]Documents\b", "Meridian_Residence"),
            (r"\b9272 Abbott Ave\b", "425 Meridian Ave"),
            (r"\b9272\s*Abbott\b", "the residence"),
            (r"\bAbbott Ave\b", "Meridian Ave"),
            (r"\bAbbott\b", "the residence"),
            (r"\b9272\b", "425"),
            # Surfside + Miami-Dade + Florida: KEEP -- anonymized address is
            # Surfside, FL (Miami-Dade County), so these are not leaks.
        ],
        "leaks": [
            r"\bGreenblatt\b", r"\bItenberg\b",
            r"\bCarlyle\b", r"\b9332\b",
            r"\bAbbott\b", r"\b9272\b",
        ],
        "project": {
            "id": "demo-meridian",
            "name": "Meridian Residence",
            "name_long": "Meridian Residence — Single Family New Construction",
            "address": "425 Meridian Ave, Surfside, FL 33154",
            "type": "Single Family New Construction",
            "construction_value": 3_200_000,
            "construction_value_display": "$3,200,000",
        },
    },
}


# ---------------------------------------------------------------------------
# Firm / engineer patterns (applied to all projects)
# ---------------------------------------------------------------------------

FIRM_SUFFIXES = (
    r"(?:Consulting|Engineering|Architects?|Engineers?|"
    r"Design Group|Associates|PLLC|LLP|PLC|, Inc\.|, LLC|, P\.A\.)"
)
FIRM_PATTERN = re.compile(
    rf"\b(?:[A-Z][A-Za-z\-']{{1,25}}\s+){{1,4}}(?:&\s+)?{FIRM_SUFFIXES}\b"
)


def _replace_firm(match: re.Match) -> str:
    phrase = match.group(0).lower()
    if "architect" in phrase:
        return "the architect"
    if "struct" in phrase:
        return "the structural engineer"
    if "mechanic" in phrase or "mep" in phrase or "hvac" in phrase:
        return "the MEP engineer"
    if "electric" in phrase:
        return "the electrical engineer"
    if "civil" in phrase:
        return "the civil engineer"
    if "landscape" in phrase:
        return "the landscape architect"
    return "the design team"


# ---------------------------------------------------------------------------
# Sheet-ref normalization (applied to all projects)
# Matches A-101, A-101A, S-201, M-000.01, MEP-200.01, ID-3.10A, C0.0, E101.02
# Collapses to discipline-letter + first-nonzero-digit.
# ---------------------------------------------------------------------------

SHEET_PATTERN = re.compile(r"\b([A-Z]{1,4})-?(\d{1,4})(?:\.\d{1,3})?([A-Z])?\b")


def _collapse_sheet(match: re.Match) -> str:
    disc, num = match.group(1), match.group(2)
    first_nonzero = next((d for d in num if d != "0"), "1")
    return f"{disc}{first_nonzero}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def anonymize_text(text: str, source_key: str) -> str:
    """Apply anonymization for the given source project to a string."""
    if not text:
        return text
    rules = PROJECT_RULES[source_key]
    out = text
    # Project-specific scrubs are case-insensitive so PARKWAY / parkway / Parkway
    # all get caught. Replacement strings stay as authored (usually lowercase).
    for pattern, replacement in rules["scrub"]:
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    # Firm names (case-sensitive since pattern already requires Capitalized words)
    out = FIRM_PATTERN.sub(_replace_firm, out)
    # Sheet-ref normalization
    out = SHEET_PATTERN.sub(_collapse_sheet, out)
    # Collapse residual double-spaces from deletions
    out = re.sub(r"  +", " ", out).strip()
    return out


def anonymize_sheet_list(sheets: List[str], source_key: str) -> List[str]:
    """Normalize each sheet ref, dropping empties and deduping."""
    if not sheets:
        return sheets
    out = []
    for s in sheets:
        if not isinstance(s, str):
            out.append(s)
            continue
        stripped = s.strip()
        m = SHEET_PATTERN.match(stripped)
        if m and m.end() == len(stripped):
            out.append(_collapse_sheet(m))
        else:
            out.append(anonymize_text(stripped, source_key))
    seen = set()
    return [x for x in out if x and not (x in seen or seen.add(x))]


def anonymize_conflict(conflict: Dict, source_key: str) -> Dict:
    """Anonymize every string field on a conflict. Preserves numerics, flags, scores."""
    c = dict(conflict)
    for key in ("title", "description", "recommended_action", "location", "source", "type"):
        if key in c and isinstance(c[key], str):
            c[key] = anonymize_text(c[key], source_key)
    if "sheets" in c and isinstance(c["sheets"], list):
        c["sheets"] = anonymize_sheet_list(c["sheets"], source_key)
    return c


def leak_scan(text: str, source_key: str) -> List[Tuple[str, List[str]]]:
    """Return list of (pattern, sample_hits) for any surviving identifiers."""
    hits = []
    for pattern in PROJECT_RULES[source_key]["leaks"]:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            hits.append((pattern, list(set(matches))[:5]))
    return hits


def get_project_metadata(source_key: str) -> Dict:
    """Return the anonymized project metadata dict for this source."""
    return dict(PROJECT_RULES[source_key]["project"])
