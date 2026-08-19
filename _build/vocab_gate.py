"""Forbidden internal vocabulary gate for the public demo.

Deliberately standalone: `re` and nothing else. It lives apart from
build_demo.py because build_demo imports current_gates -> fp_filters, which
lives in the pipeline checkout and is NOT present on a CI runner. Importing
the gate through build_demo made the CI job die with ModuleNotFoundError
before it scanned a single byte — a gate that cannot run is not a gate.
(Caught 2026-08-19: the local rehearsal passed only because the pipeline
code happens to sit on the author's machine.)

Scanned against the FINAL RENDERED HTML, not the data blob. The leak this
was written for — "Conflicts by discipline pair", a per-finding `consensus`
object, the named severity axes, `spec_processor_api` — lived in hardcoded
template strings, CSS/JS comments and embedded JSON, none of which the
identity-focused leak_scan() ever looked at.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# Sourced from the customer-secrecy doctrine's forbidden list.
FORBIDDEN_VOCAB = [
    r"discipline[ _-]pairs?",
    r"\d+[ -]point model",
    r"fan-?out",
    r"multi-?pass",
    r"\bPass [0-4]\b",
    r"\bconsensus\b",
    r"MATCH_THRESHOLD",
    r"VISION_CONFIDENCE\w*",
    r"FAIL_FAST",
    r"\bDEGRADED\b",
    r"quality[ _-]gate",
    r"submission_id",
    r"pipeline_runner",
    r"process_plans",
    r"\bFargate\b",
    r"\bCelery\b",
    r"\balembic\b",
    r"\bboto3\b",
    r"app/services/",
    # Internal module names. These reach public HTML through the conflict
    # `source` field (e.g. "spec_processor_api"), which is why they are here
    # as well as in INTERNAL_CONFLICT_FIELDS — belt and braces, since the
    # field strip is a denylist and a new field could carry them again.
    r"spec_processor\w*",
    r"text_extractor\w*",
    r"vision_(?:pass|anemic)\w*",
    r"consensus_runner",
    r"coordination_detector",
    r"clearance_validator",
    r"ada_dimension_checker",
    r"rcp_electrical_postpass",
    r"geotech_report_parser",
    r"legend_consistency",
    r"panel_processor",
    r"index_audit",
    r"schedule_(?:parser|template_builder)",
    # Internal repo/source paths. Added after a CSS comment naming the
    # portal's tailwind config and lib path shipped to page source.
    r"customer-portal[\w-]*/",
    r"tailwind\.config",
    r"src/lib/",
    r"flikt-demo/_build",
]

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


def vocab_scan(html: str) -> List[Tuple[str, List[str]]]:
    """Return (pattern, sample_hits) for any forbidden internal vocabulary.

    Fails the build rather than warning. A public marketing surface that leaks
    architecture is not a cosmetic defect, and a warning in a 60-line build log
    is exactly how the last one survived three refreshes unnoticed.
    """
    hits = []
    for pattern in FORBIDDEN_VOCAB:
        matches = re.findall(pattern, html, flags=re.IGNORECASE)
        if matches:
            hits.append((pattern, sorted(set(matches))[:5]))
    return hits


def selftest() -> int:
    """Prove the gate FIRES, not just that a clean build passes.

    A gate is only worth its line count if you have watched it fail. Each case
    below is a string that actually shipped to demo.flikt.ai before 2026-08-19.
    """
    must_catch = [
        ("results header", "<span>Conflicts by discipline pair</span>"),
        ("analysis log", "Comparing elements across 21 discipline pairs"),
        ("css comment", "/* Discipline pair strip (collapsed) */"),
        ("stage label", "Scoring severity (50-point model)..."),
        ("embedded json", '"consensus": {"runs_detected": 5, "total_runs": 5}'),
        ("module name", '"source": "spec_processor_api"'),
        ("repo path", "/* sourced from customer-portal-main/tailwind.config.ts */"),
    ]
    must_pass = [
        ("trade badge", '<span class="disc-pair-tag">A &harr; S</span>'),
        ("finding title", "Plumbing Pipe Penetrations Through Fire-Rated Assembly"),
        ("neutral log", "Comparing elements across every trade combination in the set"),
        ("cost line", "Total cost exposure: $489,717 - $1,178,916"),
    ]

    failures = 0
    for label, sample in must_catch:
        if not vocab_scan(sample):
            print(f"  FAIL (missed) {label}: {sample!r}")
            failures += 1
        else:
            print(f"  ok  caught   {label}")
    for label, sample in must_pass:
        hits = vocab_scan(sample)
        if hits:
            print(f"  FAIL (over-caught) {label}: {hits}")
            failures += 1
        else:
            print(f"  ok  allowed  {label}")

    print()
    if failures:
        print(f"SELFTEST FAILED ({failures})")
        return 1
    print("SELFTEST PASSED — gate catches every known leak, allows legit copy")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(selftest())
