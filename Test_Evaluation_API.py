import requests
import json

EVAL_URL = "http://localhost:8001"

def test_notification():
    """Test receiving a deployment notification"""
    print("\n" + "="*60)
    print("Test 1: Send Deployment Notification")
    print("="*60)
    
    notification = {
        "email": "student@iitm.ac.in",
        "task": "sum-of-sales-test",
        "round": 1,
        "nonce": "nonce-123",
        "repo_url": "https://github.com/student/app-sum-of-sales-abc12",
        "commit_sha": "abc123def456",
        "pages_url": "https://student.github.io/app-sum-of-sales-abc12/"
    }
    
    response = requests.post(f"{EVAL_URL}/notify", json=notification)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_round2_notification():
    """Test Round 2 deployment"""
    print("\n" + "="*60)
    print("Test 2: Send Round 2 Deployment Notification")
    print("="*60)
    
    notification = {
        "email": "student@iitm.ac.in",
        "task": "sum-of-sales-test",
        "round": 2,
        "nonce": "nonce-456",
        "repo_url": "https://github.com/student/app-sum-of-sales-abc12",
        "commit_sha": "def456ghi789",
        "pages_url": "https://student.github.io/app-sum-of-sales-abc12/"
    }
    
    response = requests.post(f"{EVAL_URL}/notify", json=notification)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_deployments():
    """Test retrieving deployments"""
    print("\n" + "="*60)
    print("Test 3: Get All Deployments")
    print("="*60)
    
    response = requests.get(f"{EVAL_URL}/deployments")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total deployments: {data['total']}")
    print(f"Deployments:")
    for d in data['deployments']:
        print(f"  - {d['email']} | Task: {d['task']} | Round: {d.get('round', 'N/A')}")
    return response.status_code == 200

def test_get_by_email():
    """Test retrieving deployments by email"""
    print("\n" + "="*60)
    print("Test 4: Get Deployments by Email")
    print("="*60)
    
    email = "student@iitm.ac.in"
    response = requests.get(f"{EVAL_URL}/deployments/{email}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Deployments for {email}: {data['total']}")
    return response.status_code == 200

def test_evaluation_result():
    """Test storing evaluation results"""
    print("\n" + "="*60)
    print("Test 5: Store Evaluation Result")
    print("="*60)
    
    result = {
        "email": "student@iitm.ac.in",
        "task": "sum-of-sales-test",
        "round": 1,
        "repo_url": "https://github.com/student/app-sum-of-sales-abc12",
        "commit_sha": "abc123def456",
        "pages_url": "https://student.github.io/app-sum-of-sales-abc12/",
        "check": "Repo has MIT license",
        "score": 100,
        "reason": "MIT license file found at root",
        "logs": "Check passed successfully"
    }
    
    response = requests.post(f"{EVAL_URL}/evaluate", json=result)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_summary():
    """Test getting summary"""
    print("\n" + "="*60)
    print("Test 6: Get Summary")
    print("="*60)
    
    response = requests.get(f"{EVAL_URL}/summary")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total deployments: {data['total_deployments']}")
    print(f"Total tasks: {data['total_tasks']}")
    print(f"Round 1 deployments: {data['round_1_deployments']}")
    print(f"Round 2 deployments: {data['round_2_deployments']}")
    print(f"Unique students: {data['unique_students']}")
    return response.status_code == 200

def test_export():
    """Test exporting data"""
    print("\n" + "="*60)
    print("Test 7: Export Data")
    print("="*60)
    
    response = requests.get(f"{EVAL_URL}/export")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Exported {len(data['deployments'])} deployments")
    print(f"Exported at: {data['exported_at']}")
    return response.status_code == 200

def run_all():
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "EVALUATION API TEST SUITE".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    results = {
        "Send Notification": test_notification(),
        "Send Round 2": test_round2_notification(),
        "Get Deployments": test_get_deployments(),
        "Get by Email": test_get_by_email(),
        "Store Result": test_evaluation_result(),
        "Get Summary": test_summary(),
        "Export Data": test_export(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test, result in results.items():
        status = "complete" if result else "incomplete"
        print(f"{status} {test}")
    
    passed = sum(results.values())
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n All evaluation API tests passed!")
    else:
        print("\n Some tests failed")

if __name__ == "__main__":
    run_all()