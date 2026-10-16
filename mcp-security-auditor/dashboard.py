import html
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
SCANNER = ROOT / "mcp_scanner.py"
REPORT_ROOT = ROOT / "dashboard_reports"

SERVERS = [
    ("Clean Server", ROOT / "demo" / "clean_server.py"),
    ("Rugpull Server", ROOT / "demo" / "rugpull_server.py"),
    ("Vulnerable Server", ROOT / "demo" / "vuln_server.py"),
]

ACCENT = "#4B3FD1"
SEV_ORDER = ["critical", "high", "medium", "low", "info", "unknown"]
SEV_COLOR = {
    "critical": "#7A0F2E",
    "high": "#D23B2A",
    "medium": "#E59A12",
    "low": "#3E7CB1",
    "info": "#8A90A6",
    "unknown": "#B9BDCB",
}

st.set_page_config(page_title="MCP Sentinel", page_icon="🛡️", layout="wide")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --paper: #F6F5F9;
  --panel: #FFFFFF;
  --ink: #1B2142;
  --muted: #62688A;
  --line: #E1E1EC;
  --accent: #4B3FD1;
}

html, body, [class*="st-"], .stApp, button, input, textarea {
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
}
h1, h2, h3, .display { font-family: 'Bricolage Grotesque', 'IBM Plex Sans', sans-serif !important; }
code, pre, .mono { font-family: 'IBM Plex Mono', ui-monospace, monospace !important; }

.stApp { background: var(--paper); color: var(--ink); }
.block-container { max-width: 1180px; padding-top: 2.4rem; padding-bottom: 4rem; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

/* wordmark */
.wordmark { display: flex; align-items: center; gap: 14px; }
.wordmark svg { flex: none; }
.wordmark .name { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.9rem; letter-spacing: -0.035em; line-height: 1; }
.wordmark .tag { color: var(--muted); font-size: 0.92rem; margin-top: 5px; }

/* summary */
.summary { margin: 38px 0 6px; display: flex; align-items: baseline; flex-wrap: wrap; gap: 6px 18px; }
.summary .big { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 4.4rem; letter-spacing: -0.05em; line-height: 0.95; }
.summary .text { font-size: 1.3rem; font-weight: 500; letter-spacing: -0.01em; }
.sevline { display: flex; flex-wrap: wrap; gap: 6px 26px; margin: 12px 0 0; font-size: 1rem; }
.sevline span { display: inline-flex; align-items: center; gap: 8px; }
.sevline b { font-weight: 600; font-size: 1.15rem; }
.sevline i { width: 11px; height: 11px; border-radius: 2px; display: inline-block; }
.scope { color: var(--muted); font-size: 0.9rem; margin-top: 14px; max-width: 640px; line-height: 1.5; }

/* ledger */
.sect { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; margin: 42px 0 12px; }
.ledger { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }
.row {
  display: grid; grid-template-columns: 1.25fr 0.95fr 2.6fr; gap: 20px;
  align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--line);
}
.row:last-child { border-bottom: none; }
.row .srv { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.2rem; letter-spacing: -0.02em; }
.row .file { color: var(--muted); font-size: 0.8rem; margin-top: 3px; }
.row .verdict { font-weight: 600; font-size: 1rem; display: flex; align-items: center; gap: 9px; }
.row .verdict::before { content: ""; width: 9px; height: 9px; border-radius: 99px; background: currentColor; flex: none; }
.row .sub { color: var(--muted); font-size: 0.82rem; margin-top: 4px; font-weight: 400; }
.strip { display: flex; flex-wrap: wrap; gap: 4px; }
.strip i { width: 16px; height: 16px; border-radius: 2px; display: block; }
.strip.none { color: var(--muted); font-size: 0.9rem; }
.pending .srv, .pending .verdict { color: var(--muted); }
.pending .strip i { background: transparent; border: 1.5px dashed #C9CCDA; }

/* finding detail */
.f-meta { color: var(--muted); font-size: 0.86rem; margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 4px 14px; align-items: center; }
.pill { display: inline-block; font-size: 0.8rem; font-weight: 600; padding: 2px 9px; border-radius: 3px; color: #fff; }
.f-label { font-weight: 600; font-size: 0.88rem; margin: 14px 0 4px; }
.f-fix { border-left: 3px solid var(--accent); background: #EFEDFB; padding: 10px 14px; border-radius: 0 4px 4px 0; font-size: 0.94rem; line-height: 1.5; }

/* widgets */
div.stButton > button[kind="primary"] {
  background: var(--ink); color: #fff; border: none; border-radius: 6px;
  padding: 0.7rem 1.2rem; font-weight: 600; font-size: 0.98rem;
}
div.stButton > button[kind="primary"]:hover { background: var(--accent); color: #fff; }
div.stButton > button[kind="primary"]:focus-visible { outline: 3px solid #B7B0F3; outline-offset: 2px; }
div[data-testid="stExpander"] { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; margin-bottom: 8px; }
div[data-testid="stExpander"] summary { font-weight: 500; }
div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }
button[data-baseweb="tab"] { font-weight: 500; }
.footnote { color: var(--muted); font-size: 0.85rem; margin-top: 36px; }

@media (max-width: 820px) {
  .row { grid-template-columns: 1fr; gap: 10px; }
  .summary .big { font-size: 3.2rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def sev_of(finding: dict) -> str:
    s = str(finding.get("severity", "unknown")).strip().lower()
    return s if s in SEV_ORDER else "unknown"


def sev_counts(findings: list) -> dict:
    counts = {s: 0 for s in SEV_ORDER}
    for f in findings:
        counts[sev_of(f)] += 1
    return counts


def count_text(counts: dict) -> str:
    return ", ".join(f"{counts[s]} {s}" for s in SEV_ORDER if counts[s])


def verdict(res: dict):
    if not res["ok"]:
        return "Scan failed", "#A32D20"
    c = sev_counts(res["findings"])
    if c["critical"] or c["high"]:
        return "Action needed", SEV_COLOR["high"]
    if c["medium"] or c["low"] or c["unknown"]:
        return "Review findings", "#B87708"
    if c["info"]:
        return "Informational only", SEV_COLOR["info"]
    return "No findings", ACCENT


def ledger_row(res: dict) -> str:
    v, color = verdict(res)
    if not res["ok"]:
        strip = f'<div class="strip none">{esc(res["error"])}</div>'
        sub = ""
    else:
        findings = sorted(res["findings"], key=lambda f: SEV_ORDER.index(sev_of(f)))
        if findings:
            squares = "".join(
                f'<i style="background:{SEV_COLOR[sev_of(f)]}" '
                f'title="{esc(sev_of(f).title())}: {esc(f.get("id", ""))} {esc(f.get("title", ""))}"></i>'
                for f in findings
            )
            strip = f'<div class="strip">{squares}</div>'
            sub = f'<div class="sub">{len(findings)} total: {count_text(sev_counts(findings))}</div>'
        else:
            strip = '<div class="strip none">Nothing reported by the static scan</div>'
            sub = ""
    return f"""
    <div class="row">
      <div><div class="srv">{esc(res['label'])}</div><div class="file mono">{esc(res['file'])}</div></div>
      <div><div class="verdict" style="color:{color}">{v}</div>{sub}</div>
      {strip}
    </div>"""


def pending_row(label: str, path: Path) -> str:
    return f"""
    <div class="row pending">
      <div><div class="srv">{esc(label)}</div><div class="file mono">demo/{esc(path.name)}</div></div>
      <div><div class="verdict">Not scanned</div></div>
      <div class="strip"><i></i><i></i><i></i></div>
    </div>"""


def run_scan(label: str, server_path: Path) -> dict:
    res = {
        "label": label,
        "file": f"demo/{server_path.name}",
        "stem": server_path.stem,
        "ok": False,
        "error": "",
        "findings": [],
        "stdout": "",
        "markdown": "",
        "json_bytes": b"",
    }

    if not server_path.is_file():
        res["error"] = f"File not found: {server_path}"
        return res

    report_dir = REPORT_ROOT / server_path.stem
    report_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable, str(SCANNER), "scan", str(server_path),
        "-m", "static",
        "--format", "all",
        "--out", str(report_dir),
        "--fail-on", "never",
    ]

    try:
        proc = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, timeout=120
        )
        if proc.returncode != 0:
            res["error"] = f"Scanner exited with code {proc.returncode}. {proc.stderr.strip()}"
            return res

        json_report = report_dir / "report.json"
        if not json_report.is_file():
            res["error"] = "The JSON report was not generated."
            return res

        data = json.loads(json_report.read_text(encoding="utf-8"))
        # Adapt the extraction to the scanner's report schema.
        findings = [f for f in data.get("findings", []) if isinstance(f, dict)]
        for f in findings:
            f["dashboard_server"] = label

        md_report = report_dir / "report.md"
        res.update(
            ok=True,
            findings=findings,
            stdout=proc.stdout or "",
            markdown=md_report.read_text(encoding="utf-8") if md_report.is_file() else "",
            json_bytes=json_report.read_bytes(),
        )
    except subprocess.TimeoutExpired:
        res["error"] = "The scan timed out after 120 seconds."
    except (OSError, json.JSONDecodeError) as error:
        res["error"] = str(error)
    return res


# ---------------------------------------------------------------------------
# Top bar: wordmark and scan action
# ---------------------------------------------------------------------------
top_l, top_r = st.columns([4, 1.3], vertical_alignment="center")
with top_l:
    st.markdown(
        f"""
<div class="wordmark">
  <svg width="38" height="38" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d="M12 2 21 5.5V12c0 5-4 8.5-9 10-5-1.5-9-5-9-10V5.5L12 2Z" fill="#1B2142"/>
    <circle cx="12" cy="11" r="3.2" fill="{ACCENT}"/>
    <path d="M12 14.2V18" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round"/>
  </svg>
  <div>
    <div class="name">MCP Sentinel</div>
    <div class="tag">Security audit for MCP servers</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with top_r:
    start = st.button("Scan all three servers", type="primary", use_container_width=True)

if start:
    if not SCANNER.is_file():
        st.error("mcp_scanner.py was not found next to this dashboard.")
        st.stop()

    REPORT_ROOT.mkdir(exist_ok=True)
    results = []
    with st.status("Scanning servers…", expanded=True) as status:
        for label, path in SERVERS:
            st.write(f"Scanning {label}")
            results.append(run_scan(label, path))
        n_failed = sum(1 for r in results if not r["ok"])
        status.update(
            label="Scan finished" if not n_failed else f"Scan finished with {n_failed} failure(s)",
            state="complete" if not n_failed else "error",
            expanded=False,
        )
    st.session_state["results"] = results
    st.session_state["ran_at"] = datetime.now().strftime("%d %b %Y, %H:%M")

results = st.session_state.get("results")

# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------
if not results:
    st.markdown(
        """
<div class="summary"><div class="text" style="font-size:2rem;font-weight:700;letter-spacing:-0.03em" >No scan yet</div></div>
<div class="scope">Run a scan to audit the three demo servers. This dashboard uses static analysis only;
AI description analysis and dynamic probing are not part of this workflow.</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sect">Servers</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ledger">' + "".join(pending_row(l, p) for l, p in SERVERS) + "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
all_findings = [f for r in results if r["ok"] for f in r["findings"]]
totals = sev_counts(all_findings)
n_ok = sum(1 for r in results if r["ok"])
failed = [r["label"] for r in results if not r["ok"]]

sevline = "".join(
    f'<span><i style="background:{SEV_COLOR[s]}"></i><b>{totals[s]}</b> {s}</span>'
    for s in SEV_ORDER
    if totals[s] or s in ("high", "medium", "low", "info")
)
st.markdown(
    f"""
<div class="summary">
  <div class="big">{len(all_findings)}</div>
  <div class="text">{'finding' if len(all_findings) == 1 else 'findings'} across {n_ok} scanned {'server' if n_ok == 1 else 'servers'}</div>
</div>
<div class="sevline">{sevline}</div>
<div class="scope">Static analysis only. Last scan {esc(st.session_state.get('ran_at', ''))}.</div>
""",
    unsafe_allow_html=True,
)

if failed:
    st.warning("Some scans could not be completed: " + ", ".join(failed))

# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------
st.markdown('<div class="sect">Servers</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ledger">' + "".join(ledger_row(r) for r in results) + "</div>",
    unsafe_allow_html=True,
)
st.caption("Each square is one finding, ordered from most to least severe. Hover a square for its ID and title.")

# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------
st.markdown('<div class="sect">Findings</div>', unsafe_allow_html=True)

if not all_findings:
    st.write("No findings were returned by the successful scans.")
else:
    f1, f2, f3 = st.columns([2, 2, 3])
    present_sev = [s for s in SEV_ORDER if totals[s]]
    sel_sev = f1.multiselect("Severity", present_sev, default=present_sev, format_func=str.title)
    server_labels = [r["label"] for r in results if r["ok"]]
    sel_srv = f2.multiselect("Server", server_labels, default=server_labels)
    query = f3.text_input("Search", placeholder="ID, title, location, evidence or fix")

    def keep(f: dict) -> bool:
        if sev_of(f) not in sel_sev or f.get("dashboard_server") not in sel_srv:
            return False
        if query:
            hay = " ".join(
                str(f.get(k, "")) for k in ("id", "title", "location", "evidence", "fix")
            ).lower()
            return query.lower() in hay
        return True

    visible = sorted(
        (f for f in all_findings if keep(f)),
        key=lambda f: SEV_ORDER.index(sev_of(f)),
    )
    st.caption(f"Showing {len(visible)} of {len(all_findings)} findings")

    if not visible:
        st.info("No findings match the current filters.")
    else:
        tab_table, tab_detail = st.tabs(["Table", "Details"])

        with tab_table:
            df = pd.DataFrame(
                [
                    {
                        "Server": f.get("dashboard_server", ""),
                        "ID": f.get("id", ""),
                        "Severity": sev_of(f).title(),
                        "Location": f.get("location", ""),
                        "Finding": f.get("title", ""),
                        "Evidence": f.get("evidence", ""),
                        "Recommended fix": f.get("fix", ""),
                    }
                    for f in visible
                ]
            )

            def paint(v):
                return f"color:{SEV_COLOR.get(str(v).lower(), '#8A90A6')};font-weight:600"

            styler = df.style
            styler = (getattr(styler, "map", None) or styler.applymap)(paint, subset=["Severity"])

            st.dataframe(
                styler,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Severity": st.column_config.TextColumn(width="small"),
                    "ID": st.column_config.TextColumn(width="small"),
                    "Finding": st.column_config.TextColumn(width="medium"),
                    "Evidence": st.column_config.TextColumn(width="large"),
                    "Recommended fix": st.column_config.TextColumn(width="large"),
                },
            )

        with tab_detail:
            for f in visible:
                sev = sev_of(f)
                with st.expander(f"{f.get('id', '')}  {f.get('title', 'Untitled finding')}"):
                    st.markdown(
                        f'<div class="f-meta"><span class="pill" style="background:{SEV_COLOR[sev]}">{sev.title()}</span>'
                        f'<span>{esc(f.get("dashboard_server", ""))}</span>'
                        f'<span class="mono">{esc(f.get("location", "no location"))}</span></div>',
                        unsafe_allow_html=True,
                    )
                    if f.get("evidence"):
                        st.markdown('<div class="f-label">Evidence</div>', unsafe_allow_html=True)
                        st.code(str(f["evidence"]), language=None)
                    if f.get("fix"):
                        st.markdown('<div class="f-label">Recommended fix</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="f-fix">{esc(f["fix"])}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Full reports
# ---------------------------------------------------------------------------
st.markdown('<div class="sect">Full reports</div>', unsafe_allow_html=True)
ok_results = [r for r in results if r["ok"]]
if ok_results:
    tabs = st.tabs([r["label"] for r in ok_results])
    for tab, res in zip(tabs, ok_results):
        with tab:
            if res["markdown"]:
                st.markdown(res["markdown"])
            else:
                st.code(res["stdout"] or "Scan finished.", language=None)
            st.download_button(
                "Download JSON report",
                data=res["json_bytes"],
                file_name=f"{res['stem']}-report.json",
                mime="application/json",
                key=f"json-{res['stem']}",
            )
else:
    st.write("No reports available.")

st.markdown(
    '<div class="footnote">A completed scan with zero findings is not proof that a server is secure.</div>',
    unsafe_allow_html=True,
)
