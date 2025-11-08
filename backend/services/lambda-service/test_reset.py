import requests
import json

# Test reset endpoint
url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com/reset"
headers = {
    "Content-Type": "application/json",
    "X-Authorization": "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}

print("Testing DELETE /reset")

response = requests.delete(url, headers=headers)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print(f"Error response: {response.text}")