import requests
import json
import os
import csv
import time
import re

# -------------------------
# CONFIG
# -------------------------
CHAT_API_URL = "https://8795a39e8611.ngrok-free.app/chat"   # RAG bot API
WATI_API_BASE = "https://live-mt-server.wati.io/200128/api/v1"
WATI_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhMTc3MzU3Mi01ODFiLTQ4MzQtOWJiOS1mYWM2NjRkYzNiMjAiLCJ1bmlxdWVfbmFtZSI6ImVrYWdhckB2YWhhbi5jbyIsIm5hbWVpZCI6ImVrYWdhckB2YWhhbi5jbyIsImVtYWlsIjoiZWthZ2FyQHZhaGFuLmNvIiwiYXV0aF90aW1lIjoiMTAvMDUvMjAyMyAwNzozNjo1NyIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJ0ZW5hbnRfaWQiOiIyMDAxMjgiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.ud5AYN5Kf5Xm17WX8Krr1Z3qJo0waJu75cY-o3N2EuU"


CHAT_HEADERS = {"Content-Type": "application/json"}
WATI_HEADERS = {"Authorization": f"Bearer {WATI_TOKEN}", "Content-Type": "application/json"}


def save_conversation_to_csv(phone_number: str, messages: list, output_file="conversations.csv"):
    row = {
        "phone_number": phone_number,
        "messages": json.dumps(messages, ensure_ascii=False)
    }
    file_exists = os.path.isfile(output_file)
    with open(output_file, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["phone_number", "messages"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
    print(f"💾 Saved conversation for {phone_number} with {len(messages)} messages into {output_file}")


def send_conversation(conversation_json, phone_number=None):
    if not conversation_json or "messages" not in conversation_json:
        raise ValueError("Invalid conversation_json format")

    all_messages = conversation_json.get("messages", [])

    # Stop at first "Congratulations!" assistant message
    target_content_snippet = "Congratulations! Aap *Swiggy Instamart Delivery Partner* job ke liye shortlist hue hain."
    template_index = -1
    for i, msg in enumerate(all_messages):
        if msg.get("role", "").lower() == "assistant" and target_content_snippet in msg.get("content", ""):
            template_index = i
            break
    
    if template_index != -1:
        messages_to_send = all_messages[:template_index]
        print(f"✅ Found template message at index {template_index}. Sending {len(messages_to_send)} messages before it.")
    else:
        messages_to_send = all_messages
        print("⚠️ Template message not found. Sending full history.")

    if not messages_to_send:
        return {"success": False, "message": "No messages to process."}

    payload = {"messages": []}
    if phone_number:
        payload["phone_number"] = str(phone_number)

    for msg in messages_to_send:
        if msg.get("role", "").lower() in ["user", "assistant"]:
            payload["messages"].append({
                "role": msg.get("role", ""),
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp")
            })

    save_conversation_to_csv(phone_number, payload["messages"])

    try:
        response = requests.post(CHAT_API_URL, headers=CHAT_HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def split_message_into_chunks(message: str, max_sentences: int = 2):
    sentences = re.split(r'(?<=[.!?])\s+', message.strip())
    return [" ".join(sentences[i:i+max_sentences]).strip() for i in range(0, len(sentences), max_sentences) if sentences[i:i+max_sentences]]


def send_wati_message_alternative(phone_number: str, message: str, delay_seconds: int = 1):
    message = str(message).strip()
    if not message:
        return {"result": False, "error": "Message is empty"}
    
    url = f"{WATI_API_BASE}/sendSessionMessage/{phone_number}"
    headers_form = {"Authorization": f"Bearer {WATI_TOKEN}"}
    chunks = split_message_into_chunks(message)
    results = []

    for idx, chunk in enumerate(chunks, start=1):
        data = {"messageText": chunk}
        try:
            response = requests.post(url, headers=headers_form, data=data, timeout=30)
            if response.status_code == 200:
                results.append(response.json())
            else:
                results.append({"result": False, "error": f"HTTP {response.status_code}: {response.text}"})
        except Exception as e:
            results.append({"result": False, "error": str(e)})
        time.sleep(delay_seconds)

    return results
