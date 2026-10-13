"""Plot history from a local consent-gated SQLite store (synthetic demo data)."""
import sqlite3, pathlib

DB = pathlib.Path(__file__).parent.parent / "data" / "households.db"

def get_plot_history(plot_id: str, consent: bool) -> dict:
    """Return a household plot's history. Requires the household's recorded consent."""
    if not consent:
        raise PermissionError("Household consent flag not set; refusing to read plot data")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        plots = conn.execute("SELECT * FROM plots WHERE plot_id = ?", (plot_id,)).fetchall()
        return {"plot_id": plot_id, "consent": True,
                "records": [dict(r) for r in plots]}
    finally:
        conn.close()
