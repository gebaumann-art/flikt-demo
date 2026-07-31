"""Apply CURRENT production FP gates + dedup to demo source data.

Why this exists
---------------
The demo pages were built 2026-05-15 from S173/S180-era `results.json` files.
Between then and 2026-07-31 the pipeline shipped a large amount of precision
work (severity gates, garbled-artifact suppression, spec/plan value-mismatch
gating, doc-gap filtering). Re-running the demo fixtures costs API money, so
this module instead replays the *current* deterministic gates over the cached
source conflicts. That is a $0 way to keep the public demo consistent with what
the product would actually emit today.

Scope / honesty caveat
----------------------
This only replays the gates in `fp_filters.py` that operate on the conflict
list alone. It does NOT reproduce:
  - gates needing `sheet_page_map` / `classified` / `all_schedules`
  - red-pen adjudication, citation-grounding repair, the S335 coherence lint
  - any change in the detection/vision layer
So the cleaned output is a conservative *upper* bound on what the current
pipeline would emit. It never invents or upgrades a finding.

Used by build_demo.py.
"""
from __future__ import annotations

import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Tuple

PIPELINE_MAIN = Path.home() / "FLIKT" / "Coding" / "pipeline-main"
if str(PIPELINE_MAIN) not in sys.path:
    sys.path.insert(0, str(PIPELINE_MAIN))

import fp_filters as F  # noqa: E402

# Gates whose only required arg is the conflict list. Order matters only in
# that suppression runs before severity re-binning.
SUPPRESSION_GATES = [
    "filter_doc_gap_fps",
    "drop_doc_gap_speculation_merged",
    "filter_submittal_cross_disc_conflicts",
    "filter_empty_sheet_conflicts",
    "gate_index_audit_out_of_scope_fps",
    "filter_fp_deferred_design_fps",
    "gate_fp_absent_when_present",
    "gate_impossible_height_fps",
    "gate_ul_listing_xref_fps",
    "gate_general_to_mep_xref_fps",
    "gate_building_subset_xref_fps",
    "gate_garbled_artifact_fps",
    "gate_spec_plan_value_mismatch_fps",
    "gate_asapplicable_boilerplate_fps",
    "filter_self_paired_coordination_fps",
    "gate_dcm_range_satisfied_fps",
]

SEVERITY_GATES = [
    "gate_critical_severity_fps",
    "gate_routine_coordination_severity",
    "gate_verify_speculation_severity",
]

SEV_RANK = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def _call(fn, conflicts: List[Dict]) -> List[Dict]:
    """Gates return either a list or a (kept, dropped) tuple."""
    out = fn(deepcopy(conflicts))
    return out[0] if isinstance(out, tuple) else out


def _dedup_key(c: Dict) -> str:
    """Twin detection: normalized leading description text.

    The S180 sources contain genuine dedup misses — the same finding emitted
    twice under different ids and *different severities* (e.g. Salon Lofts
    C001/C007, Carlyle C003/C022). Both render on the public demo today.
    """
    d = (c.get("description") or c.get("title") or "").lower()
    d = re.sub(r"[^a-z0-9 ]+", " ", d)
    d = re.sub(r"\s+", " ", d).strip()
    return d[:120]


def _richness(c: Dict) -> tuple:
    """Prefer the twin carrying more usable data for the card UI."""
    has_cost = 1 if (c.get("cost_high") or 0) else 0
    return (has_cost, len(c.get("sheets") or []), len(c.get("description") or ""))


def collapse_duplicates(conflicts: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Collapse twin findings, keeping the richer row at the LOWER severity.

    Taking the lower severity is deliberate: a demo must never inflate. If the
    pipeline emitted the same finding as both Critical and Medium, the honest
    presentation is the conservative one.
    """
    groups: Dict[str, List[Dict]] = {}
    order: List[str] = []
    for c in conflicts:
        k = _dedup_key(c)
        if k not in groups:
            groups[k] = []
            order.append(k)
        groups[k].append(c)

    kept, dropped = [], []
    for k in order:
        twins = groups[k]
        if len(twins) == 1:
            kept.append(twins[0])
            continue
        richest = max(twins, key=_richness)
        lowest = max(twins, key=lambda c: SEV_RANK.get(str(c.get("severity")).title(), 9))
        winner = deepcopy(richest)
        winner["severity"] = str(lowest.get("severity")).title()
        kept.append(winner)
        dropped.extend([t for t in twins if t is not richest])
    return kept, dropped


def apply_current_gates(conflicts: List[Dict], label: str = "") -> Tuple[List[Dict], Dict]:
    """Replay current suppression + severity gates, then collapse twins.

    Returns (cleaned_conflicts, report_dict).
    """
    start_n = len(conflicts)
    start_sev = _sev_counts(conflicts)

    surviving = deepcopy(conflicts)
    suppressed_by: Dict[str, int] = {}
    for name in SUPPRESSION_GATES:
        fn = getattr(F, name, None)
        if fn is None:
            continue
        before = len(surviving)
        try:
            surviving = _call(fn, surviving)
        except Exception as e:  # a gate needing absent context must not kill the build
            print(f"    [current_gates] skip {name}: {type(e).__name__}: {e}")
            continue
        removed = before - len(surviving)
        if removed:
            suppressed_by[name] = removed

    pre_sev = {id(c): str(c.get("severity")).title() for c in surviving}
    for name in SEVERITY_GATES:
        fn = getattr(F, name, None)
        if fn is None:
            continue
        try:
            surviving = _call(fn, surviving)
        except Exception as e:
            print(f"    [current_gates] skip {name}: {type(e).__name__}: {e}")

    surviving, twins = collapse_duplicates(surviving)

    report = {
        "label": label,
        "start": start_n,
        "end": len(surviving),
        "suppressed": start_n - len(surviving) - len(twins),
        "twins_collapsed": len(twins),
        "suppressed_by": suppressed_by,
        "severity_before": start_sev,
        "severity_after": _sev_counts(surviving),
    }
    return surviving, report


def _sev_counts(conflicts: List[Dict]) -> Dict[str, int]:
    out = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for c in conflicts:
        s = str(c.get("severity", "Low")).title()
        out[s] = out.get(s, 0) + 1
    return out


def print_report(rep: Dict) -> None:
    print(f"  [gates] {rep['label']}: {rep['start']} -> {rep['end']} "
          f"({rep['suppressed']} suppressed, {rep['twins_collapsed']} twins collapsed)")
    print(f"          severity {rep['severity_before']} -> {rep['severity_after']}")
    for g, n in rep["suppressed_by"].items():
        print(f"            - {g}: {n}")
