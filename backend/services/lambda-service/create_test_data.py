import requests
import json

def create_test_artifacts():
    """Create sample artifacts for testing type filtering"""
    base_url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com"
    
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": "bearer test-token-ignored"
    }
    
    # Sample artifacts to create
    test_artifacts = [
        {
            "type": "model",
            "url": "https://huggingface.co/bert-base-uncased",
            "name": "bert-base-uncased"
        },
        {
            "type": "model", 
            "url": "https://huggingface.co/gpt2",
            "name": "gpt2"
        },
        {
            "type": "dataset",
            "url": "https://huggingface.co/datasets/squad",
            "name": "squad-dataset"
        },
        {
            "type": "dataset",
            "url": "https://huggingface.co/datasets/imdb",
            "name": "imdb-dataset"
        },
        {
            "type": "code",
            "url": "https://github.com/openai/whisper",
            "name": "whisper-code"
        },
        {
            "type": "code",
            "url": "https://github.com/huggingface/transformers",
            "name": "transformers-code"
        }
    ]
    
    print("Creating test artifacts...")
    created_count = 0
    
    for artifact in test_artifacts:
        artifact_url = f"{base_url}/artifact/{artifact['type']}"
        payload = {"url": artifact["url"]}
        
        print(f"Creating {artifact['type']}: {artifact['name']}")
        
        try:
            response = requests.post(artifact_url, json=payload, headers=headers)
            if response.status_code == 201:
                print(f"  ✅ Created successfully")
                created_count += 1
            elif response.status_code == 409:
                print(f"  ⚠️  Already exists")
                created_count += 1
            else:
                print(f"  ❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    print(f"\nTest data creation completed. {created_count}/{len(test_artifacts)} artifacts ready.")
    return created_count > 0

if __name__ == "__main__":
    create_test_artifacts()