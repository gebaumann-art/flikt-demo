"""
Flikt.AI — Local Processing Server
====================================
Simple FastAPI server that accepts plan uploads, processes them,
and serves results. Run locally for demos or testing.

Usage:
    python server.py                   # Start on port 8000
    python server.py --port 3000       # Custom port

Then visit http://localhost:8000
"""

import os
import sys
import json
import uuid
import shutil
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from process_plans import process_plan_set, classify_plan_set

# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(title="Flikt.AI Processor", version="1.0.0")

# Storage directories
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
UPLOADS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# In-memory job tracking
jobs = {}


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the upload/processing UI."""
    return UPLOAD_HTML


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "service": "Flikt.AI Processor"}


@app.post("/api/upload")
async def upload_plans(
    project_name: str = Form(...),
    client_name: str = Form(""),
    files: list[UploadFile] = File(...),
):
    """Upload plan PDFs and start processing."""
    # Create job
    job_id = str(uuid.uuid4())[:8]
    job_dir = UPLOADS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    output_dir = RESULTS_DIR / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded files
    saved_files = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
        file_path = job_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_files.append(file.filename)

    if not saved_files:
        raise HTTPException(400, "No PDF files uploaded")

    # Classify immediately to show disciplines
    classified = classify_plan_set(str(job_dir))

    # Initialize job
    jobs[job_id] = {
        "id": job_id,
        "project_name": project_name,
        "client_name": client_name,
        "status": "queued",
        "progress": 0,
        "message": "Upload complete, starting analysis...",
        "files": saved_files,
        "classified": {k: [Path(f).name for f in v] for k, v in classified.items()},
        "created_at": datetime.now().isoformat(),
        "results": None,
    }

    # Start processing in background thread
    thread = threading.Thread(
        target=_run_processing,
        args=(job_id, str(job_dir), str(output_dir), project_name, client_name),
        daemon=True,
    )
    thread.start()

    return {"job_id": job_id, "files": saved_files, "classified": jobs[job_id]["classified"]}


@app.get("/api/status/{job_id}")
async def job_status(job_id: str):
    """Get processing status for a job."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    job = jobs[job_id]
    return {
        "id": job["id"],
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "files": job["files"],
        "classified": job["classified"],
        "results": job.get("results"),
    }


@app.get("/api/results/{job_id}")
async def get_results(job_id: str):
    """Get full results for a completed job."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    if jobs[job_id]["status"] != "complete":
        raise HTTPException(400, "Job not complete")

    results_path = RESULTS_DIR / job_id / "results.json"
    if results_path.exists():
        with open(results_path) as f:
            return json.load(f)
    raise HTTPException(404, "Results file not found")


@app.get("/api/report/{job_id}")
async def download_report(job_id: str):
    """Download the PDF report for a completed job."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    output_dir = RESULTS_DIR / job_id
    pdf_files = list(output_dir.glob("*.pdf"))
    if not pdf_files:
        raise HTTPException(404, "Report not generated yet")

    return FileResponse(
        pdf_files[0],
        media_type="application/pdf",
        filename=pdf_files[0].name,
    )


# ============================================================================
# BACKGROUND PROCESSING
# ============================================================================

def _run_processing(job_id: str, upload_dir: str, output_dir: str,
                    project_name: str, client_name: str):
    """Run the processing pipeline in a background thread."""
    jobs[job_id]["status"] = "processing"

    def progress_cb(step, message, pct):
        jobs[job_id]["progress"] = pct
        jobs[job_id]["message"] = message

    try:
        results = process_plan_set(
            pdf_folder=upload_dir,
            project_name=project_name,
            client_name=client_name,
            output_dir=output_dir,
            progress_callback=progress_cb,
        )

        if "error" in results:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["message"] = results["error"]
        else:
            jobs[job_id]["status"] = "complete"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["message"] = "Analysis complete"
            jobs[job_id]["results"] = {
                "total_conflicts": results["summary"]["summary"]["total_conflicts"],
                "critical": results["summary"]["summary"]["critical"],
                "major": results["summary"]["summary"]["major"],
                "minor": results["summary"]["summary"]["minor"],
                "cost_low": results["summary"]["summary"]["cost_low"],
                "cost_high": results["summary"]["summary"]["cost_high"],
            }

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["message"] = str(e)


# ============================================================================
# EMBEDDED HTML UI
# ============================================================================

UPLOAD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flikt.AI — Plan Processor</title>
<style>
  /* ── Dark theme (default) ── */
  :root, [data-theme="dark"] {
    --navy: #1B2A4A; --amber: #E8A020; --red: #DC2626; --orange: #EA580C; --green: #16A34A;
    --bg: #0f1117; --bg-card: #1a1d27; --bg-input: #252833; --bg-hover: #2a2d3a;
    --text: #e4e4e7; --text-muted: #9ca3af; --text-heading: #f3f4f6;
    --border: #2e3140; --dropzone-bg: #1a1d27; --dropzone-hover: #252833;
    --file-bg: #252833; --action-bg: #1e2a3a; --score-bg: #252833;
    --bar-track: #252833; --header-bg: var(--navy);
  }
  /* ── Light theme ── */
  [data-theme="light"] {
    --bg: #f0f2f5; --bg-card: #ffffff; --bg-input: #ffffff; --bg-hover: #f8f8f8;
    --text: #333333; --text-muted: #666666; --text-heading: var(--navy);
    --border: #dddddd; --dropzone-bg: #ffffff; --dropzone-hover: #fdf8ee;
    --file-bg: #f8f8f8; --action-bg: #f0f7ff; --score-bg: #f0f0f0;
    --bar-track: #e0e0e0; --header-bg: var(--navy);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; transition: background 0.3s, color 0.3s; }
  .header { background: var(--header-bg); color: white; padding: 1rem 2rem; display: flex; align-items: center; gap: 1rem; }
  .header .logo { font-size: 1.5rem; font-weight: bold; }
  .header .logo span { color: var(--amber); }
  .header .subtitle { opacity: 0.7; font-size: 0.9rem; }
  .header .spacer { flex: 1; }
  .theme-toggle { background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); color: white; padding: 0.35rem 0.7rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; gap: 0.4rem; transition: background 0.2s; }
  .theme-toggle:hover { background: rgba(255,255,255,0.25); }
  .container { max-width: 900px; margin: 2rem auto; padding: 0 1rem; }

  /* Upload Form */
  .card { background: var(--bg-card); border-radius: 12px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-bottom: 1.5rem; border: 1px solid var(--border); transition: background 0.3s, border-color 0.3s; }
  .card h2 { color: var(--text-heading); margin-bottom: 1rem; font-size: 1.3rem; }
  .form-row { display: flex; gap: 1rem; margin-bottom: 1rem; }
  .form-row > * { flex: 1; }
  label { display: block; font-weight: 600; margin-bottom: 0.3rem; font-size: 0.9rem; color: var(--text-heading); }
  input[type="text"] { width: 100%; padding: 0.6rem 0.8rem; border: 1px solid var(--border); border-radius: 6px; font-size: 1rem; background: var(--bg-input); color: var(--text); transition: background 0.3s, border-color 0.3s, color 0.3s; }
  input[type="text"]:focus { outline: none; border-color: var(--amber); box-shadow: 0 0 0 2px rgba(232,160,32,0.2); }

  /* Drop zone */
  .dropzone { border: 2px dashed var(--border); border-radius: 12px; padding: 2rem; text-align: center; cursor: pointer; transition: all 0.2s; background: var(--dropzone-bg); }
  .dropzone:hover, .dropzone.dragover { border-color: var(--amber); background: var(--dropzone-hover); }
  .dropzone .icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
  .dropzone p { color: var(--text-muted); }
  .dropzone .hint { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem; }
  .file-list { margin-top: 1rem; }
  .file-item { display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0.6rem; background: var(--file-bg); border-radius: 6px; margin-bottom: 0.3rem; font-size: 0.9rem; }
  .file-item .remove { color: var(--red); cursor: pointer; font-weight: bold; }

  /* Buttons */
  .btn { padding: 0.7rem 1.5rem; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
  .btn-primary { background: var(--amber); color: var(--navy); }
  .btn-primary:hover { background: #d4910e; }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-outline { background: transparent; border: 2px solid var(--navy); color: var(--navy); }

  /* Progress */
  .progress-section { display: none; }
  .progress-bar-track { background: var(--bar-track); border-radius: 20px; height: 24px; overflow: hidden; margin: 1rem 0; }
  .progress-bar-fill { background: linear-gradient(90deg, var(--amber), #f0c040); height: 100%; border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; color: var(--navy); }
  .progress-msg { color: var(--text-muted); font-size: 0.9rem; min-height: 1.5rem; }

  /* Results */
  .results-section { display: none; }
  .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1rem 0; }
  .stat-box { text-align: center; padding: 1rem; border-radius: 10px; color: white; }
  .stat-box .val { font-size: 1.8rem; font-weight: 700; }
  .stat-box .lbl { font-size: 0.8rem; opacity: 0.9; }
  .bg-navy { background: var(--navy); }
  .bg-red { background: var(--red); }
  .bg-orange { background: var(--orange); }
  .bg-green { background: var(--green); }

  .conflict-card { border: 1px solid var(--border); border-radius: 10px; padding: 1rem; margin-bottom: 1rem; background: var(--bg-card); }
  .conflict-header { display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem; }
  .sev-badge { padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700; color: white; text-transform: uppercase; }
  .sev-Critical { background: var(--red); }
  .sev-Major { background: var(--orange); }
  .sev-Minor { background: var(--green); }
  .conflict-title { font-weight: 600; color: var(--text-heading); }
  .conflict-meta { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem; }
  .conflict-desc { font-size: 0.9rem; line-height: 1.5; }
  .conflict-action { background: var(--action-bg); border-radius: 6px; padding: 0.6rem; margin-top: 0.5rem; font-size: 0.85rem; }
  .conflict-action strong { color: var(--text-heading); }

  .scores-row { display: flex; gap: 0.5rem; margin: 0.5rem 0; flex-wrap: wrap; }
  .score-chip { font-size: 0.7rem; padding: 0.15rem 0.5rem; background: var(--score-bg); border-radius: 4px; color: var(--text); }

  /* Animations */
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
  .analyzing { animation: pulse 1.5s infinite; }
</style>
</head>
<body>

<div class="header">
  <div class="logo">FLIKT<span>.AI</span></div>
  <div class="subtitle">Plan Conflict Detection</div>
  <div class="spacer"></div>
  <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn" title="Toggle light/dark mode">
    <span id="themeIcon">☀️</span> <span id="themeLabel">Light</span>
  </button>
</div>

<div class="container">

  <!-- UPLOAD FORM -->
  <div id="upload-section">
    <div class="card">
      <h2>Upload Plan Set</h2>
      <div class="form-row">
        <div><label>Project Name *</label><input type="text" id="projectName" placeholder="e.g. 123 Main St Renovation"></div>
        <div><label>Client Name</label><input type="text" id="clientName" placeholder="e.g. ABC Construction"></div>
      </div>

      <label>Plan PDFs *</label>
      <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
        <div class="icon">📄</div>
        <p>Drop plan PDFs here or click to browse</p>
        <p class="hint">Accepts .pdf files — architectural, structural, MEP, civil, etc.</p>
      </div>
      <input type="file" id="fileInput" multiple accept=".pdf" style="display:none">
      <div class="file-list" id="fileList"></div>

      <div style="margin-top:1.5rem; display:flex; justify-content:flex-end;">
        <button class="btn btn-primary" id="submitBtn" onclick="submitPlans()" disabled>Start Analysis</button>
      </div>
    </div>
  </div>

  <!-- PROGRESS -->
  <div id="progress-section" class="progress-section">
    <div class="card">
      <h2 class="analyzing">Analyzing Plans...</h2>
      <div class="progress-bar-track">
        <div class="progress-bar-fill" id="progressBar" style="width:0%">0%</div>
      </div>
      <p class="progress-msg" id="progressMsg">Starting analysis...</p>
    </div>
  </div>

  <!-- RESULTS -->
  <div id="results-section" class="results-section">
    <div class="card">
      <h2>Analysis Complete</h2>
      <div class="stat-grid">
        <div class="stat-box bg-navy"><div class="val" id="statTotal">0</div><div class="lbl">Conflicts</div></div>
        <div class="stat-box bg-red"><div class="val" id="statCritical">0</div><div class="lbl">Critical</div></div>
        <div class="stat-box bg-orange"><div class="val" id="statMajor">0</div><div class="lbl">Major</div></div>
        <div class="stat-box bg-green"><div class="val" id="statMinor">0</div><div class="lbl">Minor</div></div>
      </div>
      <p id="costExposure" style="text-align:center;font-size:1.1rem;margin:0.5rem 0;"></p>
      <div style="display:flex;gap:1rem;justify-content:center;margin-top:1rem;">
        <button class="btn btn-primary" onclick="downloadReport()">Download PDF Report</button>
        <button class="btn btn-outline" onclick="location.reload()">New Analysis</button>
      </div>
    </div>

    <div class="card">
      <h2>Detected Conflicts</h2>
      <div id="conflictList"></div>
    </div>
  </div>

</div>

<script>
// ── Theme toggle ──
function initTheme() {
  const saved = localStorage.getItem('flikt-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeBtn(saved);
}
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('flikt-theme', next);
  updateThemeBtn(next);
}
function updateThemeBtn(theme) {
  document.getElementById('themeIcon').textContent = theme === 'dark' ? '☀️' : '🌙';
  document.getElementById('themeLabel').textContent = theme === 'dark' ? 'Light' : 'Dark';
}
initTheme();

let selectedFiles = [];
let currentJobId = null;

// --- Smooth progress bar state ---
let displayPct = 0;        // What the bar currently shows (float)
let serverPct = 0;         // Last real value from backend
let serverMsg = '';
let animFrame = null;
let lastTick = 0;

// Pipeline phase targets: when server reports X%, bar can drift up to Y%
// This prevents the bar from sitting still during the long AI call
const PHASE_CEILINGS = [
  { from: 0,  to: 10, ceiling: 14 },   // classify
  { from: 10, to: 50, ceiling: 54 },   // render
  { from: 50, to: 75, ceiling: 94 },   // detect (AI call — long wait)
  { from: 75, to: 90, ceiling: 94 },   // score + report
  { from: 90, to: 100, ceiling: 100 }, // done
];

function getCeiling(sPct) {
  for (const p of PHASE_CEILINGS) {
    if (sPct >= p.from && sPct < p.to) return p.ceiling;
  }
  return 100;
}

function animateBar(ts) {
  if (!lastTick) lastTick = ts;
  const dt = (ts - lastTick) / 1000; // seconds
  lastTick = ts;

  const ceiling = getCeiling(serverPct);
  const target = Math.min(serverPct === 100 ? 100 : Math.max(serverPct, displayPct), ceiling);

  if (displayPct < target) {
    // Fast catch-up if server jumped ahead; slow drift if waiting
    const gap = target - displayPct;
    const speed = gap > 5 ? 20 : 0.5; // %/sec
    displayPct = Math.min(target, displayPct + speed * dt);
  } else if (displayPct < ceiling && serverPct < 100) {
    // Slow drift toward ceiling while waiting for server
    displayPct = Math.min(ceiling, displayPct + 0.3 * dt);
  }

  const show = Math.round(displayPct);
  document.getElementById('progressBar').style.width = show + '%';
  document.getElementById('progressBar').textContent = show + '%';

  if (serverPct < 100) {
    animFrame = requestAnimationFrame(animateBar);
  } else {
    document.getElementById('progressBar').style.width = '100%';
    document.getElementById('progressBar').textContent = '100%';
  }
}

function startBarAnimation() {
  displayPct = 0; serverPct = 0; lastTick = 0;
  if (animFrame) cancelAnimationFrame(animFrame);
  animFrame = requestAnimationFrame(animateBar);
}

// --- Drag & drop ---
const dz = document.getElementById('dropzone');
dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('dragover'); });
dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
dz.addEventListener('drop', e => { e.preventDefault(); dz.classList.remove('dragover'); addFiles(e.dataTransfer.files); });
document.getElementById('fileInput').addEventListener('change', e => addFiles(e.target.files));

function addFiles(fileList) {
  for (const f of fileList) {
    if (f.name.toLowerCase().endsWith('.pdf') && !selectedFiles.find(s => s.name === f.name)) {
      selectedFiles.push(f);
    }
  }
  renderFileList();
}

function removeFile(idx) {
  selectedFiles.splice(idx, 1);
  renderFileList();
}

function renderFileList() {
  const el = document.getElementById('fileList');
  el.innerHTML = selectedFiles.map((f, i) =>
    `<div class="file-item"><span>📄 ${f.name} (${(f.size/1024/1024).toFixed(1)} MB)</span><span class="remove" onclick="removeFile(${i})">✕</span></div>`
  ).join('');
  document.getElementById('submitBtn').disabled = selectedFiles.length === 0 || !document.getElementById('projectName').value.trim();
}

document.getElementById('projectName').addEventListener('input', renderFileList);

async function submitPlans() {
  const projectName = document.getElementById('projectName').value.trim();
  if (!projectName || selectedFiles.length === 0) return;

  const formData = new FormData();
  formData.append('project_name', projectName);
  formData.append('client_name', document.getElementById('clientName').value.trim());
  for (const f of selectedFiles) formData.append('files', f);

  document.getElementById('upload-section').style.display = 'none';
  document.getElementById('progress-section').style.display = 'block';
  startBarAnimation();

  try {
    const resp = await fetch('/api/upload', { method: 'POST', body: formData });
    const data = await resp.json();
    currentJobId = data.job_id;
    pollStatus();
  } catch (e) {
    document.getElementById('progressMsg').textContent = 'Upload failed: ' + e.message;
  }
}

async function pollStatus() {
  if (!currentJobId) return;
  try {
    const resp = await fetch(`/api/status/${currentJobId}`);
    const data = await resp.json();

    // Update server state — the animation loop handles the bar
    serverPct = data.progress;
    serverMsg = data.message;
    document.getElementById('progressMsg').textContent = data.message;

    if (data.status === 'complete') {
      serverPct = 100;
      // Let the animation finish to 100, then show results after a short delay
      setTimeout(() => {
        if (animFrame) cancelAnimationFrame(animFrame);
        showResults(data.results);
        loadConflicts();
      }, 600);
    } else if (data.status === 'error') {
      if (animFrame) cancelAnimationFrame(animFrame);
      document.getElementById('progressMsg').textContent = 'Error: ' + data.message;
    } else {
      setTimeout(pollStatus, 1500);
    }
  } catch (e) {
    setTimeout(pollStatus, 2000);
  }
}

function showResults(r) {
  document.getElementById('progress-section').style.display = 'none';
  document.getElementById('results-section').style.display = 'block';
  document.getElementById('statTotal').textContent = r.total_conflicts;
  document.getElementById('statCritical').textContent = r.critical;
  document.getElementById('statMajor').textContent = r.major;
  document.getElementById('statMinor').textContent = r.minor;
  document.getElementById('costExposure').textContent =
    `Cost Exposure: $${r.cost_low.toLocaleString()} - $${r.cost_high.toLocaleString()}`;
}

async function loadConflicts() {
  try {
    const resp = await fetch(`/api/results/${currentJobId}`);
    const data = await resp.json();
    const list = document.getElementById('conflictList');
    list.innerHTML = (data.conflicts || []).map(c => `
      <div class="conflict-card">
        <div class="conflict-header">
          <span class="sev-badge sev-${c.severity}">${c.severity}</span>
          <span class="conflict-title">${c.title}</span>
        </div>
        <div class="conflict-meta">${c.disc_a} vs ${c.disc_b} | ${c.type} | ${c.location} | Sheets: ${(c.sheets||[]).join(', ')}</div>
        <div class="scores-row">
          <span class="score-chip">Build: ${c.scores?.constructability||'-'}/10</span>
          <span class="score-chip">Cost: ${c.scores?.cost||'-'}/10</span>
          <span class="score-chip">Safety: ${c.scores?.safety||'-'}/10</span>
          <span class="score-chip">Schedule: ${c.scores?.schedule||'-'}/10</span>
          <span class="score-chip">Downstream: ${c.scores?.downstream||'-'}/10</span>
        </div>
        <div class="conflict-desc">${c.description}</div>
        ${c.recommended_action ? `<div class="conflict-action"><strong>Recommended:</strong> ${c.recommended_action}</div>` : ''}
        <div class="conflict-meta" style="margin-top:0.5rem;">Cost: $${(c.cost_low||0).toLocaleString()}-$${(c.cost_high||0).toLocaleString()} | Schedule: ${c.schedule_impact}</div>
      </div>
    `).join('');
  } catch (e) { console.error(e); }
}

function downloadReport() {
  if (currentJobId) window.open(`/api/report/${currentJobId}`, '_blank');
}
</script>
</body>
</html>"""


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Flikt.AI Local Processing Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    print("=" * 50)
    print("  FLIKT.AI — Local Processing Server")
    print(f"  http://localhost:{args.port}")
    print("=" * 50)

    uvicorn.run(app, host=args.host, port=args.port)
