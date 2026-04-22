# Telecom Digest

Daglig norsk telecom-nyhetsbrev — generert automatisk med Claude og servert som en statisk nettside.

---

## Hvordan det fungerer

```
Claude (web search) → nyheter.json → Telecom Digest.html
```

Hver morgen søker Claude etter dagens viktigste telecom-nyheter, vurderer norsk relevans, og skriver resultatet til `nyheter.json`. HTML-filen leser JSON-filen og renderer designet. Designet røres aldri — bare innholdet byttes ut.

---

## Filstruktur

```
├── Telecom Digest.html   # Designmalen — røres ikke
├── nyheter.json          # Dagens innhold — genereres daglig
├── generate_nyheter.py   # Henter nyheter via Claude API
├── send_email.py         # Sender nyhetsbrevet via SendGrid (valgfritt)
└── .github/
    └── workflows/
        └── daily.yml     # GitHub Actions — kjører kl. 06:00 man–fre
```

---

## Kom i gang

### 1. Klon repoet

```bash
git clone https://github.com/dittbrukernavn/telecom-digest.git
cd telecom-digest
pip install anthropic sendgrid
```

### 2. Sett API-nøkkel og test lokalt

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python generate_nyheter.py
```

Åpne `Telecom Digest.html` i en nettleser etterpå (krever en lokal webserver, f.eks. `python -m http.server`).

### 3. Aktiver GitHub Actions

Gå til **Settings → Secrets and variables → Actions** i repoet og legg til:

| Secret | Beskrivelse |
|---|---|
| `ANTHROPIC_API_KEY` | Din Anthropic API-nøkkel |
| `SENDGRID_API_KEY` | SendGrid API-nøkkel (kun hvis e-post ønskes) |
| `SENDGRID_FROM` | Avsender-e-post verifisert i SendGrid |
| `SENDGRID_TO` | Mottaker(e), kommaseparert |

### 4. Aktiver GitHub Pages (valgfritt)

Gå til **Settings → Pages** og velg `main`-branchen som kilde. Nyhetsbrevet blir da tilgjengelig på `https://dittbrukernavn.github.io/telecom-digest/Telecom%20Digest.html` og oppdateres automatisk hver morgen.

### 5. Aktiver e-postutsendelse

I `.github/workflows/daily.yml`, fjern kommentarene rundt steget `Send nyhetsbrevet på e-post`.

---

## Manuell kjøring

Du kan trigge en ny utgave manuelt fra **GitHub → Actions → Telecom Digest — Daglig utgave → Run workflow**.

---

## Tilpasning

- **Antall saker:** Endre `ANTALL_SAKER` i `generate_nyheter.py`
- **Tidspunkt:** Endre `cron`-verdien i `daily.yml` (format: UTC-tid)
- **Vinkling:** Endre `SYSTEM_PROMPT` i `generate_nyheter.py` for annen bransje eller geografi
- **Design:** Rediger kun `Telecom Digest.html` — `nyheter.json`-strukturen forblir den samme

---

## Kostnad

| Komponent | Estimat |
|---|---|
| Claude Opus (per utgave) | ~$0.20–0.50 |
| SendGrid (gratis plan) | 100 e-poster/dag gratis |
| GitHub Actions | Gratis for offentlige repo |

---

## Teknisk

- `generate_nyheter.py` bruker Claude med `web_search`-tool for å søke autonomt
- Claude returnerer strukturert JSON — ikke HTML — for konsistent output
- `Telecom Digest.html` bruker `fetch()` for å laste JSON dynamisk
- `send_email.py` renderer HTML med inline CSS for e-postklient-kompatibilitet
