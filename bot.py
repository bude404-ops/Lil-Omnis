
import json
import os
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import date

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
SITE_URL = "https://bude404-ops.github.io/Lil-Omnis/"
WEBHOOK_PATH = "/telegram-webhook"

if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in Render Environment.")
if not BASE_URL.startswith("https://"):
    raise RuntimeError("RENDER_EXTERNAL_URL is missing or not HTTPS.")

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
    {
        "question": "Many computers share my records. What am I?",
        "answers": ["blockchain", "a blockchain", "distributed ledger"],
        "hint": "Think of the shared record behind crypto transactions."
    },
    {
        "question": "Six realms, one connected mystery. What collection is this?",
        "answers": ["lil omnis", "the lil omnis", "omnis"],
        "hint": "The answer is the name of this collection."
    },
    {
        "question": "I represent unique digital art in a wallet. What am I?",
        "answers": ["nft", "an nft", "collectible"],
        "hint": "Three letters: N, F, T."
    },
]

def telegram(method, data=None, attempts=3):
    request_data = json.dumps(data or {}).encode()

    for attempt in range(attempts):
        try:
            request = urllib.request.Request(
                f"{API}/{method}",
                data=request_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode())

            if not result.get("ok"):
                raise RuntimeError(
                    f"Telegram {method} error: {result.get('description', 'Unknown error')}"
                )
            return result["result"]

        except (urllib.error.URLError, TimeoutError, OSError) as error:
            print(f"Telegram request {method} failed: {error}")
            if attempt == attempts - 1:
                raise
            time.sleep(2 * (attempt + 1))

def send(chat_id, message, keyboard=None):
    data = {"chat_id": chat_id, "text": message}
    if keyboard:
        data["reply_markup"] = {"inline_keyboard": keyboard}
    telegram("sendMessage", data)

def menu():
    return [
        [{"text": "🌌 Explore the Six Realms", "callback_data": "realms"}],
        [{"text": "🧩 Solve a Riddle", "callback_data": "riddle"}],
        [{"text": "📜 Enter the Archive", "callback_data": "archive"}],
        [{"text": "🖼️ Collection Website", "url": SITE_URL}],
    ]

def show_realms(chat_id):
    lines = ["🌌 THE SIX REALMS", ""]
    lines.extend(f"{chapter} — {chain}" for chapter, chain in REALMS)
    lines += [
        "",
        "Six chapters. 111 collectibles per realm. 666 in all.",
        "Each realm holds a piece of the mystery."
    ]
    send(chat_id, "\n".join(lines), menu())

def show_archive(chat_id):
    send(
        chat_id,
        "📜 THE HIDDEN ARCHIVE\n\n"
        "FRAGMENT 001: ECHOES\n\n"
        "Six gates stand apart, yet their echoes share one origin. "
        "Cross each threshold, gather what was hidden, and the pattern "
        "may reveal itself.\n\n"
        "The archive is only beginning, seeker.",
        menu()
    )

def give_riddle(chat_id):
    index = date.today().timetuple().tm_yday % len(RIDDLES)
    item = RIDDLES[index]
    pending[chat_id] = item

    send(
        chat_id,
        "🧩 ARCHIVE RIDDLE\n\n"
        + item["question"]
        + "\n\nReply with your answer, or tap Hint.",
        [
            [{"text": "💡 Hint", "callback_data": "hint"}],
            [{"text": "🏛️ Main Menu", "callback_data": "menu"}]
        ]
    )

def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    command = text.split()[0].lower().split("@")[0] if text else ""

    if command == "/start":
        send(
            chat_id,
            "🌌 WELCOME TO THE LIL OMNIS ARCHIVE\n\n"
            "Six realms. Six hidden histories. One mystery connecting them all.\n\n"
            "Explore the realms, solve riddles, and uncover fragments of the archive.",
            menu()
        )

    elif command == "/help":
        send(
            chat_id,
            "📖 ARCHIVE COMMANDS\n\n"
            "/start — Open the archive\n"
            "/realms — Explore six realms\n"
            "/riddle — Receive a riddle\n"
            "/hint — Get a clue\n"
            "/archive — Read hidden lore\n"
            "/collection — Visit the collection",
            menu()
        )

    elif command == "/realms":
        show_realms(chat_id)

    elif command == "/riddle":
        give_riddle(chat_id)

    elif command == "/hint":
        item = pending.get(chat_id)
        send(
            chat_id,
            "💡 " + item["hint"] if item else "Start with /riddle first."
        )

    elif command == "/archive":
        show_archive(chat_id)

    elif command == "/collection":
        send(chat_id, "Explore the Lil Omnis collection:\n" + SITE_URL, menu())

    elif text and chat_id in pending and not command.startswith("/"):
        answer = text.lower().strip(" .!?")
        accepted = pending[chat_id]["answers"]

        if answer in accepted:
            pending.pop(chat_id, None)
            send(
                chat_id,
                "✨ CORRECT, SEEKER!\n\n"
                "You uncovered a fragment of the archive. "
                "More secrets await. Try /riddle again.",
                menu()
            )
        else:
            send(chat_id, "Not quite, seeker. Try again or use /hint.")

    else:
        send(chat_id, "The archive awaits. Choose a path below or type /help.", menu())

def handle_update(update):
    if "message" in update:
        handle_message(update["message"])

    elif "callback_query" in update:
        callback = update["callback_query"]
        callback_id = callback["id"]
        chat_id = callback["message"]["chat"]["id"]
        choice = callback.get("data", "")

        try:
            telegram("answerCallbackQuery", {"callback_query_id": callback_id})
        except Exception as error:
            print("Callback acknowledgement failed:", error)

        if choice == "realms":
            show_realms(chat_id)
        elif choice == "riddle":
            give_riddle(chat_id)
        elif choice == "archive":
            show_archive(chat_id)
        elif choice == "hint":
            item = pending.get(chat_id)
            send(
                chat_id,
                "💡 " + item["hint"] if item else "Start with /riddle first."
            )
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
        if self.path != WEBHOOK_PATH:
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
            print("Webhook processing failed:", error)
            try:
                self.send_response(500)
                self.end_headers()
            except OSError:
                pass

    def log_message(self, format, *args):
        print(format % args)

def register_webhook():
    webhook_url = BASE_URL + WEBHOOK_PATH

    while True:
        try:
            print("Registering Telegram webhook...")
            telegram(
                "setWebhook",
                {
                    "url": webhook_url,
                    "allowed_updates": ["message", "callback_query"],
                    "drop_pending_updates": False
                }
            )
            print("Telegram webhook registered successfully.")
            return

        except Exception as error:
            print("Webhook registration failed:", error)
            print("Retrying in 10 seconds...")
            time.sleep(10)

def main():
    port = int(os.environ.get("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)

    print(f"Lil Omnis Archive listening on port {port}")

    import threading
    threading.Thread(target=register_webhook, daemon=True).start()

    server.serve_forever()

if __name__ == "__main__":
    main()
