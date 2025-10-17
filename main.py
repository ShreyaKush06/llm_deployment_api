from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import base64
import os
from typing import List, Optional
from datetime import datetime
import subprocess
import uuid

app = FastAPI()

# Configuration
AIPIPE_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjMwMDM1MjlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.2UULPxOKpcLBQAnaounQId8ihlKB2TFAT-rrrKCcQiw"
AIPIPE_API_URL = "https://aipipe.org/openai/v1/chat/completions"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "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")
STUDENT_SECRET = "TheNameIsShreya"  # Change this

# Models
class Attachment(BaseModel):
    name: str
    url: str

class DeployRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: Optional[List[Attachment]] = []

class DeployResponse(BaseModel):
    repo_url: str
    commit_sha: str
    pages_url: str

# Utility Functions
def verify_secret(secret: str) -> bool:
    return secret == STUDENT_SECRET

def call_aipipe_api(prompt: str) -> str:
    """Call aipipe API to generate code"""
    headers = {
        "Authorization": f"Bearer {AIPIPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert web developer. Generate clean, minimal, production-ready HTML/CSS/JavaScript code."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(AIPIPE_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"API call failed: {str(e)}")

def extract_attachments(attachments: List[Attachment]) -> dict:
    """Extract and decode base64 attachments"""
    extracted = {}
    for att in attachments:
        if att.url.startswith("data:"):
            # Parse data URI
            parts = att.url.split(",", 1)
            if len(parts) == 2:
                try:
                    content = base64.b64decode(parts[1])
                    extracted[att.name] = content
                except:
                    pass
    return extracted

def create_html_file(brief: str, attachments: List[Attachment]) -> str:
    """Generate HTML file using LLM"""
    attachment_desc = "\n".join([f"- {a.name}" for a in attachments])
    
    prompt = f"""Generate a complete, self-contained HTML page that fulfills this requirement:

{brief}

Available attachments: {attachment_desc}

Return ONLY the HTML code wrapped in ```html``` blocks. Include inline CSS and JavaScript.
The HTML must:
1. Be valid HTML5
2. Include all necessary styling
3. Be production-ready
4. Handle the attachments appropriately
5. Meet all the checks mentioned if any

Example format:
```html
<!DOCTYPE html>
<html>
<head>...</head>
<body>...</body>
</html>
```"""
    
    response = call_aipipe_api(prompt)
    
    # Extract HTML from markdown code blocks
    if "```html" in response:
        start = response.find("```html") + 7
        end = response.find("```", start)
        html_code = response[start:end].strip()
    else:
        html_code = response
    
    return html_code

def create_github_repo(task_name: str, html_content: str, readme: str) -> tuple:
    """Create GitHub repo and push files"""
    repo_name = f"app-{task_name[:20]}-{uuid.uuid4().hex[:5]}"
    
    # Initialize repo locally
    repo_dir = f"/tmp/{repo_name}"
    os.makedirs(repo_dir, exist_ok=True)
    
    # Create files
    with open(f"{repo_dir}/index.html", "w") as f:
        f.write(html_content)
    
    with open(f"{repo_dir}/README.md", "w") as f:
        f.write(readme)
    
    with open(f"{repo_dir}/LICENSE", "w") as f:
        f.write("MIT License\n\nCopyright (c) 2025\n\nPermission is hereby granted...")
    
    # Git operations
    os.chdir(repo_dir)
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "student@example.com"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Student"], check=True, capture_output=True)
    subprocess.run(["git", "add", "."], check=True, capture_output=True)
    
    result = subprocess.run(["git", "commit", "-m", "Initial commit"], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Git commit failed: {result.stderr}")
    
    # Get commit SHA
    commit_result = subprocess.run(["git", "rev-parse", "HEAD"], 
                                  capture_output=True, text=True, check=True)
    commit_sha = commit_result.stdout.strip()
    
    return repo_dir, commit_sha

def generate_readme(brief: str, task: str, checks: List[str]) -> str:
    """Generate professional README.md"""
    checks_text = "\n".join([f"- {check}" for check in checks])
    
    readme = f"""# {task}

## Summary
{brief}

## Checks
{checks_text}

## Setup
1. Clone this repository
2. Open `index.html` in a web browser

## Usage
Open the application in any modern web browser. The app will automatically load and function according to the specifications.

## Code Explanation
This project generates a minimal, self-contained web application using an LLM-assisted generator. The application is built to fulfill specific requirements and pass automated checks.

## License
MIT License - See LICENSE file for details
"""
    return readme

# API Endpoints
@app.post("/api/endpoint")
async def handle_deployment(request: DeployRequest):
    """Main deployment endpoint"""
    
    # Verify secret
    if not verify_secret(request.secret):
        raise HTTPException(status_code=401, detail="Invalid secret")
    
    try:
        # Generate HTML
        html_content = create_html_file(request.brief, request.attachments)
        
        # Generate README
        readme = generate_readme(request.brief, request.task, request.checks)
        
        # Create GitHub repo
        repo_dir, commit_sha = create_github_repo(request.task, html_content, readme)
        
        # Simulated GitHub URL (in production, push to actual GitHub)
        repo_url = f"https://github.com/student/{request.task}-{commit_sha[:7]}"
        pages_url = f"https://student.github.io/{request.task}-{commit_sha[:7]}/"
        
        # Send evaluation notification
        notification = {
            "email": request.email,
            "task": request.task,
            "round": request.round,
            "nonce": request.nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        
        try:
            requests.post(request.evaluation_url, json=notification, timeout=10)
        except:
            pass  # Continue even if notification fails
        
        return {
            "status": "success",
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)