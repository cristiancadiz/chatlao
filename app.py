import os
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "clave123"  # Debe ser igual al que pones en Meta

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Validación del token para Meta
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Token inválido", 403

    elif request.method == "POST":
        # Aquí se reciben los mensajes de WhatsApp
        data = request.get_json()
        print(data)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
#
