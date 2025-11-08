import requests
import json

def create_many_artifacts(count=150):
    """Create many artifacts to test pagination"""
    base_url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com"
    reset_url = f"{base_url}/reset"
    
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": "bearer test-token-ignored"
    }
    
    # Reset database first
    print("Resetting database...")
    reset_response = requests.delete(reset_url, headers={"X-Authorization": "bearer test-token-ignored"})
    if reset_response.status_code != 200:
        print(f"Reset failed: {reset_response.status_code}")
        return False
    print("✅ Database reset")
    
    # Create many test artifacts
    print(f"Creating {count} artifacts for pagination testing...")
    
    for i in range(count):
        artifact_type = ["model", "dataset", "code"][i % 3]
        artifact_url = f"{base_url}/artifact/{artifact_type}"
        
        payload = {"url": f"https://example.com/artifact-{i:03d}"}
        
        try:
            response = requests.post(artifact_url, json=payload, headers=headers)
            if response.status_code == 201:
                if i % 20 == 0:  # Print progress every 20 artifacts
                    print(f"  Created {i+1}/{count} artifacts...")
            else:
                print(f"Failed to create artifact {i}: {response.status_code}")
        except Exception as e:
            print(f"Error creating artifact {i}: {e}")
    
    print(f"✅ Created {count} artifacts")
    return True

def test_pagination():
    """Test pagination with offset"""
    base_url = "https://7mdrks3e27.execute-api.us-east-2.amazonaws.com"
    artifacts_url = f"{base_url}/artifacts"
    
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": "bearer test-token-ignored"
    }
    
    print("=== Testing pagination with offset ===\n")
    
    # Test 1: First page (no offset)
    print("1. Test: First page (no offset)")
    payload = [{"name": "*"}]
    response = requests.post(artifacts_url, json=payload, headers=headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        artifacts = response.json()
        offset_header = response.headers.get('offset')
        
        print(f"   Artifacts returned: {len(artifacts)}")
        print(f"   Offset header: {offset_header}")
        print(f"   ✅ Should return max 100 artifacts: {len(artifacts) <= 100}")
        
        # Test 2: Second page (with offset)
        if offset_header:
            print(f"\n2. Test: Second page (with offset)")
            response2 = requests.post(f"{artifacts_url}?offset={offset_header}", json=payload, headers=headers)
            
            print(f"   Status: {response2.status_code}")
            if response2.status_code == 200:
                artifacts2 = response2.json()
                offset_header2 = response2.headers.get('offset')
                
                print(f"   Artifacts returned: {len(artifacts2)}")
                print(f"   Next offset header: {offset_header2}")
                
                # Check no duplicates between pages
                ids_page1 = set(a['id'] for a in artifacts)
                ids_page2 = set(a['id'] for a in artifacts2)
                overlap = ids_page1.intersection(ids_page2)
                
                print(f"   ✅ No duplicate IDs between pages: {len(overlap) == 0}")
                if len(overlap) > 0:
                    print(f"   ❌ Found {len(overlap)} duplicate IDs")
                
                # Test 3: Third page if exists
                if offset_header2:
                    print(f"\n3. Test: Third page")
                    response3 = requests.post(f"{artifacts_url}?offset={offset_header2}", json=payload, headers=headers)
                    
                    print(f"   Status: {response3.status_code}")
                    if response3.status_code == 200:
                        artifacts3 = response3.json()
                        offset_header3 = response3.headers.get('offset')
                        
                        print(f"   Artifacts returned: {len(artifacts3)}")
                        print(f"   Next offset header: {offset_header3}")
                        
                        # Total count across all pages
                        total_artifacts = len(artifacts) + len(artifacts2) + len(artifacts3)
                        print(f"   Total artifacts across 3 pages: {total_artifacts}")
                else:
                    print(f"\n3. No third page (offset header was None)")
                    total_artifacts = len(artifacts) + len(artifacts2)
                    print(f"   Total artifacts across 2 pages: {total_artifacts}")
            else:
                print(f"   ❌ Second page failed: {response2.text}")
        else:
            print(f"\n2. No second page needed (all results fit in first page)")
            print(f"   Total artifacts: {len(artifacts)}")
    else:
        print(f"   ❌ First page failed: {response.text}")
    
    print("\n=== Pagination test completed ===")

def main():
    print("Setting up pagination test environment...\n")
    
    # Create many artifacts for testing
    if create_many_artifacts(150):
        print()
        test_pagination()
    else:
        print("Failed to create test artifacts")

if __name__ == "__main__":
    main()