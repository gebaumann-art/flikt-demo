"""HTML template for per-project demo pages.

Portal report-view styled (S181 refresh). Uses {} placeholders filled by
build_demo.py. CSS palette matches the FliktAI customer portal report view:
light body, dark navy navbar, severity-tinted conflict cards, two-column
findings + sheet-viewer layout.

Placeholders (Python str.format):
  {TITLE}, {DATA_JSON}, {STAGES_JSON}, {RENDER_CAP}, {PDF_FILENAME}, {REPORT_DATE}

Literal CSS / JS braces are escaped as {{ }}.
"""

PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} &mdash; Flikt.AI Plan Analysis</title>
<meta property="og:title" content="{TITLE} &mdash; Flikt.AI Plan Analysis">
<meta property="og:description" content="AI-powered plan coordination demo. Real conflict data, anonymized project details.">
<meta property="og:type" content="website">
<meta property="og:image" content="og_final_demo.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script>
(function(){{try{{var s=localStorage.getItem('flikt-theme');
if(!s){{s=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}}
document.documentElement.setAttribute('data-theme',s)}}catch(e){{}}}})();
</script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --navy:#0a1929;--navy-2:#13243a;--amber:#E8A020;--amber-light:#F5C96B;
  --critical:#DC2626;--critical-tint:#FEF2F2;--critical-border:#FECACA;
  --high:#EA580C;--high-tint:#FFF7ED;--high-border:#FED7AA;
  --medium:#D97706;--medium-tint:#FFFBEB;--medium-border:#FDE68A;
  --low:#16A34A;--low-tint:#F0FDF4;--low-border:#BBF7D0;
  --bg:#F5F7FA;--card:#FFFFFF;--text:#0F172A;--text-muted:#64748B;--text-soft:#94A3B8;
  --border:#E2E8F0;--border-strong:#CBD5E1;
  --canvas-stripe-a:#FAFCFF;--canvas-stripe-b:#F3F6FB
}}
:root[data-theme="dark"]{{
  --bg:#0F1723;--card:#1A2540;
  --text:#E8ECF1;--text-muted:#A0AEC0;--text-soft:#7C8B9F;
  --border:#2A3A55;--border-strong:#3A4A65;
  --critical-tint:#3F1313;--critical-border:#5D2020;
  --high-tint:#3D1F0A;--high-border:#5C2F10;
  --medium-tint:#3D2F0A;--medium-border:#5C4710;
  --low-tint:#0D2C19;--low-border:#1A4D2C;
  --canvas-stripe-a:#13243A;--canvas-stripe-b:#1A2540
}}
html,body{{height:100%}}
body{{
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.5;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
  overflow-x:hidden
}}
a{{color:var(--amber);text-decoration:none;transition:color .2s}}
a:hover{{color:#B97D0F}}

/* ============ Header / Navbar ============ */
.header{{
  background:var(--navy);border-bottom:1px solid rgba(255,255,255,0.06);
  padding:14px 32px;display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:100
}}
.header-left{{display:flex;align-items:center;gap:20px}}
.back-link{{
  color:rgba(255,255,255,0.65);font-size:13px;font-weight:600;
  display:inline-flex;align-items:center;gap:6px;transition:color .2s
}}
.back-link:hover{{color:var(--amber)}}
.logo{{display:flex;align-items:center;gap:10px;font-size:20px;font-weight:700;letter-spacing:.1px;color:#fff}}
.logo-icon{{height:30px;width:30px;display:block;flex-shrink:0}}
.logo-wm{{color:#fff;white-space:nowrap}}
.logo-accent{{color:var(--amber)}}
.nav{{display:flex;gap:4px}}
.nav button{{
  background:transparent;border:1px solid transparent;
  color:rgba(255,255,255,0.65);padding:7px 14px;border-radius:6px;cursor:pointer;
  font-family:inherit;font-size:13px;font-weight:600;transition:all .2s
}}
.nav button:hover{{color:#fff;background:rgba(255,255,255,0.06)}}
.nav button.active{{color:var(--navy);background:var(--amber)}}
.nav button.locked{{opacity:0.35;cursor:not-allowed;pointer-events:none}}
.header-right{{display:flex;align-items:center;gap:10px}}
.theme-toggle{{
  background:transparent;border:1px solid rgba(255,255,255,0.18);border-radius:8px;
  width:32px;height:32px;display:flex;align-items:center;justify-content:center;
  cursor:pointer;color:#fff;transition:background .15s ease,border-color .15s ease;padding:0
}}
.theme-toggle:hover{{background:rgba(255,255,255,0.08);border-color:rgba(255,255,255,0.35)}}
.theme-toggle svg{{width:15px;height:15px;display:block}}
.theme-toggle .sun{{display:none}}
.theme-toggle .moon{{display:block}}
:root[data-theme="dark"] .theme-toggle .sun{{display:block}}
:root[data-theme="dark"] .theme-toggle .moon{{display:none}}

/* ============ View container ============ */
.view{{display:none;padding:24px 32px 48px;max-width:1280px;margin:0 auto}}
.view.active{{display:block}}

/* ============ Dashboard view ============ */
.dash-hero{{text-align:center;margin:32px 0 24px;padding:0 8px}}
.dash-hero h1{{font-size:30px;font-weight:800;letter-spacing:-0.02em;margin-bottom:8px}}
.dash-hero p{{color:var(--text-muted);font-size:15px;max-width:600px;margin:0 auto}}
.project-card{{
  background:var(--card);border:1px solid var(--border);border-radius:14px;
  padding:28px 32px;margin:24px 0;box-shadow:0 1px 2px rgba(15,23,42,0.04)
}}
.project-card h2{{font-size:22px;font-weight:700;letter-spacing:-0.01em;margin-bottom:18px;color:var(--text)}}
.meta-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}
.meta-item{{padding:14px;background:var(--bg);border-radius:10px;border:1px solid var(--border)}}
.meta-item .label{{font-size:10px;text-transform:uppercase;color:var(--text-muted);letter-spacing:.6px;font-weight:600}}
.meta-item .value{{font-size:17px;font-weight:700;margin-top:4px;color:var(--text)}}
.disciplines-list{{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}}
.disc-tag{{
  background:var(--bg);padding:4px 12px;border-radius:14px;font-size:12px;
  border:1px solid var(--border);color:var(--text);font-weight:500
}}
.disc-tag .count{{color:var(--amber);font-weight:700;margin-left:4px}}
.btn{{
  display:inline-flex;align-items:center;gap:8px;padding:12px 22px;border-radius:8px;
  font-family:inherit;font-size:14px;font-weight:700;cursor:pointer;border:1px solid transparent;
  transition:all .2s
}}
.btn-primary{{background:var(--amber);color:var(--navy)}}
.btn-primary:hover{{background:#D38F12;transform:translateY(-1px);box-shadow:0 6px 16px rgba(232,160,32,0.3)}}
.btn-outline{{background:transparent;color:var(--text);border:1px solid var(--border-strong)}}
.btn-outline:hover{{background:var(--bg);border-color:var(--text-muted)}}
.btn-ghost{{background:transparent;color:var(--text-muted);border:1px solid var(--border)}}
.btn-ghost:hover{{background:var(--bg);color:var(--text)}}
.center-btn{{text-align:center;margin:28px 0}}

/* ============ Progress view ============ */
.progress-container{{max-width:680px;margin:60px auto;text-align:center}}
.progress-container h2{{font-size:22px;font-weight:700;margin-bottom:24px;letter-spacing:-0.01em}}
.progress-bar-wrap{{
  background:var(--border);border-radius:12px;height:16px;overflow:hidden;margin:18px 0
}}
.progress-bar{{
  background:linear-gradient(90deg,var(--amber),var(--amber-light));
  height:100%;border-radius:12px;transition:width .3s ease;width:0%
}}
.progress-pct{{font-size:44px;font-weight:800;color:var(--amber);margin:14px 0;letter-spacing:-0.02em}}
.progress-stage{{color:var(--text-muted);font-size:14px;margin:6px 0}}
.activity-log{{
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:16px;margin-top:28px;text-align:left;max-height:240px;overflow-y:auto;
  font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:11.5px;line-height:1.55
}}
.log-line{{padding:2px 0;color:var(--text-muted)}}
.log-line .time{{color:var(--amber);margin-right:8px;font-weight:600}}
.log-line.highlight{{color:var(--text);font-weight:500}}

/* ============ Results view (portal report-view) ============ */
.report-hero{{
  background:var(--card);border:1px solid var(--border);border-radius:14px;
  padding:24px 28px;margin-bottom:18px;box-shadow:0 1px 2px rgba(15,23,42,0.04)
}}
.report-hero-top{{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;flex-wrap:wrap}}
.report-hero-title{{flex:1;min-width:240px}}
.report-hero-title h1{{font-size:26px;font-weight:800;letter-spacing:-0.02em;color:var(--text);line-height:1.25}}
.report-hero-title .addr{{color:var(--text-muted);font-size:14px;margin-top:6px}}
.action-toolbar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center}}
.action-btn{{
  display:inline-flex;align-items:center;gap:6px;
  background:var(--card);color:var(--text);border:1px solid var(--border);
  padding:7px 12px;border-radius:8px;font-family:inherit;font-size:12.5px;font-weight:600;
  cursor:pointer;transition:all .15s
}}
.action-btn:hover{{background:var(--bg);border-color:var(--border-strong)}}
.action-btn.primary{{background:var(--amber);color:var(--navy);border-color:var(--amber)}}
.action-btn.primary:hover{{background:#D38F12;border-color:#D38F12}}
.action-btn svg{{width:14px;height:14px}}

/* Stats summary row (above two-column) */
.summary-row{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:10px}}
.stat-box{{
  padding:14px 12px;border-radius:10px;text-align:center;
  background:var(--card);border:1px solid var(--border)
}}
.stat-box .num{{font-size:24px;font-weight:800;letter-spacing:-0.01em}}
.stat-box .lbl{{font-size:10px;text-transform:uppercase;letter-spacing:.5px;margin-top:3px;color:var(--text-muted);font-weight:600}}
.stat-total .num{{color:var(--text)}}
.stat-critical{{background:var(--critical-tint);border-color:var(--critical-border)}}
.stat-critical .num{{color:var(--critical)}}
.stat-high{{background:var(--high-tint);border-color:var(--high-border)}}
.stat-high .num{{color:var(--high)}}
.stat-medium{{background:var(--medium-tint);border-color:var(--medium-border)}}
.stat-medium .num{{color:var(--medium)}}
.stat-low{{background:var(--low-tint);border-color:var(--low-border)}}
.stat-low .num{{color:var(--low)}}
.summary-row2{{display:grid;grid-template-columns:3fr 2fr;gap:10px;margin-bottom:18px}}
.stat-cost{{
  background:var(--card);border:1px solid var(--border);
  padding:14px 18px;border-radius:10px;text-align:center
}}
.stat-cost .num{{font-size:20px;font-weight:700;color:var(--text);letter-spacing:-0.01em}}
.stat-cost .lbl{{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--text-muted);font-weight:600;margin-bottom:4px}}
.stat-pairs{{
  background:var(--navy);color:#fff;padding:14px 18px;border-radius:10px;text-align:center;
  border:1px solid var(--navy)
}}
.stat-pairs .num{{font-size:20px;font-weight:700;color:var(--amber)}}
.stat-pairs .lbl{{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:rgba(255,255,255,0.7);font-weight:600;margin-bottom:4px}}

/* Discipline pair strip (collapsed) */
.disc-pair-strip{{
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:12px 16px;margin-bottom:14px;display:flex;flex-wrap:wrap;align-items:center;gap:10px
}}
.disc-pair-strip .strip-label{{
  font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--text-muted);
  font-weight:700;margin-right:4px
}}
.disc-pair-chip{{
  display:inline-flex;align-items:center;gap:5px;
  background:var(--bg);border:1px solid var(--border);
  padding:4px 10px;border-radius:14px;font-size:11.5px;font-weight:600;color:var(--text)
}}
.disc-pair-chip .pair-count{{color:var(--amber);font-weight:700}}

/* Filters */
.filters{{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap}}
.filter-btn{{
  background:var(--card);border:1px solid var(--border);color:var(--text-muted);
  padding:7px 14px;border-radius:18px;cursor:pointer;
  font-family:inherit;font-size:12px;font-weight:600;transition:all .2s
}}
.filter-btn:hover{{border-color:var(--border-strong);color:var(--text)}}
.filter-btn.active{{background:var(--navy);color:#fff;border-color:var(--navy)}}

/* Two-column body */
.report-body{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;align-items:start}}
.findings-col{{min-width:0}}
.viewer-col{{min-width:0;position:sticky;top:88px}}

/* Conflict cards — portal report-view style */
.conflict-card{{
  background:var(--card);border:1px solid var(--border);border-left-width:4px;
  border-radius:10px;margin-bottom:10px;overflow:hidden;transition:all .15s;cursor:pointer
}}
.conflict-card:hover{{border-color:var(--border-strong);transform:translateY(-1px);box-shadow:0 4px 12px rgba(15,23,42,0.06)}}
.conflict-card.active{{box-shadow:0 0 0 2px var(--amber);border-color:var(--amber)}}
.conflict-card[data-sev="Critical"]{{background:linear-gradient(180deg,var(--critical-tint) 0%,var(--card) 60%);border-left-color:var(--critical)}}
.conflict-card[data-sev="High"]{{background:linear-gradient(180deg,var(--high-tint) 0%,var(--card) 60%);border-left-color:var(--high)}}
.conflict-card[data-sev="Medium"]{{background:linear-gradient(180deg,var(--medium-tint) 0%,var(--card) 60%);border-left-color:var(--medium)}}
.conflict-card[data-sev="Low"]{{background:linear-gradient(180deg,var(--low-tint) 0%,var(--card) 60%);border-left-color:var(--low)}}
.cc-header{{padding:12px 14px;display:flex;align-items:flex-start;gap:10px}}
.cc-left-col{{display:flex;flex-direction:column;gap:6px;flex-shrink:0;min-width:80px}}
.sev-badge{{
  padding:3px 10px;border-radius:6px;font-size:11px;font-weight:800;color:#fff;
  letter-spacing:.3px;text-align:center
}}
.sev-Critical{{background:var(--critical)}}
.sev-High{{background:var(--high)}}
.sev-Medium{{background:var(--medium)}}
.sev-Low{{background:var(--low)}}
.disc-pair-tag{{
  background:var(--navy);color:#fff;padding:2px 8px;border-radius:5px;
  font-size:10.5px;font-weight:700;letter-spacing:.2px;text-align:center
}}
.cc-body-col{{flex:1;min-width:0}}
.cc-row-top{{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:4px}}
.cc-title{{font-size:13.5px;font-weight:700;color:var(--text);line-height:1.35}}
.cc-index{{font-size:11px;color:var(--text-soft);font-weight:600;white-space:nowrap;flex-shrink:0}}
.cc-snippet{{font-size:12.5px;color:var(--text-muted);line-height:1.45;margin-top:2px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.cc-chevron{{color:var(--text-soft);font-size:12px;flex-shrink:0;transition:transform .2s;margin-top:4px}}
.conflict-card.expanded .cc-chevron{{transform:rotate(180deg)}}
.cc-body{{display:none;padding:0 14px 14px 14px;border-top:1px solid rgba(15,23,42,0.05);margin-top:6px;padding-top:12px}}
.conflict-card.expanded .cc-body{{display:block}}
.cc-meta{{
  display:grid;grid-template-columns:1fr 1fr;gap:6px;background:rgba(15,23,42,0.03);
  padding:10px;border-radius:8px;margin-bottom:10px
}}
.cc-meta-item{{font-size:11.5px;color:var(--text)}}
.cc-meta-item .k{{color:var(--text-muted);font-weight:600;margin-right:4px}}
.cc-desc{{font-size:12.5px;color:var(--text);margin-bottom:12px;line-height:1.55}}
.scores-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-bottom:10px}}
.score-dim{{text-align:center}}
.score-dim .dim-label{{font-size:9.5px;font-weight:700;text-transform:uppercase;color:var(--text-muted);margin-bottom:3px;letter-spacing:.3px}}
.score-bar-bg{{height:6px;background:var(--border);border-radius:3px;overflow:hidden}}
.score-bar-fill{{height:100%;border-radius:3px;transition:width .5s ease}}
.score-dim .dim-val{{font-size:10.5px;font-weight:700;margin-top:2px}}
.cc-impact{{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px}}
.impact-box{{
  background:rgba(15,23,42,0.03);padding:9px 12px;border-radius:6px;
  border-left:3px solid var(--amber);font-size:11.5px
}}
.impact-box .ib-label{{font-weight:700;color:var(--text)}}
.cc-action{{
  background:rgba(232,160,32,0.08);border:1px solid rgba(232,160,32,0.25);
  border-radius:8px;padding:10px 14px;font-size:11.5px;line-height:1.55;color:var(--text)
}}
.cc-action strong{{color:#B97D0F}}
.truncated-notice{{
  padding:14px;margin-top:14px;background:rgba(232,160,32,0.08);
  border:1px solid rgba(232,160,32,0.25);border-radius:8px;text-align:center;
  font-size:12.5px;color:var(--text)
}}
.truncated-notice strong{{color:#B97D0F}}
.truncated-notice a{{color:var(--amber);font-weight:700}}

/* Sheet viewer (right pane) */
.sheet-viewer{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:18px;box-shadow:0 1px 2px rgba(15,23,42,0.04);
  display:flex;flex-direction:column;min-height:520px
}}
.viewer-header{{
  display:flex;justify-content:space-between;align-items:center;
  padding-bottom:12px;border-bottom:1px solid var(--border);margin-bottom:14px
}}
.viewer-title{{font-size:13px;font-weight:700;color:var(--text);letter-spacing:-0.01em}}
.viewer-sheet-id{{font-size:11px;color:var(--text-muted);font-family:ui-monospace,monospace}}
.viewer-canvas{{
  flex:1;background:repeating-linear-gradient(45deg,var(--canvas-stripe-a),var(--canvas-stripe-a) 12px,var(--canvas-stripe-b) 12px,var(--canvas-stripe-b) 24px);
  border:1px dashed var(--border-strong);border-radius:8px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:32px;text-align:center;position:relative;overflow:hidden;min-height:380px
}}
.viewer-canvas .viewer-icon{{
  width:60px;height:60px;border-radius:14px;background:var(--navy);
  display:flex;align-items:center;justify-content:center;margin-bottom:18px;
  box-shadow:0 4px 14px rgba(10,25,41,0.18)
}}
.viewer-canvas .viewer-icon svg{{width:32px;height:32px;color:var(--amber)}}
.viewer-canvas h3{{font-size:15px;font-weight:700;color:var(--text);margin-bottom:6px}}
.viewer-canvas p{{font-size:12.5px;color:var(--text-muted);max-width:280px;line-height:1.55}}
.viewer-pin{{
  position:absolute;width:24px;height:24px;border-radius:50%;
  background:var(--critical);border:3px solid #fff;
  box-shadow:0 2px 8px rgba(220,38,38,0.4),0 0 0 4px rgba(220,38,38,0.2);
  display:flex;align-items:center;justify-content:center;color:#fff;font-size:10px;font-weight:800
}}
.viewer-footnote{{
  font-size:11px;color:var(--text-soft);text-align:center;margin-top:12px;
  padding-top:10px;border-top:1px solid var(--border)
}}

/* ============ Report view ============ */
.report-preview{{text-align:center;margin:32px 0}}
.report-preview h2{{font-size:22px;font-weight:700;letter-spacing:-0.01em;margin-bottom:10px}}
.report-preview .subtitle{{color:var(--text-muted);margin-bottom:24px;font-size:14px}}
.report-mockup{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  max-width:480px;margin:0 auto;padding:36px;color:var(--text);
  box-shadow:0 8px 32px rgba(15,23,42,0.08)
}}
.rm-header{{background:var(--navy);color:#fff;padding:24px;border-radius:8px;margin-bottom:18px}}
.rm-header h3{{font-size:20px;letter-spacing:.5px;font-weight:800}}
.rm-header h3 .amber{{color:var(--amber)}}
.rm-header p{{opacity:.75;font-size:12px;margin-top:4px}}
.rm-title{{font-size:16px;font-weight:700;color:var(--text);text-align:center;margin:14px 0}}
.rm-bar{{height:3px;background:var(--amber);border-radius:2px;margin:10px 0}}
.rm-meta{{font-size:12px;color:var(--text);margin:6px 0;text-align:left}}
.rm-meta strong{{color:var(--text-muted);font-weight:600}}

/* ============ Mobile ============ */
.mobile-tabs{{
  display:none;position:fixed;bottom:0;left:0;right:0;background:var(--navy);
  border-top:1px solid rgba(255,255,255,0.06);z-index:100;
  padding:6px 0 env(safe-area-inset-bottom,6px)
}}
.mobile-tabs-inner{{display:flex;justify-content:space-around;align-items:center}}
.mobile-tab{{
  display:flex;flex-direction:column;align-items:center;gap:2px;
  background:none;border:none;color:rgba(255,255,255,0.55);
  font-family:inherit;font-size:10px;font-weight:600;
  padding:6px 12px;cursor:pointer;transition:color .2s;
  -webkit-tap-highlight-color:transparent
}}
.mobile-tab svg{{width:20px;height:20px}}
.mobile-tab.active{{color:var(--amber)}}
.mobile-tab.locked{{opacity:0.3;pointer-events:none}}
@media(max-width:960px){{
  .report-body{{grid-template-columns:1fr}}
  .viewer-col{{position:static}}
  .sheet-viewer{{min-height:360px}}
}}
@media(max-width:768px){{
  .header{{flex-direction:column;gap:10px;padding:12px 16px}}
  .header-left{{flex-direction:row;width:100%;justify-content:space-between;gap:12px}}
  .summary-row{{grid-template-columns:repeat(2,1fr)}}
  .summary-row2{{grid-template-columns:1fr}}
  .meta-grid{{grid-template-columns:1fr 1fr}}
  .scores-grid{{grid-template-columns:repeat(3,1fr)}}
  .cc-impact{{grid-template-columns:1fr}}
  .cc-meta{{grid-template-columns:1fr}}
  .nav{{display:none}}
  .view{{padding:16px}}
  .mobile-tabs{{display:block}}
  body{{padding-bottom:72px}}
  .report-hero{{padding:18px}}
  .action-toolbar{{width:100%;justify-content:flex-start}}
  .report-hero-title h1{{font-size:22px}}
}}
@media(max-width:480px){{
  .summary-row{{grid-template-columns:1fr 1fr}}
}}
</style>
</head>
<body>
<div class="header">
  <div class="header-left">
    <a href="index.html" class="back-link">&larr; Projects</a>
    <a href="index.html" class="logo" aria-label="Flikt.AI home">
      <img src="flikt-icon.svg" alt="" class="logo-icon">
      <span class="logo-wm">Flikt<span class="logo-accent">.AI</span></span>
    </a>
  </div>
  <div class="header-right">
    <div class="nav">
      <button class="active" onclick="showView('dashboard')">Dashboard</button>
      <button onclick="showView('progress')">Analysis</button>
      <button onclick="showView('results')">Results</button>
      <button onclick="showView('report')">Report</button>
    </div>
    <button class="theme-toggle" type="button" aria-label="Toggle dark mode" title="Toggle dark mode" onclick="(function(){{var r=document.documentElement;var n=r.getAttribute('data-theme')==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{{localStorage.setItem('flikt-theme',n)}}catch(e){{}}}})()">
      <svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
    </button>
  </div>
</div>

<div id="dashboard" class="view active">
  <div class="dash-hero">
    <h1>AI-Powered Plan Coordination</h1>
    <p>Upload construction plans. Detect coordination conflicts. Save thousands in rework.</p>
  </div>
  <div class="project-card">
    <h2 id="proj-name"></h2>
    <div class="meta-grid">
      <div class="meta-item"><div class="label">Address</div><div class="value" id="proj-addr"></div></div>
      <div class="meta-item"><div class="label">Project Type</div><div class="value" id="proj-type"></div></div>
      <div class="meta-item"><div class="label">Construction Value</div><div class="value" id="proj-value"></div></div>
      <div class="meta-item"><div class="label">Total Sheets</div><div class="value" id="proj-sheets"></div></div>
    </div>
    <div style="margin-top:18px">
      <div style="font-size:10px;text-transform:uppercase;color:var(--text-muted);letter-spacing:.6px;margin-bottom:8px;font-weight:700">Disciplines Detected</div>
      <div class="disciplines-list" id="disc-list"></div>
    </div>
  </div>
  <div class="center-btn">
    <button class="btn btn-primary" onclick="startAnalysis()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
      Run Conflict Analysis
    </button>
  </div>
</div>

<div id="progress" class="view">
  <div class="progress-container">
    <h2>Analyzing Plan Set</h2>
    <div class="progress-pct" id="pct">0%</div>
    <div class="progress-bar-wrap"><div class="progress-bar" id="pbar"></div></div>
    <div class="progress-stage" id="stage">Initializing...</div>
    <div class="activity-log" id="log"></div>
  </div>
</div>

<div id="results" class="view">
  <!-- Report hero: title + address + action toolbar -->
  <div class="report-hero">
    <div class="report-hero-top">
      <div class="report-hero-title">
        <h1 id="rh-title"></h1>
        <div class="addr" id="rh-addr"></div>
      </div>
      <div class="action-toolbar">
        <button class="action-btn" title="View summary stats">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          Stats
        </button>
        <button class="action-btn" title="Classic list view">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
          Classic
        </button>
        <button class="action-btn" onclick="copyLink()" title="Copy shareable link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
          Copy Link
        </button>
      </div>
    </div>
  </div>

  <!-- Summary stats row -->
  <div class="summary-row" id="summary-row"></div>
  <div class="summary-row2" id="summary-row2"></div>

  <!-- Discipline pair strip -->
  <div class="disc-pair-strip" id="disc-pair-strip"></div>

  <!-- Filters -->
  <div class="filters" id="filters"></div>

  <!-- Two-column body: findings list + sheet viewer -->
  <div class="report-body">
    <div class="findings-col">
      <div id="conflict-list"></div>
      <div id="truncated-notice"></div>
    </div>
    <div class="viewer-col">
      <div class="sheet-viewer">
        <div class="viewer-header">
          <div class="viewer-title" id="viewer-title">Sheet Preview</div>
          <div class="viewer-sheet-id" id="viewer-sheet-id">&mdash;</div>
        </div>
        <div class="viewer-canvas" id="viewer-canvas">
          <div class="viewer-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <h3>Sheet preview</h3>
          <p id="viewer-placeholder-text">Select a conflict to see its location. Real sheet renderings available in the customer portal &mdash; request a live walkthrough at <a href="mailto:hello@flikt.ai">hello@flikt.ai</a>.</p>
        </div>
        <div class="viewer-footnote">Sheet images are redacted in this public demo. Full sheet rendering is available in the live customer portal.</div>
      </div>
    </div>
  </div>
</div>

<div id="report" class="view">
  <div class="report-preview">
    <h2>Plan Conflict &amp; Coordination Report</h2>
    <p class="subtitle">Professional PDF report ready for download</p>
    <div class="report-mockup">
      <div class="rm-header">
        <h3>Flikt<span class="amber">.AI</span></h3>
        <p>AI-Powered Plan Coordination</p>
      </div>
      <div class="rm-bar"></div>
      <div class="rm-title">Plan Conflict &amp; Coordination Report</div>
      <div class="rm-bar"></div>
      <div class="rm-meta"><strong>Project:</strong> <span id="rm-proj"></span></div>
      <div class="rm-meta"><strong>Report Date:</strong> {REPORT_DATE}</div>
      <div class="rm-meta"><strong>Conflicts Found:</strong> <span id="rm-count"></span></div>
      <div class="rm-meta"><strong>Cost Exposure:</strong> <span id="rm-cost"></span></div>
    </div>
    <div style="margin-top:28px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <button class="btn btn-primary" onclick="showView('results')">
        Back to Results
      </button>
    </div>
  </div>
</div>

<div class="mobile-tabs">
  <div class="mobile-tabs-inner">
    <button class="mobile-tab active" onclick="showView('dashboard')" data-view="dashboard">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
      Dashboard
    </button>
    <button class="mobile-tab" onclick="showView('progress')" data-view="progress">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      Analysis
    </button>
    <button class="mobile-tab" onclick="showView('results')" data-view="results">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      Results
    </button>
    <button class="mobile-tab" onclick="showView('report')" data-view="report">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
      Report
    </button>
  </div>
</div>

<script>
let DATA = {DATA_JSON};
const STAGES = {STAGES_JSON};
const RENDER_CAP = {RENDER_CAP};

let analysisComplete = false;
init();

function updateNavLocks(){{
  document.querySelectorAll('.nav button').forEach(b=>{{
    const label = b.textContent.toLowerCase();
    if(!analysisComplete && (label.includes('results') || label.includes('report'))){{
      b.classList.add('locked');
    }} else {{
      b.classList.remove('locked');
    }}
  }});
  document.querySelectorAll('.mobile-tab').forEach(b=>{{
    const view = b.dataset.view;
    if(!analysisComplete && (view==='results' || view==='report')){{
      b.classList.add('locked');
    }} else {{
      b.classList.remove('locked');
    }}
  }});
}}

function init(){{
  const p=DATA.project, s=DATA.summary;
  document.getElementById('proj-name').textContent=p.name_long || p.name;
  document.getElementById('proj-addr').textContent=p.address;
  document.getElementById('proj-type').textContent=p.type;
  document.getElementById('proj-value').textContent=p.construction_value_display || ('$'+(p.construction_value||0).toLocaleString());
  document.getElementById('proj-sheets').textContent=p.total_sheets+' sheets';
  const dl=document.getElementById('disc-list');
  Object.entries(p.disciplines).forEach(([name,sheets])=>{{
    const n = (sheets && sheets.length) || 0;
    const cnt = n > 0 ? `<span class="count">${{n}}</span>` : '';
    dl.innerHTML+=`<span class="disc-tag">${{name}}${{cnt}}</span>`;
  }});
  // Hero in results view
  document.getElementById('rh-title').textContent = p.name_long || p.name;
  document.getElementById('rh-addr').textContent = p.address;
  // Report mockup
  document.getElementById('rm-proj').textContent=p.name;
  document.getElementById('rm-count').textContent=s.total_conflicts;
  document.getElementById('rm-cost').textContent='$'+s.cost_low.toLocaleString()+' – $'+s.cost_high.toLocaleString();
  updateNavLocks();
}}

function showView(id){{
  if(!analysisComplete && (id==='results'||id==='report')) return;
  document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.nav button').forEach(b=>{{
    if(b.textContent.toLowerCase().includes(id==='dashboard'?'dashboard':id==='progress'?'analysis':id))
      b.classList.add('active');
  }});
  document.querySelectorAll('.mobile-tab').forEach(b=>{{
    b.classList.toggle('active', b.dataset.view===id);
  }});
  if(id==='results'&&!document.getElementById('conflict-list').innerHTML) buildResults();
}}

function copyLink(){{
  const url = window.location.href;
  navigator.clipboard.writeText(url).then(()=>{{
    const btns = document.querySelectorAll('.action-btn');
    btns.forEach(b=>{{
      if(b.textContent.includes('Copy')) b.textContent = ' Copied!';
    }});
    setTimeout(()=>location.reload(),1200);
  }}).catch(()=>{{}});
}}

function startAnalysis(){{
  showView('progress');
  let i=0;
  const run=()=>{{
    if(i>=STAGES.length){{
      analysisComplete=true;
      updateNavLocks();
      setTimeout(()=>showView('results'),800);
      return;
    }}
    const s=STAGES[i];
    document.getElementById('pct').textContent=s.pct+'%';
    document.getElementById('pbar').style.width=s.pct+'%';
    document.getElementById('stage').textContent=s.text;
    const log=document.getElementById('log');
    const cls=s.log.startsWith('⚠')?'log-line highlight':'log-line';
    log.innerHTML+=`<div class="${{cls}}"><span class="time">${{new Date().toLocaleTimeString()}}</span>${{s.log}}</div>`;
    log.scrollTop=log.scrollHeight;
    i++;
    setTimeout(run, 500+Math.random()*900);
  }};
  run();
}}

const SEVERITY_ORDER = {{Critical:0, High:1, Medium:2, Low:3}};
function sortedConflicts(){{
  return DATA.conflicts.slice().sort((a,b)=>{{
    const sa = SEVERITY_ORDER[a.severity]??99, sb=SEVERITY_ORDER[b.severity]??99;
    if(sa!==sb) return sa-sb;
    return (b.cost_high||0)-(a.cost_high||0);
  }});
}}

function discPairCounts(conflicts){{
  const counts = new Map();
  conflicts.forEach(c=>{{
    const a = (c.disc_a||'').trim(), b = (c.disc_b||'').trim();
    if(!a || !b) return;
    const key = [a,b].sort().join(' ↔ ');
    counts.set(key, (counts.get(key)||0) + 1);
  }});
  return Array.from(counts.entries()).sort((x,y)=>y[1]-x[1]);
}}

function discAbbrev(name){{
  const map = {{Architectural:'A',Structural:'S',Mechanical:'M',Electrical:'E',Plumbing:'P',
    Civil:'C',Landscape:'L','Fire Protection':'F','Fire Alarm':'FA','Low Voltage':'LV',
    Signage:'SG','Interior Design':'ID',Kitchen:'K',Telecom:'T',Specifications:'SP'}};
  return map[name] || (name||'').charAt(0).toUpperCase();
}}

function buildResults(){{
  const s=DATA.summary;
  document.getElementById('summary-row').innerHTML=`
    <div class="stat-box stat-total"><div class="num">${{s.total_conflicts}}</div><div class="lbl">Total Conflicts</div></div>
    <div class="stat-box stat-critical"><div class="num">${{s.critical}}</div><div class="lbl">Critical</div></div>
    <div class="stat-box stat-high"><div class="num">${{s.high}}</div><div class="lbl">High</div></div>
    <div class="stat-box stat-medium"><div class="num">${{s.medium}}</div><div class="lbl">Medium</div></div>
    <div class="stat-box stat-low"><div class="num">${{s.low}}</div><div class="lbl">Low</div></div>`;
  document.getElementById('summary-row2').innerHTML=`
    <div class="stat-cost"><div class="lbl">Cost Exposure</div><div class="num">$${{s.cost_low.toLocaleString()}} – $${{s.cost_high.toLocaleString()}}</div></div>
    <div class="stat-pairs"><div class="lbl">Discipline Pairs</div><div class="num">${{s.discipline_pairs}}</div></div>`;

  // Discipline pair strip
  const pairs = discPairCounts(DATA.conflicts).slice(0, 8);
  const strip = document.getElementById('disc-pair-strip');
  strip.innerHTML = `<span class="strip-label">By Pair:</span>` + pairs.map(([k,v])=>
    `<span class="disc-pair-chip">${{escapeHtml(k)}} <span class="pair-count">${{v}}</span></span>`
  ).join('');

  const severities=['All','Critical','High','Medium','Low'];
  document.getElementById('filters').innerHTML=severities.map(sv=>
    `<button class="filter-btn ${{sv==='All'?'active':''}}" onclick="filterConflicts('${{sv}}',this)">${{sv}}</button>`
  ).join('');

  renderConflicts('All');
}}

let currentFilter='All';
function filterConflicts(sev,btn){{
  currentFilter=sev;
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  renderConflicts(sev);
}}

function scoreColor(v){{return v>=8?'var(--critical)':v>=5?'var(--high)':'var(--low)'}}

function selectConflict(idx, sheets, title){{
  document.querySelectorAll('.conflict-card').forEach(c=>c.classList.remove('active'));
  const card = document.querySelector(`.conflict-card[data-idx="${{idx}}"]`);
  if(card) card.classList.add('active');
  // Update viewer pane
  document.getElementById('viewer-title').textContent = title || 'Sheet Preview';
  document.getElementById('viewer-sheet-id').textContent = sheets || '—';
  const canvas = document.getElementById('viewer-canvas');
  // Place a pin in a deterministic position based on idx
  const pinX = 20 + (idx * 37) % 60;
  const pinY = 25 + (idx * 53) % 50;
  const existingPin = canvas.querySelector('.viewer-pin');
  if(existingPin) existingPin.remove();
  const pin = document.createElement('div');
  pin.className = 'viewer-pin';
  pin.style.left = pinX + '%';
  pin.style.top = pinY + '%';
  pin.textContent = '!';
  pin.title = 'Conflict location (approximate)';
  canvas.appendChild(pin);
}}

function renderConflicts(severity){{
  const sorted = sortedConflicts();
  const filtered = severity==='All' ? sorted : sorted.filter(c=>c.severity===severity);
  const visible = filtered.slice(0, RENDER_CAP);
  const hidden = filtered.length - visible.length;

  const list=document.getElementById('conflict-list');
  list.innerHTML=visible.map((c, idx)=>{{
    const dims=['constructability','cost','safety','schedule','downstream'];
    const scoresHTML=dims.map(d=>{{
      const v=(c.scores||{{}})[d]||0;
      return `<div class="score-dim">
        <div class="dim-label">${{d.slice(0,6)}}</div>
        <div class="score-bar-bg"><div class="score-bar-fill" style="width:${{v*10}}%;background:${{scoreColor(v)}}"></div></div>
        <div class="dim-val" style="color:${{scoreColor(v)}}">${{v}}/10</div>
      </div>`;
    }}).join('');

    const sheetsStr = Array.isArray(c.sheets)?c.sheets.join(', '):(c.sheets||'');
    const da = c.disc_a || '', db = c.disc_b || '';
    const pairTag = (da && db) ? `${{discAbbrev(da)}} ↔ ${{discAbbrev(db)}}` : '';
    const snippet = (c.description || '').slice(0, 180);
    // FIX-S181: HTML-encode embedded quotes so JSON.stringify(...) values
    // can't terminate the outer onclick="..." attribute prematurely.
    const sheetsAttr = JSON.stringify(sheetsStr).replace(/"/g, '&quot;');
    const titleAttr  = JSON.stringify(c.title || '').replace(/"/g, '&quot;');

    return `<div class="conflict-card" data-sev="${{c.severity}}" data-idx="${{idx}}"
      onclick="selectConflict(${{idx}}, ${{sheetsAttr}}, ${{titleAttr}}); this.classList.toggle('expanded')">
      <div class="cc-header">
        <div class="cc-left-col">
          <span class="sev-badge sev-${{c.severity}}">${{c.severity}}</span>
          ${{pairTag ? `<span class="disc-pair-tag">${{pairTag}}</span>` : ''}}
        </div>
        <div class="cc-body-col">
          <div class="cc-row-top">
            <div class="cc-title">${{escapeHtml(c.title)}}</div>
            <div class="cc-index">#${{idx+1}}</div>
          </div>
          <div class="cc-snippet">${{escapeHtml(snippet)}}</div>
        </div>
        <span class="cc-chevron">▼</span>
      </div>
      <div class="cc-body">
        <div class="cc-meta">
          <div class="cc-meta-item"><span class="k">Disciplines:</span> ${{escapeHtml(da)}} ↔ ${{escapeHtml(db)}}</div>
          <div class="cc-meta-item"><span class="k">Type:</span> ${{escapeHtml(c.type||'')}}</div>
          <div class="cc-meta-item"><span class="k">Location:</span> ${{escapeHtml(c.location||'')}}</div>
          <div class="cc-meta-item"><span class="k">Sheets:</span> ${{escapeHtml(sheetsStr)}}</div>
        </div>
        <div class="cc-desc">${{escapeHtml(c.description||'')}}</div>
        <div class="scores-grid">${{scoresHTML}}</div>
        <div class="cc-impact">
          <div class="impact-box"><span class="ib-label">Cost Exposure:</span> $${{(c.cost_low||0).toLocaleString()}} – $${{(c.cost_high||0).toLocaleString()}}</div>
          <div class="impact-box"><span class="ib-label">Schedule Impact:</span> ${{escapeHtml(c.schedule_impact||'')}}</div>
        </div>
        <div class="cc-action"><strong>Recommended Action:</strong> ${{escapeHtml(c.recommended_action||'')}}</div>
      </div>
    </div>`;
  }}).join('');

  const notice = document.getElementById('truncated-notice');
  if(hidden > 0){{
    notice.innerHTML=`<div class="truncated-notice"><strong>Showing top ${{visible.length}} of ${{filtered.length}} conflicts</strong> by severity. Contact <a href="mailto:hello@flikt.ai">hello@flikt.ai</a> to run Flikt.AI on your project and see all ${{DATA.summary.total_conflicts}} findings.</div>`;
  }} else {{
    notice.innerHTML='';
  }}
}}

function escapeHtml(s){{
  return String(s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]);
}}
</script>

<div style="text-align:center;padding:24px 16px 88px;color:var(--text-muted);font-size:11.5px;border-top:1px solid var(--border);margin-top:32px">
  Flikt.AI &middot; &copy; 2026 &middot; Patents Pending
</div>

</body>
</html>
"""
