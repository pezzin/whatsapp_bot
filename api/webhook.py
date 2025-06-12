from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse

app = FastAPI()

RESPONSE_MAP = {
    "check-in": "Il check-in è disponibile dalle ore 14:00. Il check-out entro le 10:00.",
    "colazione": "La colazione viene servita dalle 7:30 alle 10:00 nella sala principale.",
    "parcheggio": "Il parcheggio è gratuito per tutti gli ospiti e non richiede prenotazione.",
    "animazione": "L'animazione per bambini è attiva ogni giorno dalle 10:00 alle 12:00 e dalle 15:00 alle 18:00."
}

@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    user_msg = Body.strip().lower()
    sender = From

    reply = RESPONSE_MAP.get(user_msg, "Mi dispiace, non ho capito. Scrivi ad esempio 'check-in', 'colazione' o 'parcheggio'.")
    print(f"Messaggio da {sender}: {user_msg} → Risposta: {reply}")

    return PlainTextResponse(content=reply)
