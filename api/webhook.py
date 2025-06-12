from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
import requests
import os

app = FastAPI()

# Risposte predefinite simulate (puoi estendere o caricare da file JSON)
RESPONSE_MAP = {
    "check-in": "Il check-in è disponibile dalle ore 14:00. Il check-out entro le 10:00.",
    "colazione": "La colazione viene servita dalle 7:30 alle 10:00 nella sala principale.",
    "parcheggio": "Il parcheggio è gratuito per tutti gli ospiti e non richiede prenotazione.",
    "animazione": "L'animazione per bambini è attiva ogni giorno dalle 10:00 alle 12:00 e dalle 15:00 alle 18:00."
}

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HUGGINGFACE_TOKEN = os.getenv("HF_API_TOKEN")


def ask_huggingface(question: str) -> str:
    if not HUGGINGFACE_TOKEN:
        print("[ERRORE] Token Hugging Face mancante.")
        return "Errore di configurazione: token AI mancante."

    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    prompt = (
        "Sei un receptionist dell'hotel Eurhotel di Rimini. "
        "Offrite camere familiari, animazione per bambini, piscina, e colazione inclusa. "
        "Rispondi in italiano in modo educato e pratico alla seguente domanda del cliente:\n"
        f"{question}\nRisposta:"
    )
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }
    try:
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
        print(f"[DEBUG] Status Code: {response.status_code}")
        print(f"[DEBUG] Raw text response: {response.text}")

        if response.status_code != 200:
            return "Il nostro assistente AI è momentaneamente non disponibile."

        result = response.json()
        print("[DEBUG] Risposta Hugging Face (parsed):", result)

        if isinstance(result, list) and "generated_text" in result[0]:
            raw_text = result[0]["generated_text"]
            clean_reply = raw_text.split("Risposta:", 1)[-1].strip()
            return clean_reply
        elif isinstance(result, dict) and "error" in result:
            return "Il nostro assistente è momentaneamente non disponibile."

        return "Risposta non riconosciuta dal modello."

    except Exception as e:
        print(f"[ERRORE] Eccezione AI: {str(e)}")
        return f"Errore nell'assistente AI: {str(e)}"


@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    user_msg = Body.strip().lower()
    sender = From

    if user_msg in RESPONSE_MAP:
        reply = RESPONSE_MAP[user_msg]
    else:
        print(f"[NLP] Nessuna keyword trovata, invio a Hugging Face: {user_msg}")
        reply = ask_huggingface(user_msg)

    print(f"Messaggio da {sender}: {user_msg} → Risposta: {reply}")

    return PlainTextResponse(content=reply)

# Per test locale: uvicorn whatsapp_bot:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("whatsapp_bot:app", host="0.0.0.0", port=8000, reload=True)
