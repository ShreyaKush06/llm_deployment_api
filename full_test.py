import requests
import json
import time

BASE_URL = "http://localhost:8000"
SECRET = "TheNameIsShreya"  # Match what's in main.py

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f" Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f" Error: {e}")
        return False

def test_invalid_secret():
    """Test with wrong secret"""
    print("\n" + "=" * 60)
    print("Testing Invalid Secret (Should Fail)")
    print("=" * 60)
    payload = {
        "email": "student@example.com",
        "secret": "wrong_secret",
        "task": "test-task",
        "round": 1,
        "nonce": "test-123",
        "brief": "Create a simple page",
        "checks": ["Test check"],
        "evaluation_url": "http://localhost:8000/health",
        "attachments": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/endpoint", json=payload)
        if response.status_code == 401:
            print(f" Correctly rejected: {response.json()['detail']}")
            return True
        else:
            print(f" Should have been rejected but got {response.status_code}")
            return False
    except Exception as e:
        print(f" Error: {e}")
        return False

def test_deployment_round1():
    """Test successful deployment (Round 1)"""
    print("\n" + "=" * 60)
    print("Testing Round 1 Deployment")
    print("=" * 60)
    payload = {
        "email": "student@test@iitm.ac.in",
        "secret": SECRET,
        "task": f"sum-of-sales-{int(time.time())}",
        "round": 1,
        "nonce": f"nonce-{int(time.time())}",
        "brief": "Create a page that displays 'Hello World' in bold using Bootstrap",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays text"
        ],
        "evaluation_url": "http://localhost:8000/health",
        "attachments": []
    }
    
    try:
        print("Sending deployment request...")
        response = requests.post(f"{BASE_URL}/api/endpoint", json=payload, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f" Success!")
            print(f"Repo URL: {data['repo_url']}")
            print(f"Commit SHA: {data['commit_sha']}")
            print(f"Pages URL: {data['pages_url']}")
            return True
        else:
            print(f" Failed: {response.json()}")
            return False
    except Exception as e:
        print(f" Error: {e}")
        return False

def test_deployment_round2():
    """Test revision deployment (Round 2)"""
    print("\n" + "=" * 60)
    print("Testing Round 2 Deployment")
    print("=" * 60)
    payload = {
        "email": "student@test@iitm.ac.in",
        "secret": SECRET,
        "task": "sum-of-sales-test",
        "round": 2,
        "nonce": "nonce-round2",
        "brief": "Update the page to add a subtitle",
        "checks": [
            "Page displays both title and subtitle"
        ],
        "evaluation_url": "http://localhost:8000/health",
        "attachments": []
    }
    
    try:
        print("Sending revision request...")
        response = requests.post(f"{BASE_URL}/api/endpoint", json=payload, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f" Success!")
            print(f"Round: {data.get('round')}")
            print(f"Repo URL: {data['repo_url']}")
            return True
        else:
            print(f" Failed: {response.json()}")
            return False
    except Exception as e:
        print(f" Error: {e}")
        return False

def test_with_attachments():
    """Test with base64 attachments"""
    print("\n" + "=" * 60)
    print("Testing with Attachments")
    print("=" * 60)
    payload = {
        "email": "student@test@iitm.ac.in",
        "secret": SECRET,
        "task": f"markdown-test-{int(time.time())}",
        "round": 1,
        "nonce": f"nonce-attach-{int(time.time())}",
        "brief": "Create a markdown viewer page",
        "checks": [
            "Markdown is rendered",
            "Code blocks are highlighted"
        ],
        "evaluation_url": "http://localhost:8000/health",
        "attachments": [
            {
                "name": "sample.md",
                "url": "data:text/markdown;base64,IyBTYW1wbGUgTWFya2Rvd24KClRoaXMgaXMgYSBzYW1wbGUgbWFya2Rvd24gZmlsZS4K"
            }
        ]
    }
    
    try:
        print("Sending request with attachments...")
        response = requests.post(f"{BASE_URL}/api/endpoint", json=payload, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f" Success!")
            print(f"Repo URL: {data['repo_url']}")
            return True
        else:
            print(f" Failed: {response.json()}")
            return False
    except Exception as e:
        print(f" Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  LLM DEPLOYMENT - COMPREHENSIVE TEST SUITE".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60 + "\n")
    
    results = {
        "Health Check": test_health(),
        "Invalid Secret": test_invalid_secret(),
        "Round 1 Deployment": test_deployment_round1(),
        "Round 2 Deployment": test_deployment_round2(),
        "With Attachments": test_with_attachments(),
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results.items():
        status = " PASSED" if result else " FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n All tests passed! Your API is ready for deployment!")
    else:
        print("\n  Some tests failed. Check errors above.")

if __name__ == "__main__":
    run_all_tests()