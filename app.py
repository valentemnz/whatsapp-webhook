from flask import Flask, request
import requests
import openai
import os

app = Flask(__name__)

# Configura tu clave de OpenAI aquí
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Token y número configurado en tu app de Meta
WHATSAPP_TOKEN = "EAAU4xPS3ZCx8BO56nb1HRQdMljcA9OtxLekUxIXMwb0ZAynKkJB6PbBBTiyS2j6kXsoJjoob7b1X9sOtcpT5rxAReZAbduA2RRK83L4sgZCVyRb2LyZBk0vW6XOpZCSZBM1OAG98C83e5dEU9YRPCGCC3yuhK3ZC3QR7cvQ8erZCkS9WrmGKl4NmlPRqsdBZCFl6ZBRTkz3ldbK2ZC5lQAJCaYU0A4Ul6cAZD"
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

            # Consulta a ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": text}]
            )
            reply = response.choices[0].message["content"]

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
            requests.post(url, headers=headers, json=payload)

        except Exception as e:
            print("❌ ERROR en webhook:", e)

        return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
