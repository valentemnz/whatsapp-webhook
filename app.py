from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        print("✅ Verificación recibida en servidor de Render")
        verify_token = "miverificacion"
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        print(f"🔍 mode={mode}, token={token}, challenge={challenge}")
        if mode == "subscribe" and token == verify_token:
            print("🎉 Webhook verificado exitosamente desde Meta.")
            return challenge, 200
        else:
            print("❌ Token de verificación inválido.")
            return "Token inválido", 403
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
