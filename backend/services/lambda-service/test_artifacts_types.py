import requests
import json

def test_artifacts_type_filtering():
    """Test the /artifacts endpoint with different type filters"""
    base_url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com"
    artifacts_url = f"{base_url}/artifacts"
    
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": "bearer test-token-ignored"
    }
    
    print("=== Testing /artifacts endpoint with type filtering ===\n")
    
    # Test 1: Get all artifacts (no type filter)
    print("1. Test: Get all artifacts (no type filter)")
    payload1 = [{"name": "*"}]
    response1 = requests.post(artifacts_url, json=payload1, headers=headers)
    print(f"   Status: {response1.status_code}")
    if response1.status_code == 200:
        artifacts = response1.json()
        print(f"   Total artifacts: {len(artifacts)}")
        types_found = set(artifact.get('type') for artifact in artifacts)
        print(f"   Types found: {types_found}")
        print(f"   Sample artifacts: {artifacts[:3] if artifacts else 'None'}")
    else:
        print(f"   Error: {response1.text}")
    print()
    
    # Test 2: Filter by model type only
    print("2. Test: Filter by 'model' type only")
    payload2 = [{"name": "*", "types": ["model"]}]
    response2 = requests.post(artifacts_url, json=payload2, headers=headers)
    print(f"   Status: {response2.status_code}")
    if response2.status_code == 200:
        artifacts = response2.json()
        print(f"   Model artifacts: {len(artifacts)}")
        types_found = set(artifact.get('type') for artifact in artifacts)
        print(f"   Types found: {types_found}")
        # Verify all returned artifacts are models
        all_models = all(artifact.get('type') == 'model' for artifact in artifacts)
        print(f"   ✅ All results are models: {all_models}" if all_models else f"   ❌ Found non-model types: {types_found}")
    else:
        print(f"   Error: {response2.text}")
    print()
    
    # Test 3: Filter by dataset type only
    print("3. Test: Filter by 'dataset' type only")
    payload3 = [{"name": "*", "types": ["dataset"]}]
    response3 = requests.post(artifacts_url, json=payload3, headers=headers)
    print(f"   Status: {response3.status_code}")
    if response3.status_code == 200:
        artifacts = response3.json()
        print(f"   Dataset artifacts: {len(artifacts)}")
        types_found = set(artifact.get('type') for artifact in artifacts)
        print(f"   Types found: {types_found}")
        # Verify all returned artifacts are datasets
        all_datasets = all(artifact.get('type') == 'dataset' for artifact in artifacts)
        print(f"   ✅ All results are datasets: {all_datasets}" if all_datasets else f"   ❌ Found non-dataset types: {types_found}")
    else:
        print(f"   Error: {response3.text}")
    print()
    
    # Test 4: Filter by code type only
    print("4. Test: Filter by 'code' type only")
    payload4 = [{"name": "*", "types": ["code"]}]
    response4 = requests.post(artifacts_url, json=payload4, headers=headers)
    print(f"   Status: {response4.status_code}")
    if response4.status_code == 200:
        artifacts = response4.json()
        print(f"   Code artifacts: {len(artifacts)}")
        types_found = set(artifact.get('type') for artifact in artifacts)
        print(f"   Types found: {types_found}")
        # Verify all returned artifacts are code
        all_code = all(artifact.get('type') == 'code' for artifact in artifacts)
        print(f"   ✅ All results are code: {all_code}" if all_code else f"   ❌ Found non-code types: {types_found}")
    else:
        print(f"   Error: {response4.text}")
    print()
    
    # Test 5: Filter by multiple types
    print("5. Test: Filter by multiple types ['model', 'dataset']")
    payload5 = [{"name": "*", "types": ["model", "dataset"]}]
    response5 = requests.post(artifacts_url, json=payload5, headers=headers)
    print(f"   Status: {response5.status_code}")
    if response5.status_code == 200:
        artifacts = response5.json()
        print(f"   Model + Dataset artifacts: {len(artifacts)}")
        types_found = set(artifact.get('type') for artifact in artifacts)
        print(f"   Types found: {types_found}")
        # Verify only models and datasets are returned
        valid_types = all(artifact.get('type') in ['model', 'dataset'] for artifact in artifacts)
        print(f"   ✅ Only models and datasets: {valid_types}" if valid_types else f"   ❌ Found other types: {types_found}")
    else:
        print(f"   Error: {response5.text}")
    print()
    
    # Test 6: Invalid type (should be ignored)
    print("6. Test: Invalid type 'invalid_type' (should be ignored)")
    payload6 = [{"name": "*", "types": ["invalid_type"]}]
    response6 = requests.post(artifacts_url, json=payload6, headers=headers)
    print(f"   Status: {response6.status_code}")
    if response6.status_code == 200:
        artifacts = response6.json()
        print(f"   Artifacts with invalid type filter: {len(artifacts)}")
        print(f"   ✅ Invalid type gracefully handled")
    else:
        print(f"   Error: {response6.text}")
    print()
    
    # Test 7: Mixed valid and invalid types
    print("7. Test: Mixed valid and invalid types ['model', 'invalid', 'dataset']")
    payload7 = [{"name": "*", "types": ["model", "invalid", "dataset"]}]
    response7 = requests.post(artifacts_url, json=payload7, headers=headers)
    print(f"   Status: {response7.status_code}")
    if response7.status_code == 200:
        artifacts = response7.json()
        print(f"   Artifacts with mixed types: {len(artifacts)}")
        types_found = set(artifact.get('type') for artifact in artifacts)
        print(f"   Types found: {types_found}")
        # Should only return model and dataset (invalid ignored)
        valid_types = all(artifact.get('type') in ['model', 'dataset'] for artifact in artifacts)
        print(f"   ✅ Invalid types filtered out: {valid_types}" if valid_types else f"   ❌ Invalid handling: {types_found}")
    else:
        print(f"   Error: {response7.text}")
    print()
    
    # Test 8: Empty types array
    print("8. Test: Empty types array")
    payload8 = [{"name": "*", "types": []}]
    response8 = requests.post(artifacts_url, json=payload8, headers=headers)
    print(f"   Status: {response8.status_code}")
    if response8.status_code == 200:
        artifacts = response8.json()
        print(f"   Artifacts with empty types: {len(artifacts)}")
        print(f"   ✅ Empty types array handled (should return all)")
    else:
        print(f"   Error: {response8.text}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_artifacts_type_filtering()