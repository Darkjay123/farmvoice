"""FarmVoice MCP server. Four tools: get_rainfall, get_prices, get_plot_history, draft_advisory."""
from mcp.server.fastmcp import FastMCP
import json, datetime, pathlib
from .data_sources import get_rainfall, get_prices
from .plots import get_plot_history

mcp = FastMCP("farmvoice")
LOG = pathlib.Path(__file__).parent.parent / "data" / "tool_log.jsonl"

def _log(tool, args, out):
    with open(LOG, "a") as f:
        f.write(json.dumps({"tool": tool, "args": args, "out": out,
                            "ts": datetime.datetime.utcnow().isoformat() + "Z"}) + "\n")

@mcp.tool()
def get_rainfall(lat: float, lon: float, days: int = 30) -> dict:
    """Rainfall total and agroclimatic zone for a location (CHIRPS-class open archive)."""
    out = get_rainfall(lat, lon, days); _log("get_rainfall", {"lat": lat, "lon": lon, "days": days}, out); return out

@mcp.tool()
def get_prices(commodity: str = "maize", admin1: str = None, limit: int = 10) -> dict:
    """Latest WFP market prices for a commodity, optionally filtered by state."""
    out = get_prices(commodity, admin1, limit); _log("get_prices", {"commodity": commodity, "admin1": admin1}, out); return out

@mcp.tool()
def get_plot_history(plot_id: str, consent: bool = False) -> dict:
    """A household plot's recorded history. consent must be True (officer-confirmed)."""
    out = get_plot_history(plot_id, consent); _log("get_plot_history", {"plot_id": plot_id, "consent": consent}, out); return out

@mcp.tool()
def draft_advisory(plot_id: str, officer_id: str, approval_token: str, question: str, rainfall: dict, prices: dict, history: dict) -> dict:
    """Draft a citation-backed advisory. IRREVERSIBLE-ADJACENT: refuses without an approval token."""
    if not approval_token or not approval_token.startswith("APPR-"):
        return {"refused": True,
                "reason": "No officer approval token. The draft advisory will not be generated until a named officer signs off."}
    draft = (f"Advisory for plot {plot_id} (question: {question})\n"
             f"- Rainfall (last 30d): {rainfall.get('total_mm')} mm, zone {rainfall.get('agroclimatic_zone')} "
             f"[source: {rainfall.get('source')}]\n"
             f"- Market prices: latest {prices.get('commodity')} entries from {prices.get('source')}\n"
             f"- Plot history: {len(history.get('records', []))} records on file\n"
             f"Recommendation follows from the evidence above; officer review required before sending.")
    entry = {"tool": "draft_advisory", "plot_id": plot_id, "officer_id": officer_id,
             "approval_token": approval_token, "question": question, "ts": datetime.datetime.utcnow().isoformat() + "Z"}
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return {"draft": draft, "approved_by": officer_id, "citation_sources": [rainfall.get("source"), prices.get("source")]}

if __name__ == "__main__":
    mcp.run()
