
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
SITE_URL = "https://bude404-ops.github.io/Lil-Omnis/"

API = f"https://api.telegram.org/bot{TOKEN}"

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
        "question": "I keep records across many computers, without one central bookkeeper. What am I?",
        "answers": ["blockchain", "a blockchain", "distributed ledger"],
        "hint": "Think of the shared record behind crypto transactions."
    },
    {
        "question": "Six realms, one connected mystery. What collection is this archive about?",
        "answers": ["lil omnis", "the lil omnis", "omnis"],
        "hint": "The answer is the name of this collection."
    },
    {
        "question": "I can live in a digital wallet and represent unique digital art. What am I?",
        "answers": ["nft", "an nft", "collectible"],
        "hint": "Three letters: N, F, T."
    }
]

pending = {}

def telegram(method, data=None):
    if not TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN secret.")
    payload = json.dumps(data or {}).encode()
    request = urllib.request.Request(
        f"{API}/{method}",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        return json.loads(response.read().decode())

def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
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
    for chapter, chain in REALMS:
        lines.append(f"{chapter} — {chain}")
    lines += ["", "Six chapters. 111 collectibles per realm. 666 in all."]
    send(chat_id, "\n".join(lines), menu())

def show_archive(chat_id):
    send(
        chat_id,
        "📜 THE HIDDEN ARCHIVE\n\n"
        "Fragment 001: Echoes\n\n"
        "Six gates stand apart, yet their echoes share one origin. "
        "Cross each threshold, gather what was hidden, and the pattern "
        "may reveal itself.\n\n"
        "The archive is only beginning...",
        menu()
    )

def give_riddle(chat_id):
    index = int(datetime.now().strftime("%j")) % len(RIDDLES)
    riddle = RIDDLES[index]
    pending[chat_id] = riddle
    send(
        chat_id,
        "🧩 ARCHIVE RIDDLE\n\n" + riddle["question"] +
        "\n\nReply with your answer, or type /hint.",
        [[{"text": "💡 Hint", "callback_data": "hint"}],
         [{"text": "🏛️ Main Menu", "callback_data": "menu"}]]
    )

def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    command = text.split()[0].lower().split("@")[0] if text else ""

    if command == "/start":
        send(
            chat_id,
            "🌌 Welcome to the LIL OMNIS ARCHIVE.\n\n"
            "Six realms. Six hidden histories. One mystery connecting them all.\n\n"
            "Explore the realms, solve riddles, and uncover fragments of the archive.",
            menu()
        )
    elif command == "/help":
        send(chat_id, "Commands:\n/start\n/realms\n/riddle\n/hint\n/archive\n/collection", menu())
    elif command == "/realms":
        show_realms(chat_id)
    elif command == "/riddle":
        give_riddle(chat_id)
    elif command == "/hint":
        riddle = pending.get(chat_id)
        send(chat_id, "💡 " + riddle["hint"] if riddle else "Start a riddle first with /riddle.")
    elif command == "/archive":
        show_archive(chat_id)
    elif command == "/collection":
        send(chat_id, "Explore the Lil Omnis collection:\n" + SITE_URL, menu())
    elif text and chat_id in pending and not command.startswith("/"):
        answer = text.lower().strip(" .!?")
        if answer in pending[chat_id]["answers"]:
            pending.pop(chat_id, None)
            send(chat_id, "✨ Correct! You uncovered a fragment of the archive.\n\nMore secrets await. Try /riddle again.", menu())
        else:
            send(chat_id, "Not quite, seeker. Try again, or type /hint.")
    else:
        send(chat_id, "The archive awaits. Choose a path below or type /help.", menu())

def main():
    print("Lil Omnis Archive bot is starting...")
    offset = None
    while True:
        try:
            data = {"timeout": 30}
            if offset is not None:
                data["offset"] = offset
            result = telegram("getUpdates", data)
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
                elif "callback_query" in update:
                    callback = update["callback_query"]
                    chat_id = callback["message"]["chat"]["id"]
                    choice = callback.get("data", "")
                    telegram("answerCallbackQuery", {"callback_query_id": callback["id"]})
                    if choice == "realms":
                        show_realms(chat_id)
                    elif choice == "riddle":
                        give_riddle(chat_id)
                    elif choice == "archive":
                        show_archive(chat_id)
                    elif choice == "hint":
                        riddle = pending.get(chat_id)
                        send(chat_id, "💡 " + riddle["hint"] if riddle else "Start a riddle first with /riddle.")
                    elif choice == "menu":
                        send(chat_id, "Choose your path through the archive:", menu())
        except Exception as error:
            print("Bot error:", error)
            time.sleep(5)

if __name__ == "__main__":
    main()
