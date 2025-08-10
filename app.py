import os, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "miclave123")
GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v20.0")
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"

def send_text(to_e164: str, body: str):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product":"whatsapp",
        "to": to_e164,
        "type":"text",
        "text":{"body": body[:4096]}
    }
    r = requests.post(GRAPH_URL, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

@app.get("/")
def health(): return "OK", 200

# Verificación webhook
@app.get("/webhook")
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# Recepción de mensajes
@app.post("/webhook")
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages: return jsonify({"status":"no message"}), 200

        msg = messages[0]
        wa_from = msg["from"]
        mtype = msg.get("type","text")

        if mtype == "text":
            user_text = msg["text"]["body"].strip()
        elif mtype == "interactive":
            i = msg["interactive"]
            user_text = i["button_reply"]["title"] if i.get("type")=="button_reply" else i["list_reply"]["title"]
        else:
            user_text = "(no-texto)"

        reply = f"Recibí: {user_text}\nBot de prueba ✅"
        send_text(wa_from, reply)

    except Exception as e:
        print("ERR webhook:", e)
    return jsonify({"status":"ok"}), 200

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",5000)))
