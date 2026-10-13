"""Seed consent-gated synthetic household/plot data (no real personal data)."""
import sqlite3, pathlib
DB = pathlib.Path(__file__).parent / "households.db"
conn = sqlite3.connect(DB)
conn.executescript("""
DROP TABLE IF EXISTS plots;
CREATE TABLE plots (plot_id TEXT, household TEXT, crop TEXT, consent INTEGER,
  area_hectares REAL, last_visit TEXT, notes TEXT);
INSERT INTO plots VALUES
 ('plot-001','HH-01','maize',1,1.2,'2026-10-05','yellowing leaves reported'),
 ('plot-002','HH-02','cassava',1,0.8,'2026-09-28','fine, routine check'),
 ('plot-003','HH-03','tomato',0,0.4,'2026-09-20','consent NOT recorded');
""")
conn.commit(); print("seeded", DB)
