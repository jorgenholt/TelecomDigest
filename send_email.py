#!/usr/bin/env python3
"""
send_email.py
─────────────
Sender dagens Telecom Digest som HTML-e-post via SendGrid.
Leser nyheter.json og gjengir den som inline HTML — samme design som nettsiden.

Krav:
    pip install sendgrid

Miljøvariabler:
    SENDGRID_API_KEY   — SendGrid API-nøkkel
    SENDGRID_FROM      — avsender (må være verifisert i SendGrid)
    SENDGRID_TO        — mottaker(e), kommaseparert
"""

import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

NYHETER_FILE = "nyheter.json"

# Inline CSS (e-postklienter støtter ikke <link> eller <style> i <head>)
EMAIL_CSS = """
  body { margin:0; padding:0; background:#E8E6E1; font-family:Georgia,serif; }
  .wrap { max-width:620px; margin:24px auto; background:#FAFAF8; }
  .hdr { padding:28px 36px 20px; border-bottom:2px solid #111; }
  .masthead { font-family:Arial,sans-serif; font-weight:900; font-size:30px;
              letter-spacing:0.04em; text-transform:uppercase; color:#111; }
  .masthead em { color:#C8102E; font-style:normal; }
  .hdr-date { font-family:monospace; font-size:9px; letter-spacing:0.14em;
              color:#888; text-transform:uppercase; float:right; line-height:1.7; }
  .hdr-rule { height:1px; background:#E0DDD8; margin:14px 0; clear:both; }
  .tagline { font-size:13px; font-style:italic; color:#888; }
  .index { padding:16px 36px; background:#F5F4F1; border-bottom:1px solid #E0DDD8; }
  .index-label { font-family:monospace; font-size:9px; letter-spacing:0.2em;
                 color:#C8102E; text-transform:uppercase; margin-bottom:10px; display:block; }
  .index-item { font-size:12px; line-height:1.6; color:#1C1C1C;
                padding:3px 0; border-bottom:1px solid #EDECE9; }
  .index-item span { color:#C8102E; font-family:monospace; font-size:9px;
                     margin-right:10px; }
  .story { padding:28px 36px; border-bottom:1px solid #E0DDD8; }
  .story:last-of-type { border-bottom:2px solid #111; }
  .meta { font-family:monospace; font-size:9px; letter-spacing:0.14em;
          text-transform:uppercase; color:#C8102E; margin-bottom:12px; }
  .meta span { color:#888; margin-left:12px; }
  h2 { font-family:Arial,sans-serif; font-weight:900; font-size:22px;
       line-height:1.1; text-transform:uppercase; color:#111; margin-bottom:8px; }
  .deck { font-size:14px; font-style:italic; color:#555; line-height:1.5;
          margin-bottom:16px; }
  .body-text { font-size:13.5px; line-height:1.75; color:#333; margin-bottom:16px; }
  .body-text p { margin-bottom:10px; }
  .quote { border-left:2px solid #C8102E; padding:12px 16px;
           background:#F5F4F1; margin:16px 0; }
  .quote p { font-size:13px; font-style:italic; color:#444; line-height:1.6; }
  .relevance { border-top:1px solid #E0DDD8; padding-top:12px; margin-top:16px; }
  .rel-label { font-family:monospace; font-size:8px; letter-spacing:0.14em;
               text-transform:uppercase; color:#FAFAF8; background:#111;
               padding:3px 7px; display:inline-block; margin-bottom:8px; }
  .rel-text { font-size:12.5px; color:#555; line-height:1.6; }
  .footer { padding:20px 36px 28px; background:#111; }
  .footer-logo { font-family:Arial,sans-serif; font-weight:900; font-size:16px;
                 text-transform:uppercase; color:#F5F4F1; margin-bottom:12px; }
  .footer-logo em { color:#C8102E; font-style:normal; }
  .footer-sources { font-family:monospace; font-size:9px; color:#444;
                    line-height:1.9; margin-bottom:12px; }
  .footer-disc { font-family:monospace; font-size:8px; color:#333;
                 line-height:1.8; border-top:1px solid #1A1A1A; padding-top:12px; }
"""

def render_html(data):
    saker = data["saker"]
    totalt = len(saker)

    index_html = "\n".join(
        f'<div class="index-item"><span>{str(i+1).zfill(2)}</span>{s["headline"]}</div>'
        for i, s in enumerate(saker)
    )

    stories_html = ""
    for i, s in enumerate(saker):
        body_paras = "".join(f"<p>{p}</p>" for p in s["body"])
        num = f"{str(i+1).zfill(2)} / {str(totalt).zfill(2)}"
        stories_html += f"""
        <div class="story">
          <div class="meta">{s['kilde']}<span>{s['dato']}</span>
            <span style="float:right;color:#E0DDD8;">{num}</span>
          </div>
          <h2>{s['headline']}</h2>
          <p class="deck">{s['ingress']}</p>
          <div class="body-text">{body_paras}</div>
          <div class="quote"><p>{s['sitat']}</p></div>
          <div class="relevance">
            <span class="rel-label">Norsk relevans</span>
            <p class="rel-text">{s['relevans']}</p>
          </div>
        </div>"""

    sources = " · ".join(dict.fromkeys(s["kilde"] for s in saker))

    return f"""<!DOCTYPE html>
<html lang="no">
<head><meta charset="UTF-8"><style>{EMAIL_CSS}</style></head>
<body>
<div class="wrap">
  <div class="hdr">
    <div class="hdr-date">{data['ukedag']}<br>{data['dato']}<br>Vol.{data['vol']} — Nr.{data['nr']}</div>
    <div class="masthead">TELECOM<em>DIGEST</em></div>
    <div class="hdr-rule"></div>
    <p class="tagline">Dagens viktigste telecom-nyheter.</p>
  </div>
  <div class="index">
    <span class="index-label">// Denne utgaven</span>
    {index_html}
  </div>
  {stories_html}
  <div class="footer">
    <div class="footer-logo">TELECOM<em>DIGEST</em></div>
    <div class="footer-sources">Kilder: {sources}</div>
    <div class="footer-disc">
      Dette nyhetsbrevet er en redaksjonell sammenstilling av publiserte nyhetsartikler.
      Innholdet er ment som informasjon, ikke investerings- eller forretningsrådgivning.
    </div>
  </div>
</div>
</body></html>"""

def send():
    api_key  = os.environ["SENDGRID_API_KEY"]
    from_email = os.environ["SENDGRID_FROM"]
    to_emails  = [e.strip() for e in os.environ["SENDGRID_TO"].split(",")]

    with open(NYHETER_FILE, encoding="utf-8") as f:
        data = json.load(f)

    html_content = render_html(data)
    subject = f"Telecom Digest — {data['dato']}"

    for to_email in to_emails:
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"✓ Sendt til {to_email} — status {response.status_code}")

if __name__ == "__main__":
    send()
