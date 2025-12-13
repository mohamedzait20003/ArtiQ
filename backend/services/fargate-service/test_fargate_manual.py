#!/usr/bin/env python3
"""
Test script for Fargate service model evaluation pipeline.
Tests the full workflow: query -> create (if needed) -> rate
"""

import requests
import json
import time
import sys
from typing import Optional, Dict, Any


# Configuration
API_BASE_URL = "https://besp7zaxqg.execute-api.us-east-2.amazonaws.com"
AUTH_TOKEN = ""

# Test data
MODEL_NAME = "bert-base-uncased"
MODEL_URL = "https://huggingface.co/google-bert/bert-base-uncased"

HEADERS = {
    "X-Authorization": AUTH_TOKEN,
    "Content-Type": "application/json"
}


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def delete_artifact(artifact_id: str, artifact_type: str = "model") -> bool:
    """
    Delete an artifact using DELETE /artifacts/{artifact_type}/{id}.
    
    Returns:
        True if deleted successfully, False otherwise
    """
    print_section(f"Deleting existing artifact '{artifact_id}'")
    
    url = f"{API_BASE_URL}/artifacts/{artifact_type}/{artifact_id}"
    
    print(f"DELETE {url}")
    
    try:
        response = requests.delete(url, headers=HEADERS)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"\n✓ Artifact deleted successfully")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error deleting artifact: {e}")
        return False


def query_artifact(name: str) -> Optional[Dict[str, Any]]:
    """
    Query for an artifact by name using POST /artifacts.
    
    Returns:
        Artifact metadata if found, None otherwise
    """
    print_section(f"Step 1: Querying for artifact '{name}'")
    
    url = f"{API_BASE_URL}/artifacts"
    payload = [{"name": name}]
    
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            artifacts = response.json()
            print(f"Response: {json.dumps(artifacts, indent=2)}")
            
            if artifacts:
                # Find model type artifact
                for artifact in artifacts:
                    if artifact.get("type") == "model" and artifact.get("name") == name:
                        print(f"\n✓ Found model artifact: {artifact['name']} (ID: {artifact['id']})")
                        return artifact
                print(f"\n✗ No model artifact found with name '{name}'")
                return None
            else:
                print(f"\n✗ No artifacts found with name '{name}'")
                return None
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error querying artifact: {e}")
        return None


def create_artifact(name: str, url: str) -> Optional[str]:
    """
    Create a new model artifact using POST /artifact/model.
    
    Returns:
        Artifact ID if created successfully, None otherwise
    """
    api_url = f"{API_BASE_URL}/artifact/model"
    payload = {"url": url}
    
    print(f"POST {api_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(api_url, headers=HEADERS, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code in [201, 202]:
            artifact = response.json()
            print(f"Response: {json.dumps(artifact, indent=2)}")
            
            artifact_id = artifact.get("metadata", {}).get("id")
            if artifact_id:
                print(f"\n✓ Artifact created successfully!")
                print(f"  Name: {artifact['metadata']['name']}")
                print(f"  ID: {artifact_id}")
                print(f"  Type: {artifact['metadata']['type']}")
                
                if response.status_code == 202:
                    print("\n⚠ Note: Rating is being processed asynchronously (202 response)")
                
                return artifact_id
            else:
                print(f"\n✗ Artifact created but no ID returned")
                return None
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error creating artifact: {e}")
        return None


def get_rating(artifact_id: str) -> Optional[Dict[str, Any]]:
    """
    Get rating for an artifact using GET /artifact/model/{id}/rate.
    
    Returns:
        Rating data if successful, None otherwise
    """
    print_section(f"Step 3: Getting rating for artifact ID '{artifact_id}'")
    
    url = f"{API_BASE_URL}/artifact/model/{artifact_id}/rate"
    
    print(f"GET {url}")
    
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            rating = response.json()
            print(f"\n✓ Rating retrieved successfully!")
            print(f"\nFull Response:")
            print(json.dumps(rating, indent=2))
            
            return rating
            
        elif response.status_code == 404:
            print(f"\n✗ Rating not available (404)")
            print(f"Response: {response.text}")
            return None
                
        elif response.status_code == 500:
            print(f"Error: Rating system encountered an error")
            print(f"Response: {response.text}")
            return None
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting rating: {e}")
        return None


def get_cost(artifact_id: str, artifact_type: str = "model", dependency: bool = False) -> Optional[Dict[str, Any]]:
    """
    Get cost for an artifact using GET /artifact/{artifact_type}/{id}/cost.
    
    Returns:
        Cost data if successful, None otherwise
    """
    print_section(f"Step 4: Getting cost for artifact ID '{artifact_id}'")
    
    url = f"{API_BASE_URL}/artifact/{artifact_type}/{artifact_id}/cost"
    if dependency:
        url += "?dependency=true"
    
    print(f"GET {url}")
    
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            cost = response.json()
            print(f"\n✓ Cost retrieved successfully!")
            print(f"\nFull Response:")
            print(json.dumps(cost, indent=2))
            
            # Extract the cost value
            if artifact_id in cost:
                total_cost = cost[artifact_id].get("total_cost")
                standalone_cost = cost[artifact_id].get("standalone_cost")
                
                print(f"\nCost Summary:")
                if standalone_cost is not None:
                    print(f"  Standalone Cost: {standalone_cost} MB")
                print(f"  Total Cost: {total_cost} MB")
            
            return cost
            
        elif response.status_code == 404:
            print(f"\n✗ Artifact not found (404)")
            print(f"Response: {response.text}")
            return None
                
        elif response.status_code == 500:
            print(f"Error: Cost calculator encountered an error")
            print(f"Response: {response.text}")
            return None
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting cost: {e}")
        return None


def main():
    """Main test workflow."""
    print("\n" + "="*60)
    print("  Fargate Service Test - Model Evaluation Pipeline")
    print("="*60)
    print(f"\nAPI Base URL: {API_BASE_URL}")
    print(f"Model Name: {MODEL_NAME}")
    print(f"Model URL: {MODEL_URL}")
    
    # Step 1: Query for existing artifact
    artifact = query_artifact(MODEL_NAME)
    artifact_id = ""
    if artifact:
        artifact_id = artifact["id"]
    
    # Step 2: Delete if exists, then create fresh
    if artifact:
        artifact_type = artifact.get("type", "model")
        print(f"\n⚠ Artifact exists (ID: {artifact_id}). Deleting to trigger fresh evaluation...")
        
        if delete_artifact(artifact_id, artifact_type):
            print("✓ Deletion successful. Creating fresh artifact...")
        else:
            print("✗ Failed to delete artifact. Exiting.")
            sys.exit(1)
    
    # Step 3: Create artifact (fresh or for first time)
    print_section(f"Step 2: Creating new artifact '{MODEL_NAME}'")
    artifact_id = create_artifact(MODEL_NAME, MODEL_URL)
    if not artifact_id:
        print("\n✗ Failed to create artifact. Exiting.")
        sys.exit(1)
    
    # Step 4: Get rating (wait for evaluation to complete)
    rating = get_rating(artifact_id)
    
    if not rating:
        print_section("Test Failed")
        print(f"✗ Could not retrieve rating for artifact '{MODEL_NAME}' (ID: {artifact_id})")
        sys.exit(1)
    
    # Step 5: Get cost
    cost = get_cost(artifact_id, artifact_type="model", dependency=False)
    
    if cost:
        print_section("Test Completed Successfully!")
        print(f"✓ Artifact '{MODEL_NAME}' (ID: {artifact_id}) has been rated and cost calculated")
        print(f"✓ Net Score: {rating.get('net_score', 'N/A')}")
        
        if artifact_id in cost:
            total_cost = cost[artifact_id].get("total_cost")
            print(f"✓ Total Cost: {total_cost} MB")
        
        sys.exit(0)
    else:
        print_section("Test Partially Successful")
        print(f"✓ Artifact '{MODEL_NAME}' (ID: {artifact_id}) has been rated")
        print(f"✗ Could not retrieve cost")
        sys.exit(1)


if __name__ == "__main__":
    # Check if custom API URL and token provided as arguments
    if len(sys.argv) > 1:
        API_BASE_URL = sys.argv[1]
    if len(sys.argv) > 2:
        AUTH_TOKEN = sys.argv[2]
        HEADERS["X-Authorization"] = AUTH_TOKEN
    
    main()
