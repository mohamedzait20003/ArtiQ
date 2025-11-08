import requests
import json

def reset_database():
    """Reset the database to clean state"""
    base_url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com"
    reset_url = f"{base_url}/reset"
    
    headers = {
        "X-Authorization": "bearer test-token-ignored"
    }
    
    print("Resetting database...")
    response = requests.delete(reset_url, headers=headers)
    if response.status_code == 200:
        print("✅ Database reset successful")
        return True
    else:
        print(f"❌ Database reset failed: {response.status_code} - {response.text}")
        return False

def create_test_artifacts():
    """Create test artifacts with known names"""
    base_url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com"
    
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": "bearer test-token-ignored"
    }
    
    # Test artifacts with predictable names
    test_artifacts = [
        {
            "type": "model",
            "url": "https://huggingface.co/bert-base-uncased",
            "expected_name": "bert-base-uncased"
        },
        {
            "type": "model", 
            "url": "https://huggingface.co/gpt2",
            "expected_name": "gpt2"
        },
        {
            "type": "dataset",
            "url": "https://huggingface.co/datasets/squad",
            "expected_name": "squad"
        },
        {
            "type": "code",
            "url": "https://github.com/openai/whisper",
            "expected_name": "whisper"
        }
    ]
    
    created_artifacts = []
    print("Creating test artifacts...")
    
    for artifact in test_artifacts:
        artifact_url = f"{base_url}/artifact/{artifact['type']}"
        payload = {"url": artifact["url"]}
        
        print(f"  Creating {artifact['type']}: {artifact['expected_name']}")
        
        try:
            response = requests.post(artifact_url, json=payload, headers=headers)
            if response.status_code == 201:
                result = response.json()
                actual_name = result['metadata']['name']
                artifact_id = result['metadata']['id']
                artifact_type = result['metadata']['type']
                
                print(f"    ✅ Created: {actual_name} (id: {artifact_id})")
                created_artifacts.append({
                    'name': actual_name,
                    'id': artifact_id,
                    'type': artifact_type
                })
            else:
                print(f"    ❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"    ❌ Exception: {str(e)}")
    
    print(f"Created {len(created_artifacts)} test artifacts")
    return created_artifacts

def test_artifacts_name_filtering():
    """Test the /artifacts endpoint with name filtering"""
    base_url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com"
    artifacts_url = f"{base_url}/artifacts"
    
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": "bearer test-token-ignored"
    }
    
    print("=== Testing /artifacts endpoint with name filtering ===\n")
    
    # Step 1: Reset database
    if not reset_database():
        print("Failed to reset database, stopping test")
        return
    print()
    
    # Step 2: Create test artifacts
    created_artifacts = create_test_artifacts()
    if len(created_artifacts) == 0:
        print("No artifacts created, stopping test")
        return
    print()
    
    # Get the actual names for testing
    artifact_names = [a['name'] for a in created_artifacts]
    print(f"Test artifacts created with names: {artifact_names}")
    print()
    
    # Test 1: Get all artifacts
    print("1. Test: Get all artifacts")
    payload1 = [{"name": "*"}]
    response1 = requests.post(artifacts_url, json=payload1, headers=headers)
    print(f"   Status: {response1.status_code}")
    if response1.status_code == 200:
        artifacts = response1.json()
        print(f"   Total artifacts: {len(artifacts)}")
        names = [artifact['name'] for artifact in artifacts]
        print(f"   Names: {names}")
    print()
    
    # Test 2: Search for first artifact by exact name
    target_name = artifact_names[0] if artifact_names else "test-name"
    print(f"2. Test: Search for specific name '{target_name}'")
    payload2 = [{"name": target_name}]
    response2 = requests.post(artifacts_url, json=payload2, headers=headers)
    print(f"   Status: {response2.status_code}")
    if response2.status_code == 200:
        artifacts = response2.json()
        print(f"   Found artifacts: {len(artifacts)}")
        for artifact in artifacts:
            print(f"     - {artifact['name']} (id: {artifact['id']}, type: {artifact['type']})")
        all_match = all(artifact['name'] == target_name for artifact in artifacts)
        print(f"   ✅ All results match name: {all_match}" if all_match else f"   ❌ Some results don't match")
    print()
    
    # Test 3: Search for second artifact
    if len(artifact_names) > 1:
        target_name2 = artifact_names[1]
        print(f"3. Test: Search for specific name '{target_name2}'")
        payload3 = [{"name": target_name2}]
        response3 = requests.post(artifacts_url, json=payload3, headers=headers)
        print(f"   Status: {response3.status_code}")
        if response3.status_code == 200:
            artifacts = response3.json()
            print(f"   Found artifacts: {len(artifacts)}")
            for artifact in artifacts:
                print(f"     - {artifact['name']} (id: {artifact['id']}, type: {artifact['type']})")
            all_match = all(artifact['name'] == target_name2 for artifact in artifacts)
            print(f"   ✅ All results match name: {all_match}" if all_match else f"   ❌ Some results don't match")
        print()
    
    # Test 4: Search for non-existent name
    print("4. Test: Search for non-existent name")
    payload4 = [{"name": "definitely-does-not-exist"}]
    response4 = requests.post(artifacts_url, json=payload4, headers=headers)
    print(f"   Status: {response4.status_code}")
    if response4.status_code == 200:
        artifacts = response4.json()
        print(f"   Found artifacts: {len(artifacts)}")
        print(f"   ✅ Empty result for non-existent name" if len(artifacts) == 0 else f"   ❌ Found unexpected results")
    print()
    
    # Test 5: Multiple queries
    if len(artifact_names) >= 2:
        print("5. Test: Multiple queries in single request")
        payload5 = [
            {"name": artifact_names[0]},
            {"name": artifact_names[1]}
        ]
        response5 = requests.post(artifacts_url, json=payload5, headers=headers)
        print(f"   Status: {response5.status_code}")
        if response5.status_code == 200:
            artifacts = response5.json()
            print(f"   Found artifacts: {len(artifacts)}")
            names_found = set(artifact['name'] for artifact in artifacts)
            print(f"   Names found: {names_found}")
            expected_names = {artifact_names[0], artifact_names[1]}
            contains_expected = expected_names.issubset(names_found)
            print(f"   ✅ Contains expected names: {contains_expected}" if contains_expected else f"   ❌ Missing expected names")
        print()
    
    # Test 6: Combine name and type filters
    model_artifacts = [a for a in created_artifacts if a['type'] == 'model']
    if model_artifacts:
        model_name = model_artifacts[0]['name']
        print(f"6. Test: Search for name '{model_name}' with type filter ['model']")
        payload6 = [{"name": model_name, "types": ["model"]}]
        response6 = requests.post(artifacts_url, json=payload6, headers=headers)
        print(f"   Status: {response6.status_code}")
        if response6.status_code == 200:
            artifacts = response6.json()
            print(f"   Found artifacts: {len(artifacts)}")
            for artifact in artifacts:
                print(f"     - {artifact['name']} (id: {artifact['id']}, type: {artifact['type']})")
            all_match_name = all(artifact['name'] == model_name for artifact in artifacts)
            all_match_type = all(artifact['type'] == 'model' for artifact in artifacts)
            print(f"   ✅ Name and type filters work: {all_match_name and all_match_type}" if all_match_name and all_match_type else f"   ❌ Filter mismatch")
    
    print("\n=== Name filtering test completed ===")

if __name__ == "__main__":
    test_artifacts_name_filtering()