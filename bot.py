# BOT 2 - Ration / Aadhar / Mobile - FIXED
# Har line chhoti rakhi hai taaki GitHub me toot na jaye
# Commands: /ration /aadhar /mobile /add

import telebot
from telebot import types
import base64
import re
import os
import threading
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

def _keep():
    try:
        port = int(os.environ.get('PORT', 10000))
        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Bot is Live')
            def log_message(self, *a):
                pass
        HTTPServer(('0.0.0.0', port), H).serve_forever()
    except Exception:
        pass
threading.Thread(target=_keep, daemon=True).start()

TOKEN = os.environ.get('BOT_TOKEN', 'TOKEN')
bot = telebot.TeleBot(TOKEN)

SEARCH = 'https://nfsa.up.gov.in/Food/citizen/NFSASearch.aspx'
BASE = 'https://nfsa.up.gov.in/Food/TrackingRationCard/'
BASE = BASE + 'ViewRC.aspx?Details='

MAP = {
    '123456789012': {
        'rc': '0915500813140750',
        'aadhar': '123456789012',
        'mobile': '9876543210',
    },
}

def find_aadhar(a):
    for r, d in MAP.items():
        if d.get('aadhar') == a:
            return r, d
    return None, None

def find_mobile(mo):
    for r, d in MAP.items():
        if d.get('mobile') == mo:
            return r, d
    return None, None

def make_url(ration_no, rc_id):
    raw = rc_id + '#00002103#' + ration_no
    det = base64.b64encode(raw.encode()).decode()
    return BASE + det

def send_slip(chat_id, label, value, ration_no, rc_id):
    url = make_url(ration_no, rc_id)
    msg = '✅ राशन कार्ड मिल गया!\n\n'
    msg = msg + '🆔 ' + label + ': ' + value + '\n'
    msg = msg + '🆔 कार्ड नंबर: ' + ration_no + '\n\n'
    msg = msg + '👇 नीचे बटन दबाकर PDF देखो:'
    mk = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        '📄 राशन कार्ड देखें / Print PDF',
        url=url,
    )
    mk.add(btn)
    bot.send_message(chat_id, msg, reply_markup=mk)

def send_search(chat_id, label, value, mode):
    msg = '🆔 ' + label + ': ' + value + '\n\n'
    msg = msg + '👇 बटन दबाओ, Chrome me kholo:\n'
    msg = msg + '1. ' + mode + ' चुनो\n'
    msg = msg + '2. यही नंबर डालो\n'
    msg = msg + '3. Captcha डालकर Search दबाओ\n\n'
    msg = msg + 'Usi ki asli slip khulegi.'
    mk = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        '🔍 ' + mode + ' से स्लिप खोलो',
        url=SEARCH,
    )
    mk.add(btn)
    bot.send_message(chat_id, msg, reply_markup=mk)

@bot.message_handler(commands=['start'])
def start(m):
    t = 'नमस्ते! राशन स्लिप 3 तरीके से:\n\n'
    t = t + '/ration 123456789012\n'
    t = t + '/aadhar 123456789012\n'
    t = t + '/mobile 9876543210'
    bot.send_message(m.chat.id, t)

@bot.message_handler(commands=['ration'])
def ration_cmd(m):
    p = m.text.split()
    if len(p) < 2:
        bot.send_message(m.chat.id, '/ration 123456789012')
        return
    no = p[1].strip()
    if not re.fullmatch(r'\d{12}', no):
        bot.send_message(m.chat.id, '❌ 12 अंक का नंबर भेजें')
        return
    bot.send_message(m.chat.id, 'खोजा जा रहा है...')
    d = MAP.get(no)
    if d:
        send_slip(m.chat.id, 'कार्ड नंबर', no, no, d['rc'])
    else:
        send_search(m.chat.id, 'कार्ड नंबर', no, 'Ration by Number')

@bot.message_handler(commands=['aadhar'])
def aadhar_cmd(m):
    p = m.text.split()
    if len(p) < 2:
        bot.send_message(m.chat.id, '/aadhar 123456789012')
        return
    no = p[1].strip()
    if not re.fullmatch(r'\d{12}', no):
        bot.send_message(m.chat.id, '❌ 12 अंक का आधार भेजें')
        return
    bot.send_message(m.chat.id, 'आधार से खोजा जा रहा है...')
    r, d = find_aadhar(no)
    if d:
        send_slip(m.chat.id, 'आधार नंबर', no, r, d['rc'])
    else:
        send_search(m.chat.id, 'आधार नंबर', no, 'Ration by Aadhar')

@bot.message_handler(commands=['mobile'])
def mobile_cmd(m):
    p = m.text.split()
    if len(p) < 2:
        bot.send_message(m.chat.id, '/mobile 9876543210')
        return
    no = p[1].strip()
    if not re.fullmatch(r'\d{10}', no):
        bot.send_message(m.chat.id, '❌ 10 अंक का मोबाइल भेजें')
        return
    bot.send_message(m.chat.id, 'मोबाइल से खोजा जा रहा है...')
    r, d = find_mobile(no)
    if d:
        send_slip(m.chat.id, 'मोबाइल नंबर', no, r, d['rc'])
    else:
        send_search(m.chat.id, 'मोबाइल नंबर', no, 'Ration by Mobile')

@bot.message_handler(commands=['add'])
def add_cmd(m):
    p = m.text.split()
    if len(p) < 5:
        t = '/add <ration> <aadhar> <mobile> <RC_ID>'
        bot.send_message(m.chat.id, t)
        return
    r = p[1].strip()
    a = p[2].strip()
    mo = p[3].strip()
    rc = p[4].strip()
    ok = True
    if not re.fullmatch(r'\d{12}', r):
        ok = False
    if not re.fullmatch(r'\d{12}', a):
        ok = False
    if not re.fullmatch(r'\d{10}', mo):
        ok = False
    if not re.fullmatch(r'\d{16}', rc):
        ok = False
    if not ok:
        bot.send_message(m.chat.id, '❌ Format galat hai')
        return
    MAP[r] = {'rc': rc, 'aadhar': a, 'mobile': mo}
    t = '✅ Save ho gaya!\n\n'
    t = t + '/ration ' + r + '\n'
    t = t + '/aadhar ' + a + '\n'
    t = t + '/mobile ' + mo
    bot.send_message(m.chat.id, t)

@bot.message_handler(func=lambda m: True)
def anything(m):
    t = '/ration 123456789012\n'
    t = t + '/aadhar 123456789012\n'
    t = t + '/mobile 9876543210'
    bot.send_message(m.chat.id, t)

print('Bot 2 chal raha hai...')
bot.infinity_polling()
