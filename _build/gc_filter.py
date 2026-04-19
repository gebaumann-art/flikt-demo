"""GC disposition filter for the Eastside Lofts demo.

Drives off the S112 feedback review. Three filters stack on the raw
509-conflict source set:

  1. Drop confirmed False Positives (~35): civil/arch index conflation,
     phantom sheets, spec-markup-missing, A-001/A-002 index-inversion bug.
  2. Drop substantive Disputes (8): CV508, N467, N471, GEO525, GEO527,
     N457, N463, N465, T460. C376/C377 are corrected rather than dropped.
  3. Presentation-layer N471 dedup: truncate any >10 repeated sheet refs
     in a single field to the first 10 unique entries plus "(and N more)".

Note: earlier versions of this filter also tagged validated TPs with a
badge, but that badge reveals the reviewer's identity and has been removed
to keep the demo fully anonymized.
"""
import re
from typing import Dict, List, Tuple


# --- Filter 1A: civil/arch index conflation ---
# NE confirmed each of these sheets IS listed in the architectural index.
# Drop any conflict where title/description claims these are "missing from index".
INDEX_CONFLATION_SHEETS = {
    "C-3.3", "C-1.1", "C-2.1", "C-2.2", "C-2.3", "C-2.4", "C-2.5", "C-3.0",
    "C-4.1", "C-5.0", "C-7.0", "C-8.1", "C-9.1",
    "M-000.01", "M-251.01", "M-252.01", "M-601.01",
    "MEP-200.01", "MEP-210.01", "MEP-220.01",
    "G-90", "G-40", "FR-5.1", "FB-1.0",
    "FD-2.2", "FD-3.0", "FD-4.0", "FD-5.0", "FD-6.0", "FD-7.0", "FD-8.0", "FD-9.0",
    "SW-3.1", "S-4", "F-3", "S-1",
    "A-040", "A-041", "A-042", "A-052", "A-053", "A-054", "A-055", "A-056",
    "A-057", "A-060", "A-061", "A-070", "A-071", "A-072", "A-073", "A-074",
    "A-075", "A-090", "A-100",
    "L-15",
}

# --- Filter 1B: phantom/hallucinated sheets ---
# NE confirmed these sheets do NOT exist.
PHANTOM_SHEETS = {
    "A813", "P1", "A2.1", "L9", "F-8", "F-5", "D-3.4", "FB-7", "RC-1",
    # The A-001/A-002 case is handled separately (it's the index itself).
}
PHANTOM_CONFLICT_IDS = {"C379", "C381", "C383", "G524"}

# --- Filter 1D: A-001/A-002 index-inversion bug ---
INDEX_SHEETS = {"A-001", "A-002"}

# --- Filter 2: NE substantive disputes (drop entirely) ---
DISPUTED_CONFLICT_IDS = {
    "CV508", "N467", "N471", "GEO525", "GEO527", "N457", "N463", "N465", "T460",
}

# --- Filter 2b: C376/C377 corrected instead of dropped ---
AMENDMENT_CORRECTION_IDS = {"C376", "C377"}
AMENDMENT_CORRECTION_REPLACEMENTS: List[Tuple[str, str]] = [
    (r"NEC only", "FBC Chapter 11 referenced"),
    (r"cites NEC only", "cites FBC Chapter 11"),
]

def _references_any_sheet(conflict: Dict, sheet_set: set) -> bool:
    """Return True if conflict references any sheet in the given set (sheets[] or inline text)."""
    sheets = conflict.get("sheets", []) or []
    if isinstance(sheets, list):
        for s in sheets:
            if isinstance(s, str) and s in sheet_set:
                return True
    # Check inline text refs in title/description/location
    blob = " ".join(
        str(conflict.get(k, "")) for k in ("title", "description", "location", "recommended_action")
    )
    for s in sheet_set:
        # Word-boundary match to avoid false hits (e.g. "S-1" in "S-10")
        pattern = r"\b" + re.escape(s) + r"\b"
        if re.search(pattern, blob):
            return True
    return False


def _is_missing_from_index(conflict: Dict) -> bool:
    """Filter 1A helper: does this conflict claim a sheet is missing from an index?"""
    blob = " ".join(
        str(conflict.get(k, "")) for k in ("title", "description", "type")
    ).lower()
    return "missing from" in blob and "index" in blob


def _is_spec_markup_missing(conflict: Dict) -> bool:
    """Filter 1C helper: spec-referenced conflict with no spec-section citation."""
    blob = (
        str(conflict.get("title", "")) + " " + str(conflict.get("description", ""))
    )
    is_markup_pattern = bool(re.search(r"Builder Markup: RELOCATE|Roof Drain Without Downspout", blob, re.IGNORECASE))
    if not is_markup_pattern:
        return False
    # Has an actual CSI spec section (e.g., "07 26 00" or "071326")?
    has_spec_section = bool(re.search(r"\b\d{6}\b|\b\d{2}\s\d{2}\s\d{2}\b", str(conflict.get("recommended_action", ""))))
    return not has_spec_section


def _is_index_inversion(conflict: Dict) -> bool:
    """Filter 1D: flags index sheet (A-001/A-002) as missing from index."""
    if not _is_missing_from_index(conflict):
        return False
    return _references_any_sheet(conflict, INDEX_SHEETS)


def _dedup_n471_pattern(conflict: Dict) -> Dict:
    """Filter 3: truncate fields with >10 repeated sheet refs.

    N471 rendered ID-3.10A, ID-3.11A, T211A, T221B, T251, ID-3.12A each
    40-50 times. This caps any field (especially sheets[] and description
    sheet lists) at 10 unique entries.
    """
    c = dict(conflict)
    # Dedup the sheets array
    if isinstance(c.get("sheets"), list):
        seen = set()
        unique = [s for s in c["sheets"] if not (s in seen or seen.add(s))]
        if len(c["sheets"]) > 10 and len(c["sheets"]) > len(unique):
            c["sheets"] = unique[:10]
            if len(unique) > 10:
                c["sheets"].append(f"(and {len(unique) - 10} more)")
    # Dedup inline sheet mentions in description (look for "A1, A1, A1, ..." patterns)
    desc = c.get("description", "")
    if desc:
        # Pattern: a sheet ref repeated >3 times with commas/spaces between
        c["description"] = re.sub(
            r"((?:[A-Z]{1,4}-?\d[\w\.]*[,\s]+){10,})",
            lambda m: ", ".join(sorted(set(re.findall(r"[A-Z]{1,4}-?\d[\w\.]*", m.group(0))))[:10]) + " …",
            desc,
        )
    return c


def apply_corrections(conflict: Dict) -> Dict:
    """Apply NE text corrections for C376/C377."""
    c = dict(conflict)
    for field in ("title", "description", "recommended_action"):
        if field in c and isinstance(c[field], str):
            for pattern, replacement in AMENDMENT_CORRECTION_REPLACEMENTS:
                c[field] = re.sub(pattern, replacement, c[field])
    return c


def filter_and_annotate(conflicts: List[Dict]) -> Tuple[List[Dict], Dict]:
    """Apply all GC filters + annotations.

    Returns (kept_conflicts, report_dict). report_dict logs what was dropped
    and why, for the build verification log.
    """
    kept = []
    report = {
        "input_count": len(conflicts),
        "dropped_index_conflation": [],
        "dropped_phantom_sheets": [],
        "dropped_phantom_by_id": [],
        "dropped_spec_markup_missing": [],
        "dropped_index_inversion": [],
        "dropped_disputed": [],
        "corrected_amendment": [],
        "n471_deduped": [],
    }

    for c in conflicts:
        cid = c.get("id", "")

        # Filter 2: substantive disputes -> drop
        if cid in DISPUTED_CONFLICT_IDS:
            report["dropped_disputed"].append(cid)
            continue

        # Filter 1B: phantom sheets by conflict ID
        if cid in PHANTOM_CONFLICT_IDS:
            report["dropped_phantom_by_id"].append(cid)
            continue

        # Filter 1B: phantom sheets by sheet reference
        if _references_any_sheet(c, PHANTOM_SHEETS):
            report["dropped_phantom_sheets"].append(cid)
            continue

        # Filter 1D: A-001/A-002 index inversion
        if _is_index_inversion(c):
            report["dropped_index_inversion"].append(cid)
            continue

        # Filter 1A: civil/arch index conflation
        if _is_missing_from_index(c) and _references_any_sheet(c, INDEX_CONFLATION_SHEETS):
            report["dropped_index_conflation"].append(cid)
            continue

        # Filter 1C: spec-markup-missing
        if _is_spec_markup_missing(c):
            report["dropped_spec_markup_missing"].append(cid)
            continue

        # Filter 2b: amendment corrections (C376/C377)
        if cid in AMENDMENT_CORRECTION_IDS:
            c = apply_corrections(c)
            report["corrected_amendment"].append(cid)

        # Filter 3: N471-style dedup
        original_sheet_count = len(c.get("sheets", []) or [])
        c = _dedup_n471_pattern(c)
        if original_sheet_count > 10 and len(c.get("sheets", []) or []) < original_sheet_count:
            report["n471_deduped"].append(cid)

        kept.append(c)

    report["output_count"] = len(kept)
    report["total_dropped"] = (
        len(report["dropped_index_conflation"])
        + len(report["dropped_phantom_sheets"])
        + len(report["dropped_phantom_by_id"])
        + len(report["dropped_spec_markup_missing"])
        + len(report["dropped_index_inversion"])
        + len(report["dropped_disputed"])
    )
    return kept, report
