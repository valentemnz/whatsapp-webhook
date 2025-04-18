from flask import Flask, request
import os
import requests
from openai import OpenAI

app = Flask(__name__)

# Cliente OpenAI con variable de entorno
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Configuración de WhatsApp
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = "599820413221132"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = "miverificacion"
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == verify_token:
            return challenge, 200
        else:
            return "Token inválido", 403

    if request.method == "POST":
        data = request.get_json()
        try:
            entry = data["entry"][0]["changes"][0]["value"]
            message = entry.get("messages", [])[0]
            text = message["text"]["body"]
            from_number = message["from"]

            print("✅ Mensaje recibido:", text)

            # GPT-3.5-turbo (disponible para todos con API Key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": text}]
            )
            reply = response.choices[0].message.content.strip()

            print("🧠 Respuesta GPT:", reply)

            # Enviar respuesta a WhatsApp
            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "type": "text",
                "text": {"body": reply}
            }

            response_whatsapp = requests.post(url, headers=headers, json=payload)
            print("📤 Respuesta de WhatsApp:", response_whatsapp.status_code, response_whatsapp.text)

        except Exception as e:
            print("❌ ERROR en webhook:", e)

        return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
