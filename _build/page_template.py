"""HTML template for per-project demo pages.

Derived from lakewood.html. Uses {} placeholders filled by build_demo.py.

The CSS + DOM structure matches the existing portal to keep the refresh
a pure content swap.
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
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--navy:#1B2A4A;--navy-dark:#141F36;--amber:#E8A020;--amber-light:#F5C96B;
--critical:#DC2626;--high:#EA580C;--medium:#D97706;--low:#16A34A;--bg:#0F1723;--card:#1A2540;
--card-hover:#223050;--text:#E8ECF1;--text-muted:#8896A8;--border:#2A3A55}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
background:var(--bg);color:var(--text);line-height:1.5;overflow-x:hidden;transition:background .3s,color .3s}}
a{{color:var(--amber);text-decoration:none;transition:color .2s}}
a:hover{{color:var(--amber-light)}}
body.light-theme{{--bg:#f0f2f5;--card:#ffffff;--text:#333333;--text-muted:#666666;--border:#dddddd}}
.header{{background:var(--navy-dark);border-bottom:2px solid var(--amber);padding:12px 32px;
display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}}
.header-left{{display:flex;align-items:center;gap:20px}}
.back-link{{color:var(--text-muted);font-size:13px;font-weight:600;transition:color .2s}}
.back-link:hover{{color:var(--amber)}}
.logo{{font-size:22px;font-weight:800;letter-spacing:1px;color:white}}
.logo span{{color:var(--amber)}}
.theme-toggle{{background:none;border:1px solid var(--amber);color:var(--amber);
padding:8px 14px;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all .2s}}
.theme-toggle:hover{{background:rgba(232,160,32,0.1)}}
.nav{{display:flex;gap:4px}}
.nav button{{background:none;border:1px solid transparent;color:var(--text-muted);
padding:8px 16px;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all .2s}}
.nav button:hover{{color:white;background:rgba(255,255,255,0.05)}}
.nav button.active{{color:var(--amber);border-color:var(--amber);background:rgba(232,160,32,0.08)}}
.nav button.locked{{opacity:0.3;cursor:not-allowed;pointer-events:none}}
.view{{display:none;padding:32px;max-width:1100px;margin:0 auto}}
.view.active{{display:block}}
.hero{{text-align:center;margin:40px 0}}
.hero h1{{font-size:32px;font-weight:700;margin-bottom:8px}}
.hero p{{color:var(--text-muted);font-size:16px}}
.project-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;
padding:32px;margin:32px 0}}
.project-card h2{{font-size:20px;margin-bottom:16px;color:var(--amber)}}
.meta-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}}
.meta-item{{padding:12px;background:rgba(255,255,255,0.03);border-radius:8px}}
.meta-item .label{{font-size:11px;text-transform:uppercase;color:var(--text-muted);letter-spacing:1px}}
.meta-item .value{{font-size:18px;font-weight:700;margin-top:4px}}
.disciplines-list{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
.disc-tag{{background:var(--navy);padding:4px 12px;border-radius:16px;font-size:12px;
border:1px solid var(--border);color:white}}
.disc-tag .count{{color:var(--amber);font-weight:700;margin-left:4px}}
.btn{{display:inline-flex;align-items:center;gap:8px;padding:14px 32px;border-radius:8px;
font-size:15px;font-weight:700;cursor:pointer;border:none;transition:all .2s}}
.btn-primary{{background:var(--amber);color:var(--navy-dark)}}
.btn-primary:hover{{background:var(--amber-light);transform:translateY(-1px)}}
.btn-outline{{background:transparent;color:var(--amber);border:2px solid var(--amber)}}
.btn-outline:hover{{background:rgba(232,160,32,0.1)}}
.center-btn{{text-align:center;margin:32px 0}}
.progress-container{{max-width:700px;margin:60px auto;text-align:center}}
.progress-container h2{{font-size:24px;margin-bottom:32px}}
.progress-bar-wrap{{background:var(--navy);border-radius:12px;height:20px;overflow:hidden;margin:20px 0}}
.progress-bar{{background:linear-gradient(90deg,var(--amber),var(--amber-light));height:100%;
border-radius:12px;transition:width .3s ease;width:0%}}
.progress-pct{{font-size:48px;font-weight:800;color:var(--amber);margin:16px 0}}
.progress-stage{{color:var(--text-muted);font-size:14px;margin:8px 0}}
.activity-log{{background:var(--card);border:1px solid var(--border);border-radius:8px;
padding:16px;margin-top:32px;text-align:left;max-height:250px;overflow-y:auto;font-family:monospace;font-size:12px}}
.log-line{{padding:3px 0;color:var(--text-muted)}}
.log-line .time{{color:var(--amber);margin-right:8px}}
.log-line.highlight{{color:var(--text)}}
.summary-row{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:12px}}
.stat-box{{padding:20px;border-radius:10px;text-align:center;color:white}}
.stat-box .num{{font-size:32px;font-weight:800;color:white}}
.stat-box .lbl{{font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-top:4px;opacity:.85;color:white}}
.stat-total{{background:var(--navy)}}
.stat-critical{{background:var(--critical)}}
.stat-high{{background:var(--high)}}
.stat-medium{{background:var(--medium)}}
.stat-low{{background:var(--low)}}
.summary-row2{{display:grid;grid-template-columns:3fr 2fr;gap:12px;margin-bottom:24px}}
.stat-cost{{background:var(--navy);padding:16px 20px;border-radius:10px;text-align:center;color:white}}
.stat-cost .num{{font-size:22px;font-weight:700;color:white}}
.stat-cost .lbl{{color:white}}
.stat-pairs{{background:var(--amber);color:var(--navy-dark);padding:16px 20px;border-radius:10px;text-align:center}}
.stat-pairs .num{{font-size:22px;font-weight:700}}
.filters{{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}}
.filter-btn{{background:var(--card);border:1px solid var(--border);color:var(--text-muted);
padding:6px 14px;border-radius:20px;cursor:pointer;font-size:12px;font-weight:600;transition:all .2s}}
.filter-btn:hover,.filter-btn.active{{background:var(--amber);color:var(--navy-dark);border-color:var(--amber)}}
.conflict-card{{background:var(--card);border:1px solid var(--border);border-radius:10px;
margin-bottom:16px;overflow:hidden;transition:all .2s}}
.conflict-card:hover{{border-color:var(--amber);transform:translateY(-1px)}}
.cc-header{{padding:14px 20px;display:flex;align-items:center;gap:12px;cursor:pointer;flex-wrap:wrap}}
.sev-badge{{padding:4px 14px;border-radius:6px;font-size:12px;font-weight:800;color:white;min-width:70px;text-align:center}}
.sev-Critical{{background:var(--critical)}}
.sev-High{{background:var(--high)}}
.sev-Medium{{background:var(--medium)}}
.sev-Low{{background:var(--low)}}
.cc-title{{font-size:14px;font-weight:700;flex:1;min-width:200px}}
.cc-id{{font-size:11px;color:var(--text-muted)}}
.cc-chevron{{color:var(--text-muted);transition:transform .2s;font-size:18px}}
.conflict-card.expanded .cc-chevron{{transform:rotate(180deg)}}
.cc-body{{display:none;padding:0 20px 20px}}
.conflict-card.expanded .cc-body{{display:block}}
.cc-meta{{display:grid;grid-template-columns:1fr 1fr;gap:8px;background:rgba(255,255,255,0.03);
padding:12px;border-radius:8px;margin-bottom:12px}}
.cc-meta-item{{font-size:12px}}
.cc-meta-item .k{{color:var(--text-muted);font-weight:600}}
.cc-desc{{font-size:13px;color:var(--text-muted);margin-bottom:16px;line-height:1.6}}
.scores-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:12px}}
.score-dim{{text-align:center}}
.score-dim .dim-label{{font-size:10px;font-weight:700;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px}}
.score-bar-bg{{height:8px;background:rgba(255,255,255,0.1);border-radius:4px;overflow:hidden}}
.score-bar-fill{{height:100%;border-radius:4px;transition:width .5s ease}}
.score-dim .dim-val{{font-size:11px;font-weight:700;margin-top:2px}}
.cc-impact{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}}
.impact-box{{background:rgba(255,255,255,0.03);padding:10px 14px;border-radius:6px;
border-left:3px solid var(--amber);font-size:12px}}
.impact-box .ib-label{{font-weight:700;color:var(--text)}}
.cc-action{{background:rgba(232,160,32,0.06);border:1px solid rgba(232,160,32,0.2);
border-radius:8px;padding:12px 16px;font-size:12px;line-height:1.6}}
.cc-action strong{{color:var(--amber)}}
.truncated-notice{{padding:16px;margin-top:20px;background:rgba(232,160,32,0.06);
border:1px solid rgba(232,160,32,0.3);border-radius:8px;text-align:center;font-size:13px;color:var(--text-muted)}}
.truncated-notice strong{{color:var(--amber)}}
.report-preview{{text-align:center;margin:40px 0}}
.report-preview h2{{margin-bottom:16px}}
.report-mockup{{background:white;border-radius:8px;max-width:500px;margin:0 auto;
padding:40px;color:#333;box-shadow:0 8px 32px rgba(0,0,0,0.3)}}
.rm-header{{background:var(--navy);color:white;padding:30px;border-radius:6px;margin-bottom:20px}}
.rm-header h3{{font-size:24px;letter-spacing:1px}}
.rm-header p{{opacity:.7;font-size:12px;margin-top:4px}}
.rm-title{{font-size:18px;font-weight:700;color:var(--navy);text-align:center;margin:16px 0}}
.rm-bar{{height:4px;background:var(--amber);border-radius:2px;margin:12px 0}}
.rm-meta{{font-size:12px;color:#666;margin:8px 0}}
.mobile-tabs{{display:none;position:fixed;bottom:0;left:0;right:0;background:var(--navy-dark);
border-top:2px solid var(--amber);z-index:100;padding:6px 0 env(safe-area-inset-bottom,6px)}}
.mobile-tabs-inner{{display:flex;justify-content:space-around;align-items:center}}
.mobile-tab{{display:flex;flex-direction:column;align-items:center;gap:2px;background:none;border:none;
color:var(--text-muted);font-size:10px;font-weight:600;padding:6px 12px;cursor:pointer;transition:color .2s;
-webkit-tap-highlight-color:transparent}}
.mobile-tab svg{{width:20px;height:20px}}
.mobile-tab.active{{color:var(--amber)}}
.mobile-tab.locked{{opacity:0.3;pointer-events:none}}
@media(max-width:768px){{
.header{{flex-direction:column;gap:12px;padding:12px}}
.header-left{{flex-direction:column;width:100%;gap:8px}}
.summary-row{{grid-template-columns:repeat(2,1fr)}}
.summary-row2{{grid-template-columns:1fr}}
.meta-grid{{grid-template-columns:1fr 1fr}}
.scores-grid{{grid-template-columns:repeat(3,1fr)}}
.cc-impact{{grid-template-columns:1fr}}
.cc-meta{{grid-template-columns:1fr}}
.nav{{display:none}}
.mobile-tabs{{display:block}}
body{{padding-bottom:72px}}
}}
</style>
</head>
<body>
<div class="header">
  <div class="header-left">
    <a href="index.html" class="back-link">&larr; Back to Projects</a>
    <div class="logo">FLIKT<span>.AI</span></div>
  </div>
  <div style="display:flex;gap:12px;align-items:center">
    <div class="nav">
      <button class="active" onclick="showView('dashboard')">Dashboard</button>
      <button onclick="showView('progress')">Analysis</button>
      <button onclick="showView('results')">Results</button>
      <button onclick="showView('report')">Report</button>
    </div>
    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle light/dark theme">
      <span id="theme-icon"></span>
    </button>
  </div>
</div>

<div id="dashboard" class="view active">
  <div class="hero">
    <h1>AI-Powered Plan Coordination</h1>
    <p>Upload construction plans. Detect conflicts in minutes. Save thousands in rework.</p>
  </div>
  <div class="project-card">
    <h2 id="proj-name"></h2>
    <div class="meta-grid">
      <div class="meta-item"><div class="label">Address</div><div class="value" id="proj-addr"></div></div>
      <div class="meta-item"><div class="label">Project Type</div><div class="value" id="proj-type"></div></div>
      <div class="meta-item"><div class="label">Construction Value</div><div class="value" id="proj-value"></div></div>
      <div class="meta-item"><div class="label">Total Sheets</div><div class="value" id="proj-sheets"></div></div>
    </div>
    <div style="margin-top:20px">
      <div class="label" style="font-size:11px;text-transform:uppercase;color:var(--text-muted);letter-spacing:1px;margin-bottom:8px">Disciplines Detected</div>
      <div class="disciplines-list" id="disc-list"></div>
    </div>
  </div>
  <div class="center-btn">
    <button class="btn btn-primary" onclick="startAnalysis()">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
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
  <h2 style="margin-bottom:20px">Conflict Analysis Results</h2>
  <div class="summary-row" id="summary-row"></div>
  <div class="summary-row2" id="summary-row2"></div>
  <div class="filters" id="filters"></div>
  <div id="conflict-list"></div>
  <div id="truncated-notice"></div>
  <div class="center-btn" style="margin-top:24px">
    <button class="btn btn-primary" onclick="showView('report')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      View Full Report
    </button>
  </div>
</div>

<div id="report" class="view">
  <div class="report-preview">
    <h2>Plan Conflict &amp; Coordination Report</h2>
    <p style="color:var(--text-muted);margin-bottom:24px">Professional PDF report ready for download</p>
    <div class="report-mockup">
      <div class="rm-header">
        <h3>FLIKT.AI</h3>
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
    <div style="margin-top:32px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
      <a href="{PDF_FILENAME}" download class="btn btn-primary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Download PDF Report
      </a>
      <button class="btn btn-outline" onclick="showView('results')">
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

function toggleTheme(){{
  const isDark = !document.body.classList.contains('light-theme');
  if(isDark){{
    document.body.classList.add('light-theme');
    localStorage.setItem('flikt-theme','light');
    document.getElementById('theme-icon').textContent='\u{{1F319}}';
  }} else {{
    document.body.classList.remove('light-theme');
    localStorage.setItem('flikt-theme','dark');
    document.getElementById('theme-icon').textContent='\u{{2600}}\u{{FE0F}}';
  }}
}}

function loadTheme(){{
  const saved = localStorage.getItem('flikt-theme');
  if(saved === 'light'){{
    document.body.classList.add('light-theme');
    document.getElementById('theme-icon').textContent='\u{{1F319}}';
  }} else {{
    document.getElementById('theme-icon').textContent='\u{{2600}}\u{{FE0F}}';
  }}
}}

loadTheme();

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
  document.getElementById('rm-proj').textContent=p.name;
  document.getElementById('rm-count').textContent=s.total_conflicts;
  document.getElementById('rm-cost').textContent='$'+s.cost_low.toLocaleString()+' \u2013 $'+s.cost_high.toLocaleString();
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
    const cls=s.log.startsWith('\u26A0')?'log-line highlight':'log-line';
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

function buildResults(){{
  const s=DATA.summary;
  document.getElementById('summary-row').innerHTML=`
    <div class="stat-box stat-total"><div class="num">${{s.total_conflicts}}</div><div class="lbl">Total Conflicts</div></div>
    <div class="stat-box stat-critical"><div class="num">${{s.critical}}</div><div class="lbl">Critical</div></div>
    <div class="stat-box stat-high"><div class="num">${{s.high}}</div><div class="lbl">High</div></div>
    <div class="stat-box stat-medium"><div class="num">${{s.medium}}</div><div class="lbl">Medium</div></div>
    <div class="stat-box stat-low"><div class="num">${{s.low}}</div><div class="lbl">Low</div></div>`;
  document.getElementById('summary-row2').innerHTML=`
    <div class="stat-cost"><div class="lbl">Cost Exposure</div><div class="num">$${{s.cost_low.toLocaleString()}} \u2013 $${{s.cost_high.toLocaleString()}}</div></div>
    <div class="stat-pairs"><div class="lbl">Discipline Pairs</div><div class="num">${{s.discipline_pairs}}</div></div>`;

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

function renderConflicts(severity){{
  const sorted = sortedConflicts();
  const filtered = severity==='All' ? sorted : sorted.filter(c=>c.severity===severity);
  const visible = filtered.slice(0, RENDER_CAP);
  const hidden = filtered.length - visible.length;

  const list=document.getElementById('conflict-list');
  list.innerHTML=visible.map(c=>{{
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

    return `<div class="conflict-card" onclick="this.classList.toggle('expanded')">
      <div class="cc-header">
        <span class="sev-badge sev-${{c.severity}}">${{c.severity}}</span>
        <span class="cc-title">${{escapeHtml(c.title)}}</span>
        <span class="cc-id">${{c.id}}</span>
        <span class="cc-chevron">\u25BC</span>
      </div>
      <div class="cc-body">
        <div class="cc-meta">
          <div class="cc-meta-item"><span class="k">Disciplines:</span> ${{escapeHtml(c.disc_a||'')}} \u2194 ${{escapeHtml(c.disc_b||'')}}</div>
          <div class="cc-meta-item"><span class="k">Type:</span> ${{escapeHtml(c.type||'')}}</div>
          <div class="cc-meta-item"><span class="k">Location:</span> ${{escapeHtml(c.location||'')}}</div>
          <div class="cc-meta-item"><span class="k">Sheets:</span> ${{escapeHtml(sheetsStr)}}</div>
        </div>
        <div class="cc-desc">${{escapeHtml(c.description||'')}}</div>
        <div class="scores-grid">${{scoresHTML}}</div>
        <div class="cc-impact">
          <div class="impact-box"><span class="ib-label">Cost Exposure:</span> $${{(c.cost_low||0).toLocaleString()}} \u2013 $${{(c.cost_high||0).toLocaleString()}}</div>
          <div class="impact-box"><span class="ib-label">Schedule Impact:</span> ${{escapeHtml(c.schedule_impact||'')}}</div>
        </div>
        <div class="cc-action"><strong>Recommended Action:</strong> ${{escapeHtml(c.recommended_action||'')}}</div>
      </div>
    </div>`;
  }}).join('');

  const notice = document.getElementById('truncated-notice');
  if(hidden > 0){{
    notice.innerHTML=`<div class="truncated-notice"><strong>Showing top ${{visible.length}} of ${{filtered.length}} conflicts</strong> by severity. <a href="{PDF_FILENAME}" download>Download the full PDF report</a> to see all ${{DATA.summary.total_conflicts}} findings.</div>`;
  }} else {{
    notice.innerHTML='';
  }}
}}

function escapeHtml(s){{
  return String(s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]);
}}
</script>

<div style="text-align:center;padding:20px 16px 88px;color:var(--text-muted);font-size:11px;border-top:1px solid var(--border);margin-top:32px">
  Flikt.AI &middot; &copy; 2026 &middot; Patents Pending
</div>

</body>
</html>
"""
