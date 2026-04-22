#!/usr/bin/env python3
"""
generate_nyheter.py
-------------------
Søker etter dagens telecom-nyheter via Claude (med web search),
og skriver resultatet til nyheter.json — klar til rendering i Telecom Digest.html.

Krav:
    pip install anthropic

Miljøvariabler:
    ANTHROPIC_API_KEY   — din Anthropic API-nøkkel

Kjøring:
    python generate_nyheter.py
"""

import os
import json
import datetime
import anthropic

# ── Konfigurasjon ──────────────────────────────────────────────
MODEL = "claude-opus-4-5"          # Bruk Opus for best journalistisk kvalitet
OUTPUT_FILE = "nyheter.json"
ANTALL_SAKER = 5                   # Antall nyheter per utgave
# ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Du er redaktør for Telecom Digest, et daglig norsk B2B-nyhetsbrev rettet mot profesjonelle i telecom-industrien i Norge.

Din oppgave:
1. Søk etter de viktigste telecom-nyhetene fra de siste 2-3 dagene
2. Vurder relevansen for norsk telecom — ikke bare norske nyheter, men globale trender som påvirker Norge
3. Skriv profesjonelle, faktabaserte sammendrag på norsk bokmål
4. Returner ALLTID kun gyldig JSON — ingen annen tekst, ingen markdown-blokker

Kriterier for nyhetsutvalgelse:
- Prioriter nyheter med direkte påvirkning på norsk telecom (Telenor, Telia, Ice, Lyse, osv.)
- Inkluder europeiske trender som påvirker norsk regulering, investering eller konkurranse
- Globalteknologiske skifter (5G, fiber, AI i nettverk, satellite broadband)
- M&A, regulering, sikkerhet, infrastruktur
- Unngå rent amerikanske nyheter uten europeisk vinkel

Stil:
- Ingress: én setning som gir hele poenget
- Body: 3 avsnitt med kontekst, bakgrunn og analyse — ca 80-100 ord per avsnitt
- Sitat: direkte sitat fra kilden hvis mulig, ellers et representativt synspunkt
- Relevans: konkret analyse av hvorfor dette betyr noe for norsk telecom spesifikt

JSON-format (returner KUN dette, ingen annen tekst):
{
  "dato": "DD. Måned ÅÅÅÅ",
  "ukedag": "Mandag",
  "vol": "01",
  "nr": "01",
  "saker": [
    {
      "kilde": "Kildenavn",
      "dato": "DD. Måned ÅÅÅÅ",
      "headline": "Tittel på nyheten",
      "ingress": "Én setning som oppsummerer hele saken.",
      "body": [
        "Første avsnitt med kontekst og hva som skjedde.",
        "Andre avsnitt med bakgrunn og detaljer.",
        "Tredje avsnitt med analyse og konsekvenser."
      ],
      "sitat": "«Direkte sitat fra kilden eller en relevant aktør.»",
      "relevans": "Konkret analyse av norsk relevans i 2-3 setninger."
    }
  ]
}"""

def get_today_metadata():
    """Returnerer metadata for dagens utgave."""
    now = datetime.datetime.now()
    
    norske_ukedager = {
        0: "Mandag", 1: "Tirsdag", 2: "Onsdag",
        3: "Torsdag", 4: "Fredag", 5: "Lørdag", 6: "Søndag"
    }
    norske_måneder = {
        1: "Januar", 2: "Februar", 3: "Mars", 4: "April",
        5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    
    return {
        "dato_str": f"{now.day}. {norske_måneder[now.month]} {now.year}",
        "ukedag": norske_ukedager[now.weekday()],
        "uke": now.strftime("%U"),
        "år": str(now.year)
    }

def generate_nyheter():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY er ikke satt. Eksporter API-nøkkelen din.")

    client = anthropic.Anthropic(api_key=api_key)
    meta = get_today_metadata()

    print(f"Genererer Telecom Digest for {meta['dato_str']}...")

    user_message = f"""Dagens dato er {meta['dato_str']} ({meta['ukedag']}).

Søk etter de {ANTALL_SAKER} viktigste telecom-nyhetene fra de siste 2-3 dagene.
Prioriter nyheter med relevans for norsk og europeisk telecom-industri.

Metadata for denne utgaven:
- dato: "{meta['dato_str']}"
- ukedag: "{meta['ukedag']}"
- vol: "01"
- nr: "{meta['uke']}"

Returner KUN gyldig JSON i formatet beskrevet i systemprompten. Ingen annen tekst."""

    # Kall Claude med web search aktivert
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user_message}]
    )

    # Hent ut JSON-teksten fra responsen
    json_text = None
    for block in response.content:
        if block.type == "text":
            json_text = block.text.strip()
            break

    if not json_text:
        raise ValueError("Claude returnerte ingen tekst. Prøv igjen.")

    # Rens bort eventuelle markdown-blokker
    if json_text.startswith("```"):
        lines = json_text.split("\n")
        json_text = "\n".join(lines[1:-1])

    # Parse og valider JSON
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        print("Råtekst fra Claude:")
        print(json_text[:500])
        raise ValueError(f"Ugyldig JSON fra Claude: {e}")

    # Skriv til fil
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    antall = len(data.get("saker", []))
    print(f"✓ Ferdig! {antall} saker skrevet til {OUTPUT_FILE}")
    print(f"  Dato: {data.get('dato')}")
    for i, s in enumerate(data.get("saker", []), 1):
        print(f"  {i}. [{s.get('kilde')}] {s.get('headline')}")

if __name__ == "__main__":
    generate_nyheter()
