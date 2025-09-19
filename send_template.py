import requests
from datetime import datetime
import json

# ---------------------
# Hardcoded values
# ---------------------
url = "https://live-mt-server.wati.io/200128/api/v1/sendTemplateMessage?whatsappNumber=919075022502"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhMTc3MzU3Mi01ODFiLTQ4MzQtOWJiOS1mYWM2NjRkYzNiMjAiLCJ1bmlxdWVfbmFtZSI6ImVrYWdhckB2YWhhbi5jbyIsIm5hbWVpZCI6ImVrYWdhckB2YWhhbi5jbyIsImVtYWlsIjoiZWthZ2FyQHZhaGFuLmNvIiwiYXV0aF90aW1lIjoiMTAvMDUvMjAyMyAwNzozNjo1NyIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJ0ZW5hbnRfaWQiOiIyMDAxMjgiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.ud5AYN5Kf5Xm17WX8Krr1Z3qJo0waJu75cY-o3N2EuU",
    "Content-Type": "application/json"
}

payload = {
    "broadcast_name": f"MyTest-{datetime.now().strftime('%Y%m%d%H%M%S')}",  # required field
    "template_name": "swiggy_im_template",  # replace with your approved template name
}

# ---------------------
# Send request
# ---------------------
response = requests.post(url, headers=headers, json=payload)

print("Status Code:", response.status_code)
print("Response Text:", response.text)

# Optional: parse JSON safely
try:
    print("Result:", response.json().get("result"))
except Exception:
    print("Could not parse JSON")
