"""Offline tests: consent gate, advisory approval gate, log writing."""
import os, sys, json, tempfile, pathlib, types
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_consent_gate_blocks_without_consent():
    from mcp_server.plots import get_plot_history
    import pytest
    with pytest.raises(PermissionError):
        get_plot_history("plot-003", consent=False)

def test_consent_gate_allows_with_consent():
    import subprocess
    subprocess.run([sys.executable, "data/seed_households.py"], cwd=os.path.join(os.path.dirname(__file__), ".."), check=True)
    from mcp_server.plots import get_plot_history
    out = get_plot_history("plot-001", consent=True)
    assert out["consent"] is True and len(out["records"]) >= 1

def test_advisory_refuses_without_token():
    from mcp_server.server import draft_advisory
    out = draft_advisory("plot-001", "officer-x", "", "q", {}, {}, {"records": []})
    assert out.get("refused") is True

def test_advisory_runs_with_token():
    from mcp_server.server import draft_advisory
    out = draft_advisory("plot-001", "officer-7", "APPR-123", "wilting maize", 
                         {"total_mm": 120, "agroclimatic_zone": "sub-humid", "source": "Open-Meteo ERA5 archive"},
                         {"commodity": "maize", "source": "WFP via HDX"},
                         {"records": [{"plot_id": "plot-001"}]})
    assert out["approved_by"] == "officer-7" and "APPR" not in out["draft"]

def test_tool_log_written():
    log = pathlib.Path(os.path.join(os.path.dirname(__file__), "..", "data", "tool_log.jsonl"))
    assert log.exists() and any(json.loads(l)["tool"] == "draft_advisory" for l in log.read_text().splitlines())
