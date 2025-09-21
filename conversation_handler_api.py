from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import json
from coversation_history import process_number   # <-- import your first file
import time
import re
import os
import csv


# -------------------------
# CONFIG
# -------------------------
CHAT_API_URL = "bot_api_url"   # Your RAG bot API
WATI_API_BASE = "wati_base"   # Your WATI base
WATI_TOKEN = "wati_token"
  # Make sure this is your complete token


CHAT_HEADERS = {
    "Content-Type": "application/json"
}
WATI_HEADERS = {
    "Authorization": f"Bearer {WATI_TOKEN}",
    "Content-Type": "application/json"
}


def save_conversation_to_csv(phone_number: str, messages: list, output_file="conversations.csv"):
    """
    Save phone number and filtered messages JSON into a CSV file.
    If file doesn't exist, create it with headers.
    """
    row = {
        "phone_number": phone_number,
        "messages": json.dumps(messages, ensure_ascii=False)  # store as JSON string
    }

    file_exists = os.path.isfile(output_file)

    with open(output_file, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["phone_number", "messages"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"💾 Saved conversation for {phone_number} with {len(messages)} messages into {output_file}")


def send_conversation(conversation_json, phone_number=None):
    """
    MODIFIED FUNCTION
    Finds the first "Congratulations!" assistant template message
    and sends only the messages that came BEFORE it.
    """
    if not conversation_json or "messages" not in conversation_json:
        raise ValueError("Invalid conversation_json format")

    all_messages = conversation_json.get("messages", [])

    # --- REFINED LOGIC START ---
    target_content_snippet = "Congratulations! Aap *Swiggy Instamart Delivery Partner* job ke liye shortlist hue hain."
    
    template_index = -1
    # Search from TOP to bottom: stop at the FIRST matching template
    for i, msg in enumerate(all_messages):
        role = msg.get("role", "").lower()
        content = msg.get("content", "")
        
        if role == "assistant" and target_content_snippet in content:
            template_index = i
            break  # stop at the first template block
    
    # Slice the list to get only messages BEFORE the template
    if template_index != -1:
        messages_to_send = all_messages[:template_index]
        print(f"✅ Found template message at index {template_index}. Sending {len(messages_to_send)} message(s) that came BEFORE it.")
    else:
        # Fallback: If the template is not found, send the whole history
        messages_to_send = all_messages
        print("⚠️ Template message not found. Sending full conversation history as a fallback.")
    # --- REFINED LOGIC END ---

    if not messages_to_send:
        print("✅ No messages found before the template. Nothing to send.")
        return {"success": False, "message": "No messages to process."}

    # Build the payload with the filtered messages
    payload = {"messages": []}
    if phone_number:
        payload["phone_number"] = str(phone_number)

    for msg in messages_to_send:
        role = msg.get("role", "").lower()
        if role not in ["user", "assistant"]:
            continue

        payload["messages"].append({
            "role": role,
            "content": msg.get("content", ""),
            "timestamp": msg.get("timestamp")
        })
    # After payload is created:
    save_conversation_to_csv(phone_number, payload["messages"])
    print(f"📤 Sending payload with {len(payload['messages'])} message(s) to /chat API:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = requests.post(CHAT_API_URL, headers=CHAT_HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error sending conversation: {e}")
        return {"success": False, "error": str(e)}



def split_message_into_chunks(message: str, max_sentences: int = 2):
    """
    Split message into chunks of 1–2 sentences each.
    """
    # Split into sentences using regex for ., !, ?
    sentences = re.split(r'(?<=[.!?])\s+', message.strip())
    chunks = []

    # Group sentences into chunks of max_sentences
    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i:i+max_sentences]).strip()
        if chunk:
            chunks.append(chunk)
    
    return chunks


def send_wati_message_alternative(phone_number: str, message: str, delay_seconds: int = 1):
    """
    Alternative method using form data instead of JSON
    Splits message into smaller chunks and sends sequentially.
    """
    message = str(message).strip()
    if not message:
        return {"result": False, "error": "Message is empty"}
    
    url = f"{WATI_API_BASE}/sendSessionMessage/{phone_number}"
    headers_form = {"Authorization": f"Bearer {WATI_TOKEN}"}

    # Split into smaller chunks
    chunks = split_message_into_chunks(message)
    results = []

    for idx, chunk in enumerate(chunks, start=1):
        data = {"messageText": chunk}
        print(f"📤 Sending part {idx}/{len(chunks)}: {chunk}")

        try:
            response = requests.post(url, headers=headers_form, data=data, timeout=30)
            print(f"📤 Status: {response.status_code}, Response: {response.text}")
            
            if response.status_code == 200:
                results.append(response.json())
            else:
                results.append({"result": False, "error": f"HTTP {response.status_code}: {response.text}"})
            
        except Exception as e:
            print(f"❌ Error sending part {idx}: {e}")
            results.append({"result": False, "error": str(e)})

        # Add a delay between messages (to avoid rate limiting)
        time.sleep(delay_seconds)

    return results



if __name__ == "__main__":
    phone_number = "919550822097"

    # Step 1: Fetch conversation history
    conversation_json, _ = process_number(phone_number)

    if conversation_json:
        # Step 2: Send to /chat API
        chat_response = send_conversation(conversation_json, phone_number=phone_number)
        print("✅ Chat API Response:")
        print(json.dumps(chat_response, indent=2, ensure_ascii=False))

        # Step 3: Extract bot message and forward to WhatsApp
        if chat_response.get("success"):
            bot_reply = chat_response.get("message", "Thank you for contacting us.")
            
            if isinstance(bot_reply, dict):
                bot_reply = bot_reply.get("content", "Thank you for contacting us.")

            print(f"🔍 Bot reply to send: {repr(bot_reply)}")
            print(f"🔍 Bot reply length: {len(bot_reply)}")
            print(f"🔍 Phone number: {phone_number}")


            print("\n🔄 Trying alternative form data method...")
            wati_response_alt = send_wati_message_alternative(phone_number, bot_reply)
            print("✅ WATI API Response (Form):")
            print(json.dumps(wati_response_alt, indent=2, ensure_ascii=False))
        else:
            print("❌ Chat API did not return success or no new messages found, not sending WhatsApp message.")
    else:
        print("❌ No conversation data found")
