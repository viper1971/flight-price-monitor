import csv, datetime as dt, json, os, pathlib, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "measurements.csv"
FIELDS = ["checked_at_prague","source","status","price_czk","currency","airline","outbound_date","return_date","url","details"]

def fetch(url, headers=None, body=None):
    req = urllib.request.Request(url, headers=headers or {}, data=body)
    with urllib.request.urlopen(req, timeout=35) as response:
        return json.load(response)

def check():
    key, secret = os.getenv("AMADEUS_CLIENT_ID"), os.getenv("AMADEUS_CLIENT_SECRET")
    if not key or not secret:
        return "not_configured", "", "", "", "Chybí API klíče Amadeus"
    host = "https://api.amadeus.com" if os.getenv("AMADEUS_ENV") == "production" else "https://test.api.amadeus.com"
    payload = urllib.parse.urlencode({"grant_type":"client_credentials","client_id":key,"client_secret":secret}).encode()
    token = fetch(host+"/v1/security/oauth2/token", {"Content-Type":"application/x-www-form-urlencoded"}, payload)["access_token"]
    params = {"originLocationCode":"PRG","destinationLocationCode":"SIN","departureDate":"2027-08-06","returnDate":"2027-08-24","adults":"1","currencyCode":"CZK","max":"250"}
    url = host+"/v2/shopping/flight-offers?"+urllib.parse.urlencode(params)
    offers = fetch(url, {"Authorization":"Bearer "+token}).get("data", [])
    exact = []
    for offer in offers:
        legs = offer.get("itineraries", [])
        if len(legs) != 2: continue
        out, back = (leg.get("segments", []) for leg in legs)
        if len(out) != 2 or len(back) != 2: continue
        if out[0].get("departure",{}).get("at","")[11:16] != "19:15": continue
        if back[0].get("departure",{}).get("at","")[11:16] != "23:05": continue
        if not all(s.get("carrierCode") == "TK" for s in out+back): continue
        exact.append(offer)
    if not exact:
        return "no_exact_offer", "", "", url, f"Přesný let nenalezen v {len(offers)} vrácených nabídkách; výsledky nemusí být úplné"
    best = min(exact, key=lambda x: float(x["price"]["grandTotal"]))
    price = best["price"]
    return "verified", price["grandTotal"], price["currency"], url, "Přesné časy a dopravce TK; zavazadla a tarif ověřte před nákupem"

def main():
    now = dt.datetime.now(ZoneInfo("Europe/Prague")).isoformat(timespec="seconds")
    try:
        status, price, currency, url, details = check()
    except Exception as exc:
        status, price, currency, url, details = "error", "", "", "", f"{type(exc).__name__}: {str(exc)[:250]}"
    DATA.parent.mkdir(parents=True, exist_ok=True)
    new = not DATA.exists() or DATA.stat().st_size == 0
    with DATA.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new: writer.writeheader()
        writer.writerow({"checked_at_prague":now,"source":"Amadeus Flight Offers API","status":status,"price_czk":price if currency=="CZK" else "","currency":currency,"airline":"TK","outbound_date":"2027-08-06","return_date":"2027-08-24","url":url,"details":details})
    print(json.dumps({"checked_at":now,"status":status,"price_czk":price if currency=="CZK" else None,"details":details},ensure_ascii=False))

if __name__ == "__main__": main()
