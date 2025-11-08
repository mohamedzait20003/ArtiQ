import requests
import json

# Test the /artifacts endpoint
def test_artifacts_endpoint():
    base_url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com"
    
    # Test POST /artifacts
    artifacts_url = f"{base_url}/artifacts"
    
    # Prepare test payload (simple query for all artifacts)
    payload = [
        {
            "name": "*"  # Query for all artifacts
        }
    ]
    
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": "bearer test-token-ignored"  # Auth token passed but ignored
    }
    
    print(f"Testing POST {artifacts_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(artifacts_url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Success! /artifacts endpoint is working")
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            if response_data == []:
                print("✅ Correctly returned empty list (database is empty)")
            else:
                print(f"⚠️  Expected empty list, got: {response_data}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_artifacts_endpoint()