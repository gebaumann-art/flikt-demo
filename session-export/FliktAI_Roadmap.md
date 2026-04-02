# Flikt.AI — Product Roadmap & To-Do List

**Last Updated:** March 2, 2026
**Reference:** FliktAI_30Day_Execution_Plan_v3.xlsx (current execution plan)

---

## Blind Test Results — 980 Harbor Islands (Mar 2, 2026)

**GC provided 6 review comments. Flikt.AI found 5 conflicts. Direct match: 0/6.**

The GC's comments were all Civil ↔ Structural material/scope mismatches (asphalt vs concrete, SF discrepancies, missing volleyball court scope, fencing clarity). Flikt.AI found valid Electrical ↔ Landscape and Structural ↔ Electrical coordination issues the GC didn't flag — but missed all 6 GC items because they require reading specific text callouts on sheets.

**Critical improvements needed (from blind test):**
- [ ] **OCR pre-processing** — Extract text callouts from sheets before AI analysis so material specs, quantities, and scope notes are machine-readable
- [ ] **Material specification cross-referencing** — Compare material callouts (asphalt/concrete/pavers/sand) across discipline sheets for the same area
- [ ] **Quantity/SF comparison** — Cross-check area calculations and quantities between disciplines (e.g., 9,044 SF vs 5,923 SF)
- [ ] **Scope completeness checks** — Verify that work shown on one discipline's sheet is captured on related discipline sheets (e.g., volleyball court on Arch but missing from Civil)
- [ ] **Targeted Civil ↔ Structural prompting** — This is a high-value discipline pair that the current prompt underweights
- [ ] **Higher resolution for text-heavy sheets** — Current 1600px JPEG compression loses small annotation text

Full analysis: `FliktAI_Blind_Test_980_Harbor_Islands.pdf`

---

## Production Readiness — Scoring & Measurements (Model Training workstream)

These items are **demo placeholders today** and must be replaced with defensible, data-backed measurements before any client-facing delivery.

- [ ] **Replace heuristic severity scoring with data-backed model** — Current scoring uses keyword matching as a fallback when the AI returns flat scores. Production version needs calibration against historical project data (RFIs, change orders, actual rework costs) to produce defensible severity ratings. *Ties to MT tasks #1–3, #10–11, #17–18, #25–26.*
- [ ] **Tie cost estimates to real construction cost data** — Integrate RSMeans or similar cost database. Factor in local labor rates, material costs, and project-specific conditions instead of score-based multipliers.
- [ ] **Validate schedule impact against CPM logic** — Current schedule days are derived from a score multiplier. Production version should reference typical activity durations by trade and conflict type, ideally informed by real project schedules.
- [ ] **Benchmark AI detection accuracy** — Run the pipeline against projects with known BIM clash detection results to measure precision/recall and tune confidence thresholds. *Ties to MT tasks #1, #11, #18, #25.*
- [ ] **Add confidence calibration** — Map AI confidence scores to actual detection accuracy so users know when manual verification is warranted.

## 30-Day Execution Plan Status (from v3 — as of Mar 2)

### Week 1: Mar 1–7 — Foundation & Setup
| # | Stream | Task | Status |
|---|--------|------|--------|
| 1 | MT | Baseline accuracy eval | Done |
| 2 | MT | Identify top 5 weak conflict categories | Done |
| 3 | MT | Curate 20+ annotated plan set examples | Done |
| 4 | SE | Audit intake-to-delivery flow end-to-end | Done |
| 5 | SE | Finalize MSA, ToS, SOW templates | Done |
| 6 | SE | Set up Stripe account + payment links | Needs Greg |
| 7 | OE | Set up LinkedIn Sales Navigator | Needs Greg |
| 8 | OE | Build 50-contact target list | Done (60 prospects) |
| 9 | OE | Record 2 Loom demo videos | Done (script drafted) |

### Week 2: Mar 8–14 — Build Momentum
| # | Stream | Task | Status |
|---|--------|------|--------|
| 10 | MT | Fine-tuning iteration #1 on weak categories | Not Started |
| 11 | MT | Re-evaluate accuracy, measure delta | Not Started |
| 12 | SE | Automated quote generation from intake form | Not Started |
| 13 | SE | Full client onboarding end-to-end test | Not Started |
| 14 | OE | Send first 20 warm LinkedIn DMs | Done (templates ready) |
| 15 | OE | Publish first 3 LinkedIn posts | Done (6 posts drafted) |
| 16 | OE | Pitch Construction Dive article | Done (pitch drafted) |

### Week 3: Mar 15–21 — Accelerate
| # | Stream | Task | Status |
|---|--------|------|--------|
| 17 | MT | Fine-tuning iteration #2 | Not Started |
| 18 | MT | Out-of-sample validation on 2 new plan sets | Not Started |
| 19 | SE | Bug fixes from end-to-end test | Not Started |
| 20 | SE | Client onboarding email sequence | Done (4-email sequence) |
| 21 | OE | Send next 20 LinkedIn DMs | Done (templates ready) |
| 22 | OE | Publish 3 more LinkedIn + 2 Twitter/X posts | Not Started |
| 23 | OE | DM 3 ConTech influencers | Done (DMs drafted) |
| 24 | OE | Reach out to 3 Owner's Rep firms | Not Started |

### Week 4: Mar 22–31 — Close & Measure
| # | Stream | Task | Status |
|---|--------|------|--------|
| 25 | MT | Compile training results report | Not Started |
| 26 | MT | Document model limitations + next cycle plan | Not Started |
| 27 | SE | Onboard first paying client (or internal sim) | Not Started |
| 28 | SE | Document ecosystem processes in runbook | Not Started |
| 29 | OE | Follow up all DM conversations, schedule demos | Not Started |
| 30 | OE | Submit speaking proposal (ULI or NAIOP) | Not Started |
| 31 | OE | Month-end metrics scorecard | Not Started |
| 32 | ALL | 30-day retrospective + April priorities | Not Started |

### New Tasks Added (Mar 1–2)
| # | Stream | Task | Status |
|---|--------|------|--------|
| 33 | SE | Set up Stripe: EIN, bank, business verification | Not Started |
| 34 | SE | Connect payout method (bank + CC for fees) | Not Started |
| 35 | SE | Create Stripe products/prices ($5K–$200K tiers) | Not Started |
| 36 | SE | End-to-end payment test in Stripe test mode | Not Started |
| 37 | LAUNCH | Website design audit (UX, accessibility, conversion) | Not Started |
| 38 | LAUNCH | Create demo video (screen recording, 2–3 min) | Not Started |
| 39 | LEGAL | Draft privacy policy + cookie policy for flikt.ai | Not Started |
| 40 | OE | Set up CRM / pipeline tracker | Not Started |
| 41 | OE | Build anonymized case study from pilot project | Not Started |
| 42 | LAUNCH | Build pricing page for flikt.ai | Not Started |
| 43 | SE | Call GoDaddy: consolidate email + hosting | Not Started |
| 44 | SE | Confirm Domain Privacy restored | Not Started |
| 45 | SE | Create info@flikt.ai mailbox/alias | Not Started |
| 46 | SE | Test info@flikt.ai delivery | Not Started |
| 47 | LAUNCH | Verify WordPress hosting post-consolidation | Not Started |
| 48 | LAUNCH | Deploy new website pages (privacy, pricing, case study) | Not Started |
| 49 | LAUNCH | Add consistent nav bar across all pages | Not Started |

## Demo & Backend Improvements

- [ ] Push updated demo portal to GitHub Pages (index.html + pitch deck PDF)
- [x] Test smooth progress bar animation after server restart
- [x] Fix 413 request_too_large error for large plan sets (image compression + batch splitting)
- [x] Fix port config issue (default 8000 vs 9000)
- [x] Complete blind accuracy test against GC review (980 Harbor Islands)
- [ ] Prepare third-party plan set for end-to-end demo within one week
- [ ] Support more than 2 disciplines per analysis (MEP, Fire Protection, Civil, etc.)
- [ ] Add sheet-level reference tracking (populate empty "Sheets:" field in reports)
- [ ] Implement streaming AI response for real-time progress during detection
- [ ] Add job persistence (currently in-memory — lost on server restart)
- [ ] Docker containerization for deployment

## Report Enhancements

- [ ] Add plan overlay visuals showing conflict locations on actual drawings
- [ ] Include discipline-pair matrix showing which pairs have the most conflicts
- [ ] Add executive summary charts (severity pie chart, cost by discipline bar chart)
