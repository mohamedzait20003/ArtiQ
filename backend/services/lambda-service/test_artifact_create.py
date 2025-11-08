import requests
import json

# Test artifact creation endpoint
url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com/artifact/model"
headers = {
    "Content-Type": "application/json",
    "X-Authorization": "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
data = {"url": "https://huggingface.co/google-bert/bert-base-uncased"}

print("Testing POST /artifact/model")
print(f"Request: {json.dumps(data)}")

response = requests.post(url, headers=headers, json=data)

print(f"Status: {response.status_code}")
if response.status_code == 201:
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print(f"Error response: {response.text}")