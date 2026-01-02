#!/usr/bin/env python3
"""
Test script for Pharmyrus Async API
"""

import sys
import time
import requests
import json
from typing import Optional

# Configuration
API_URL = "http://localhost:8000"  # Change to your Railway URL


def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    data = response.json()
    
    print(f"   Status: {data['status']}")
    print(f"   Redis: {data['redis']}")
    print(f"   Version: {data['version']}")
    
    if data['status'] != 'healthy':
        print("   ⚠️  API not healthy!")
        return False
    
    print("   ✅ Health check passed")
    return True


def test_sync_search(molecule: str = "aspirin"):
    """Test synchronous search"""
    print(f"\n🔍 Testing sync search for: {molecule}")
    
    response = requests.post(
        f"{API_URL}/search",
        json={
            "molecule": molecule,
            "countries": ["BR"],
            "include_wipo": False
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Sync search completed")
        print(f"   Patents found: {result.get('patent_search', {}).get('total_patents', 0)}")
        return result
    else:
        print(f"   ❌ Sync search failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_async_search(molecule: str = "darolutamide", include_wipo: bool = False):
    """Test asynchronous search with progress tracking"""
    print(f"\n🚀 Testing async search for: {molecule}")
    print(f"   WIPO: {include_wipo}")
    
    # 1. Start search
    response = requests.post(
        f"{API_URL}/search/async",
        json={
            "molecule": molecule,
            "countries": ["BR"],
            "include_wipo": include_wipo
        }
    )
    
    if response.status_code != 200:
        print(f"   ❌ Failed to start search: {response.status_code}")
        print(f"   {response.text}")
        return None
    
    data = response.json()
    job_id = data['job_id']
    print(f"   ✅ Search started")
    print(f"   Job ID: {job_id}")
    print(f"   Estimated time: {data['estimated_time']}")
    
    # 2. Poll for status
    print("\n   📊 Monitoring progress...")
    last_progress = -1
    
    while True:
        time.sleep(5)  # Poll every 5 seconds
        
        response = requests.get(f"{API_URL}/search/status/{job_id}")
        status = response.json()
        
        progress = status['progress']
        step = status.get('step', 'Processing...')
        elapsed = status.get('elapsed_seconds', 0)
        
        # Only print if progress changed
        if progress != last_progress:
            bar_length = 20
            filled = int(bar_length * progress / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"   [{bar}] {progress}% - {step} ({elapsed:.1f}s)")
            last_progress = progress
        
        # Check if complete
        if status['status'] == 'complete':
            print(f"   ✅ Search completed in {elapsed:.1f}s")
            break
        
        # Check if failed
        if status['status'] == 'failed':
            print(f"   ❌ Search failed: {status['message']}")
            return None
    
    # 3. Get result
    print("\n   📥 Fetching results...")
    response = requests.get(f"{API_URL}/search/result/{job_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Results retrieved")
        
        # Save to file
        filename = f"{molecule}_result.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"   💾 Saved to: {filename}")
        
        return result
    else:
        print(f"   ❌ Failed to get result: {response.status_code}")
        return None


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Pharmyrus Async API Test Suite")
    print("=" * 60)
    
    # Update API URL if provided
    global API_URL
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]
    
    print(f"\nAPI URL: {API_URL}\n")
    
    # Test 1: Health
    if not test_health():
        print("\n❌ Health check failed. Stopping tests.")
        return
    
    # Test 2: Sync search (fast)
    print("\n" + "=" * 60)
    print("TEST 1: Synchronous Search (Fast)")
    print("=" * 60)
    test_sync_search("aspirin")
    
    # Test 3: Async search (no WIPO)
    print("\n" + "=" * 60)
    print("TEST 2: Asynchronous Search (No WIPO)")
    print("=" * 60)
    test_async_search("darolutamide", include_wipo=False)
    
    # Test 4: Async search (with WIPO) - commented out for now
    # print("\n" + "=" * 60)
    # print("TEST 3: Asynchronous Search (With WIPO - Long)")
    # print("=" * 60)
    # test_async_search("darolutamide", include_wipo=True)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
