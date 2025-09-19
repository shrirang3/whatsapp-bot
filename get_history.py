import requests

url = "https://live-mt-server.wati.io/200128/api/v1/getMessages/919550822097"

headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhMTc3MzU3Mi01ODFiLTQ4MzQtOWJiOS1mYWM2NjRkYzNiMjAiLCJ1bmlxdWVfbmFtZSI6ImVrYWdhckB2YWhhbi5jbyIsIm5hbWVpZCI6ImVrYWdhckB2YWhhbi5jbyIsImVtYWlsIjoiZWthZ2FyQHZhaGFuLmNvIiwiYXV0aF90aW1lIjoiMTAvMDUvMjAyMyAwNzozNjo1NyIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJ0ZW5hbnRfaWQiOiIyMDAxMjgiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.ud5AYN5Kf5Xm17WX8Krr1Z3qJo0waJu75cY-o3N2EuU"}

response = requests.get(url, headers=headers)

print(response.text)

#print(response.json().get("messages", {}).get("items", [{}])[0].get("text", ""))