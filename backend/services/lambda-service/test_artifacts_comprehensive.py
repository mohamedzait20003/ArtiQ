import requests
import json

# Test more comprehensive /artifacts endpoint scenarios
def test_artifacts_comprehensive():
    base_url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com"
    artifacts_url = f"{base_url}/artifacts"
    
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": "bearer test-token-ignored"  # Auth token passed but ignored
    }
    
    # Test 1: Single query for all artifacts
    print("=== Test 1: Query all artifacts ===")
    payload1 = [{"name": "*"}]
    response1 = requests.post(artifacts_url, json=payload1, headers=headers)
    print(f"Status: {response1.status_code}, Response: {response1.json()}")
    
    # Test 2: Specific artifact name query
    print("\n=== Test 2: Query specific artifact ===")
    payload2 = [{"name": "bert-base-uncased"}]
    response2 = requests.post(artifacts_url, json=payload2, headers=headers)
    print(f"Status: {response2.status_code}, Response: {response2.json()}")
    
    # Test 3: Multiple queries with types filter
    print("\n=== Test 3: Multiple queries with types ===")
    payload3 = [
        {"name": "bert", "types": ["model"]},
        {"name": "dataset", "types": ["dataset"]}
    ]
    response3 = requests.post(artifacts_url, json=payload3, headers=headers)
    print(f"Status: {response3.status_code}, Response: {response3.json()}")
    
    # Test 4: With offset parameter
    print("\n=== Test 4: With pagination offset ===")
    payload4 = [{"name": "*"}]
    response4 = requests.post(artifacts_url + "?offset=10", json=payload4, headers=headers)
    print(f"Status: {response4.status_code}, Response: {response4.json()}")
    
    # Test 5: Missing auth header (should still work for now)
    print("\n=== Test 5: Missing auth header ===")
    payload5 = [{"name": "*"}]
    headers_no_auth = {"Content-Type": "application/json"}
    response5 = requests.post(artifacts_url, json=payload5, headers=headers_no_auth)
    print(f"Status: {response5.status_code}, Response: {response5.text if response5.status_code != 200 else response5.json()}")

if __name__ == "__main__":
    test_artifacts_comprehensive()