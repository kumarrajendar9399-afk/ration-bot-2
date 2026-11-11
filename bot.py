# RATION BOT 2 - Ration / Aadhar / Mobile - FINAL
# Pehle wale bot ko mat chhedo, ye ALAG bot hai, ALAG repo / ALAG Render service me chalega.
#
# Sach baat (Example jaisa hi):
# ViewRC ki lambi Details = base64( RC_ID + "#" + "00002103" + "#" + RATION_NO )
# Ration No se RC_ID nahi ban sakta. Aadhar / Mobile se bhi seedha RC_ID nahi ban sakta.
# Isliye is bot me 2 tareeke hain:
# 1) Agar number MAP me save hai -> seedha ViewRC wali slip (Example jaisi) khulegi
# 2) Agar MAP me nahi hai -> bot official NFSASearch page ka button dega,
#    wahan Ration / Aadhar / Mobile chun kar + Captcha daal kar slip khulegi.
# Apna data MAP me ek baar daal do, phir teeno se seedhi slip khulegi.
# Example me sirf 123456789 jaisi dummy numbers hain.
#
# Commands:
# /ration 123456789012
# /aadhar 123456789012
# /mobile 9876543210
# /add 123456789012 123456789012 9876543210 0915500813140750
#      ^ration_no  ^aadhar_no  ^mobile  ^RC_ID(16 digit)

import telebot
from telebot import types
import base64, re, os, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
def _keep_alive():
    try:
        port = int(os.environ.get('PORT', 10000))
        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.end_headers(); self.wfile.write(b'Bot is Live')
            def log_message(self, *a): pass
        HTTPServer(('0.0.0.0', port), H).serve_forever()
    except Exception: pass
threading.Thread(target=_keep_alive, daemon=True).start()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "APNA_NAYE_BOT_KA_TOKEN_YAHAN_DAALO")
bot = telebot.TeleBot(BOT_TOKEN)

SEARCH_URL = "https://nfsa.up.gov.in/Food/citizen/NFSASearch.aspx"

# ===== APNA DATA YAHAN DAALO - Ek baar daal do, phir teeno se slip khulegi =====
# Format: "RATION_NO": {"rc": "RC_ID 16 digit", "aadhar": "12 digit", "mobile": "10 digit"}
# Neeche wali line sirf example hai, apna asli data iski jagah likho.
MAP = {
    "123456789012": {"rc": "0915500813140750", "aadhar": "123456789012", "mobile": "9876543210"},
}
# Aadhar / Mobile se Ration dhoondhne ke liye ulta map auto ban jayega
def find_by_aadhar(aadhar):
    for r, d in MAP.items():
        if d.get("aadhar") == aadhar:
            return r, d
    return None, None
def find_by_mobile(mobile):
    for r, d in MAP.items():
        if d.get("mobile") == mobile:
            return r, d
    return None, None

def viewrc_url(ration_no, rc_id):
    raw = f"{rc_id}#00002103#{ration_no}"
    details = base64.b64encode(raw.encode()).decode()
    return f"https://nfsa.up.gov.in/Food/TrackingRationCard/ViewRC.aspx?Details={details}"

def send_viewrc(chat_id, label, value, ration
