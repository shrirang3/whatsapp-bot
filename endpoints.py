from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
from coversation_history import process_number
from utils import send_conversation, send_wati_message_alternative

app = FastAPI()

@app.post("/webhook")
async def webhook_handler(request: Request):
    """
    Main webhook entrypoint.
    For each phone_number:
      - get conversation history
      - send to chat API
      - forward reply to WhatsApp
    """
    body = await request.json()
    phone_number = body.get("phone_number")

    if not phone_number:
        return JSONResponse({"success": False, "error": "phone_number required"}, status_code=400)

    # Step 1: Fetch conversation history
    conversation_json, _ = process_number(phone_number)
    if not conversation_json:
        return JSONResponse({"success": False, "error": "No conversation found"}, status_code=404)

    # Step 2: Send conversation to chat API
    chat_response = send_conversation(conversation_json, phone_number=phone_number)
    if not chat_response.get("success"):
        return JSONResponse({"success": False, "error": "Chat API failed", "chat_response": chat_response})

    # Step 3: Extract bot reply
    bot_reply = chat_response.get("message", "Thank you for contacting us.")
    if isinstance(bot_reply, dict):
        bot_reply = bot_reply.get("content", "Thank you for contacting us.")

    # Step 4: Send reply to WATI (WhatsApp)
    wati_response = send_wati_message_alternative(phone_number, bot_reply)

    return JSONResponse({
        "success": True,
        "chat_response": chat_response,
        "bot_reply": bot_reply,
        "wati_response": wati_response
    })
