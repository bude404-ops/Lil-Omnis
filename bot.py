
import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
SITE_URL = "https://bude404-ops.github.io/Lil-Omnis/"

if not TOKEN:
    raise RuntimeError("Add TELEGRAM_BOT_TOKEN in Render Environment.")
if not BASE_URL:
    raise RuntimeError("Render did not provide RENDER_EXTERNAL_URL.")

API = f"https://api.telegram.org/bot{TOKEN}"
pending = {}

REALMS = [
    ("Chapter I", "Ethereum"),
    ("Chapter II", "Base"),
    ("Chapter III", "Robinhood Chain"),
    ("Chapter IV", "BNB Chain"),
    ("Chapter V", "Solana"),
    ("Chapter VI", "Sui"),
]

RIDDLES = [
    ("Many computers share my records. What am I?",
     ["blockchain", "a blockchain", "distributed ledger"],
     "Think of the shared record behind crypto."),
    ("Six realms, one mystery. What collection is this?",
     ["lil omnis", "the lil omnis", "omnis"],
     "The answer is the collection's name."),
    ("I represent unique digital art in a wallet. What am I?",
     ["nft", "an nft", "collectible"],
     "Three letters: N, F, T."),
]

def telegram(method, data=None):
    request = urllib.request.Request(
        f"{API}/{method}",
        data=json.dumps(data or {}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.loads(response.read().decode())
    if not result.get("ok"):
        raise RuntimeError(str(result))
    return result["result"]

def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = {"inline_keyboard": keyboard}
    telegram("sendMessage", data)

def menu():
    return [
        [{"text": "🌌 Explore Six Realms", "callback_data": "realms"}],
        [{"text": "🧩 Solve a Riddle", "callback_data": "riddle"}],
        [{"text": "📜 Hidden Archive", "callback_data": "archive"}],
        [{"text": "🖼️ Collection Website", "url": SITE_URL}],
    ]

def realms(chat_id):
    lines = ["🌌 THE SIX REALMS", ""]
    lines.extend(f"{chapter} — {chain}" for chapter, chain in REALMS)
    lines += ["", "111 collectibles per realm. 666 in all."]
    send(chat_id, "\n".join(lines), menu())

def archive(chat_id):
    send(
        chat_id,
        "📜 THE HIDDEN ARCHIVE\n\n"
        "FRAGMENT 001: ECHOES\n\n"
        "Six gates stand apart, yet their echoes share one origin. "
        "Cross each threshold, gather what was hidden, and the pattern "
        "may reveal itself.\n\nThe archive is only beginning...",
        menu()
    )

def riddle(chat_id):
    import datetime
    question, answers, hint = RIDDLES[
        datetime.date.today().timetuple().tm_yday % len(RIDDLES)
    ]
    pending[chat_id] = (answers, hint)
    send(
        chat_id,
        "🧩 ARCHIVE RIDDLE\n\n" + question +
        "\n\nReply with your answer or type /hint.",
        [[{"text": "💡 Hint", "callback_data": "hint"}],
         [{"text": "🏛️ Main Menu", "callback_data": "menu"}]]
    )

def message_handler(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    command = text.split()[0].lower().split("@")[0] if text else ""

    if command == "/start":
        send(chat_id,
             "🌌 Welcome to the LIL OMNIS ARCHIVE!\n\n"
             "Six realms. Six hidden histories. One connected mystery.\n\n"
             "Choose your path, seeker.",
             menu())
    elif command == "/help":
        send(chat_id, "Commands: /start /realms /riddle /hint /archive /collection", menu())
    elif command == "/realms":
        realms(chat_id)
    elif command == "/riddle":
        riddle(chat_id)
    elif command == "/hint":
        item = pending.get(chat_id)
        send(chat_id, "💡 " + item[1] if item else "Start with /riddle.")
    elif command == "/archive":
        archive(chat_id)
    elif command == "/collection":
        send(chat_id, "Explore the collection:\n" + SITE_URL, menu())
    elif text and chat_id in pending and not command.startswith("/"):
        answer = text.lower().strip(" .!?")
        if answer in pending[chat_id][0]:
            pending.pop(chat_id, None)
            send(chat_id, "✨ Correct, seeker! You uncovered a fragment.\n\nTry /riddle for another mystery.", menu())
        else:
            send(chat_id, "Not quite. Try again, or type /hint.")
    else:
        send(chat_id, "The archive awaits. Choose a path below or type /help.", menu())

def handle_update(update):
    if "message" in update:
        message_handler(update["message"])
    elif "callback_query" in update:
        callback = update["callback_query"]
        telegram("answerCallbackQuery", {"callback_query_id": callback["id"]})
        chat_id = callback["message"]["chat"]["id"]
        choice = callback.get("data", "")
        if choice == "realms":
            realms(chat_id)
        elif choice == "riddle":
            riddle(chat_id)
        elif choice == "archive":
            archive(chat_id)
        elif choice == "hint":
            item = pending.get(chat_id)
            send(chat_id, "💡 " + item[1] if item else "Start with /riddle.")
        elif choice == "menu":
            send(chat_id, "Choose your path through the archive:", menu())

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"Lil Omnis Archive is online."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/telegram-webhook":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            update = json.loads(self.rfile.read(length))
            handle_update(update)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as error:
            print("Webhook error:", error)
            self.send_response(500)
            self.end_headers()

    def log_message(self, format, *args):
        print(format % args)

print("Registering Telegram webhook...")
telegram("setWebhook", {
    "url": BASE_URL + "/telegram-webhook",
    "drop_pending_updates": False
})

port = int(os.environ.get("PORT", "10000"))
server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
print(f"Lil Omnis Archive listening on port {port}")
server.serve_forever()
