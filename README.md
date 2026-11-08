# Flight Price Monitor

Automatické hodinové měření ceny **PRG–SIN 6. 8. 2027 / SIN–PRG 24. 8. 2027**, 1 dospělý, Turkish Airlines (odlet 19:15 a návrat 23:05).

- [Dashboard](https://viper1971.github.io/flight-price-monitor/)
- [Historie měření](data/measurements.csv)
- [Ruční spuštění](../../actions/workflows/hourly.yml)

## Zprovoznění

1. GitHub → Settings → Secrets and variables → Actions → New repository secret: `AMADEUS_CLIENT_ID` a `AMADEUS_CLIENT_SECRET` (získané od [Amadeus for Developers](https://developers.amadeus.com/)).
2. Nastav proměnnou `AMADEUS_ENV` na `production` pouze s produkčními přihlašovacími údaji. Testovací API nevrací spolehlivé reálné ceny.
3. Actions → Hourly flight price check → Run workflow.
4. Settings → Pages → Deploy from a branch → `main` → `/docs`.

**Omezení:** Amadeus API není Skyscanner/KAYAK a nemusí obsahovat přesný let ani všechny nejlevnější nabídky. Bez API klíčů se pouze zaznamená `not_configured`. Žádná cena se nevymýšlí. Ceny mohou být v jiné měně, v tom případě nejsou vydávány za Kč. GitHub Actions plánuje hodinové běhy, ale čas spuštění může být opožděn. Při opakovaných kontrolách se mění i dostupnost a prodejní podmínky; z týdenních dat nelze prokázat, že nákup v určitou hodinu způsobuje nižší cenu.

Referenční cena 26 730 Kč je pouze údaj z uživatelova snímku, nikoli API měření.
