"""Real, open data sources. No API keys required."""
import requests, datetime

OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"

def get_rainfall(lat: float, lon: float, days: int = 30) -> dict:
    """Rainfall + simple agroclimatic zone from Open-Meteo (ERA5 archive)."""
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    r = requests.get(OPEN_METEO_ARCHIVE, params={
        "latitude": lat, "longitude": lon,
        "start_date": start.isoformat(), "end_date": end.isoformat(),
        "daily": "precipitation_sum,et0_fao_evapotranspiration"}, timeout=30)
    r.raise_for_status()
    daily = r.json()["daily"]
    total = sum(d or 0 for d in daily["precipitation_sum"])
    zone = ("humid" if total > 200 else "semi-arid" if total < 50 else "sub-humid")
    return {"source": "Open-Meteo ERA5 archive", "lat": lat, "lon": lon,
            "days": days, "total_mm": round(total, 1),
            "agroclimatic_zone": zone, "daily_precipitation_mm":
            daily["precipitation_sum"], "retrieved_at": datetime.datetime.utcnow().isoformat() + "Z"}

WFP_HDX = "https://data.humdata.org/api/3/action/package_show?id=wfp-food-prices-for-nigeria"

def get_prices(commodity: str = "maize", admin1: str | None = None, limit: int = 10) -> dict:
    """Latest WFP food prices for Nigeria via the HDX CKAN API (open data)."""
    r = requests.get(WFP_HDX, timeout=30)
    r.raise_for_status()
    res = r.json()["result"]
    csv_url = next(res_["url"] for res_ in res["resources"] if res_["format"].lower() == "csv")
    import csv, io
    rows = list(csv.DictReader(io.StringIO(requests.get(csv_url, timeout=60).text)))
    rows = [x for x in rows if commodity.lower() in x.get("commodity", "").lower()
            and (not admin1 or admin1.lower() in x.get("admin1", "").lower())]
    rows.sort(key=lambda x: x.get("date", ""), reverse=True)
    picked = rows[:limit]
    return {"source": "WFP via HDX (wfp-food-prices-for-nigeria)", "commodity": commodity,
            "prices": [{"date": x.get("date"), "market": x.get("market"),
                        "admin1": x.get("admin1"), "price": x.get("price"),
                        "currency": x.get("currency"), "unit": x.get("unit")} for x in picked],
            "retrieved_at": datetime.datetime.utcnow().isoformat() + "Z"}
