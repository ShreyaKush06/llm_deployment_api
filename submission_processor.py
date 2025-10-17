import csv
import requests
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict
import time

# Configuration
STUDENT_API_BASE = "http://localhost:8000"  # Change to student's actual API
EVALUATION_API = "http://localhost:8001/notify"
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # Exponential backoff

# Task Templates
TASK_TEMPLATES = {
    "sum-of-sales": {
        "brief": "Publish a single-page site that displays 'Sales Summary Dashboard'. Create a mock sales table with at least 3 products and show total sales.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays sales data in a table",
            "Page shows total sales amount",
            "Page is responsive and styled"
        ]
    },
    "markdown-to-html": {
        "brief": "Create a page that converts markdown text to HTML. Include a text area where users can paste markdown and see live HTML preview below.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page has textarea for markdown input",
            "Page renders markdown to HTML",
            "Code blocks are syntax highlighted"
        ]
    },
    "github-user-profile": {
        "brief": "Create a page with a form to search GitHub users. Display user info including name, profile picture, followers, and account creation date.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Form accepts GitHub username",
            "Page fetches from GitHub API",
            "User info is displayed correctly"
        ]
    }
}

class SubmissionProcessor:
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.submissions = []
        self.load_submissions()
    
    def load_submissions(self):
        """Load submissions from Google Form CSV"""
        try:
            with open(self.csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.submissions.append(row)
            print(f" Loaded {len(self.submissions)} submissions from {self.csv_file}")
        except FileNotFoundError:
            print(f" CSV file not found: {self.csv_file}")
            print("Create a submissions.csv with columns: timestamp,email,endpoint,secret")
    
    def process_round_1(self):
        """Process Round 1 - Send initial tasks to all students"""
        print("\n" + "="*70)
        print("PROCESSING ROUND 1 TASKS")
        print("="*70)
        
        for idx, submission in enumerate(self.submissions):
            email = submission.get('email', '').strip()
            endpoint = submission.get('endpoint', '').strip()
            secret = submission.get('secret', '').strip()
            
            if not all([email, endpoint, secret]):
                print(f"  Skipping submission {idx+1}: Missing required fields")
                continue
            
            print(f"\nSubmission {idx+1}/{len(self.submissions)}")
            print(f"   Email: {email}")
            print(f"   Endpoint: {endpoint}")
            
            # Pick a random template
            template_name = list(TASK_TEMPLATES.keys())[idx % len(TASK_TEMPLATES)]
            template = TASK_TEMPLATES[template_name]
            
            # Generate task
            task_id = f"{template_name}-{uuid.uuid4().hex[:5]}"
            nonce = str(uuid.uuid4())
            
            task_request = {
                "email": email,
                "secret": secret,
                "task": task_id,
                "round": 1,
                "nonce": nonce,
                "brief": template['brief'],
                "checks": template['checks'],
                "evaluation_url": EVALUATION_API,
                "attachments": []
            }
            
            # Send to student API
            success = self.send_task(endpoint, task_request, email)
            
            if success:
                print(f"    Task sent successfully")
                print(f"   Task ID: {task_id}")
                print(f"   Template: {template_name}")
            else:
                print(f"    Failed to send task")
            
            time.sleep(1)  # Rate limiting
    
    def send_task(self, endpoint: str, task_request: Dict, email: str) -> bool:
        """Send task to student API with retries"""
        url = f"{endpoint}/api/endpoint" if not endpoint.endswith('/api/endpoint') else endpoint
        
        for attempt in range(MAX_RETRIES):
            try:
                print(f"   Attempt {attempt+1}/{MAX_RETRIES}...")
                response = requests.post(
                    url,
                    json=task_request,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"   Status: {response.status_code}")
                    return True
                else:
                    print(f"   Status: {response.status_code}")
                    if attempt < MAX_RETRIES - 1:
                        delay = RETRY_DELAYS[attempt]
                        print(f"   Retrying in {delay} seconds...")
                        time.sleep(delay)
            
            except requests.exceptions.RequestException as e:
                print(f"   Error: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAYS[attempt]
                    print(f"   Retrying in {delay} seconds...")
                    time.sleep(delay)
        
        return False
    
    def process_round_2(self):
        """Process Round 2 - Send revision tasks based on Round 1 results"""
        print("\n" + "="*70)
        print("PROCESSING ROUND 2 TASKS")
        print("="*70)
        print("\n  This would fetch results from evaluation API")
        print("    and generate Round 2 tasks based on Round 1 performance")
        print("\n    For now, manually trigger after reviewing Round 1 results")

def create_sample_csv():
    """Create a sample submissions CSV"""
    data = [
        {
            "timestamp": datetime.now().isoformat(),
            "email": "student@iitm.ac.in",
            "endpoint": "http://localhost:8000/api/endpoint",
            "secret": "your_secret_key"
        }
    ]
    
    with open("submissions.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "email", "endpoint", "secret"])
        writer.writeheader()
        writer.writerows(data)
    
    print(" Created sample submissions.csv")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Process student submissions')
    parser.add_argument('--csv', default='submissions.csv', help='CSV file path')
    parser.add_argument('--create-sample', action='store_true', help='Create sample CSV')
    parser.add_argument('--round', type=int, default=1, help='Round to process (1 or 2)')
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_csv()
        return
    
    processor = SubmissionProcessor(args.csv)
    
    if args.round == 1:
        processor.process_round_1()
    elif args.round == 2:
        processor.process_round_2()
    else:
        print("Invalid round. Use --round 1 or --round 2")

if __name__ == "__main__":
    main()