from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
import os
from typing import Optional, List

app = FastAPI()

# In-memory database (for testing)
# In production, use actual database
deployments = []
tasks = []

# Models
class DeploymentNotification(BaseModel):
    email: str
    task: str
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str

class TaskRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: Optional[list] = []

class EvaluationResult(BaseModel):
    email: str
    task: str
    round: int
    repo_url: str
    commit_sha: str
    pages_url: str
    check: str
    score: float  # 0-100
    reason: str
    logs: Optional[str] = None

# Endpoints
@app.post("/notify")
async def receive_deployment(notification: DeploymentNotification):
    """
    Receives deployment notifications from student API
    Called when student deploys their app
    """
    print(f"\n📨 Received deployment notification:")
    print(f"   Email: {notification.email}")
    print(f"   Task: {notification.task}")
    print(f"   Round: {notification.round}")
    print(f"   Repo: {notification.repo_url}")
    print(f"   Commit: {notification.commit_sha}")
    
    # Store in database
    deployment = {
        "timestamp": datetime.now().isoformat(),
        "email": notification.email,
        "task": notification.task,
        "round": notification.round,
        "nonce": notification.nonce,
        "repo_url": notification.repo_url,
        "commit_sha": notification.commit_sha,
        "pages_url": notification.pages_url,
        "status": "received"
    }
    
    deployments.append(deployment)
    
    # Save to file for persistence
    save_deployments()
    
    return {
        "status": "ok",
        "message": "Deployment received and queued for evaluation",
        "deployment_id": len(deployments) - 1
    }

@app.get("/deployments")
async def get_deployments():
    """Get all received deployments"""
    return {
        "total": len(deployments),
        "deployments": deployments
    }

@app.get("/deployments/{email}")
async def get_deployments_by_email(email: str):
    """Get deployments for specific student"""
    student_deployments = [d for d in deployments if d["email"] == email]
    return {
        "email": email,
        "total": len(student_deployments),
        "deployments": student_deployments
    }

@app.get("/deployments/task/{task}")
async def get_deployments_by_task(task: str):
    """Get deployments for specific task"""
    task_deployments = [d for d in deployments if d["task"] == task]
    return {
        "task": task,
        "total": len(task_deployments),
        "deployments": task_deployments
    }

@app.post("/evaluate")
async def evaluate_deployment(result: EvaluationResult):
    """
    Store evaluation results
    Instructors call this endpoint to store check results
    """
    evaluation = {
        "timestamp": datetime.now().isoformat(),
        "email": result.email,
        "task": result.task,
        "round": result.round,
        "repo_url": result.repo_url,
        "commit_sha": result.commit_sha,
        "pages_url": result.pages_url,
        "check": result.check,
        "score": result.score,
        "reason": result.reason,
        "logs": result.logs
    }
    
    print(f"\n✅ Evaluation Result:")
    print(f"   Email: {result.email}")
    print(f"   Task: {result.task}")
    print(f"   Check: {result.check}")
    print(f"   Score: {result.score}/100")
    
    deployments.append(evaluation)
    save_deployments()
    
    return {
        "status": "ok",
        "message": "Evaluation result recorded"
    }

@app.post("/task")
async def create_task(task: TaskRequest):
    """
    Instructors send round 2 tasks
    Stored for analysis
    """
    task_data = {
        "timestamp": datetime.now().isoformat(),
        "email": task.email,
        "task": task.task,
        "round": task.round,
        "nonce": task.nonce,
        "brief": task.brief,
        "checks": task.checks,
        "evaluation_url": task.evaluation_url,
        "status": "created"
    }
    
    tasks.append(task_data)
    save_tasks()
    
    print(f"\n📋 New Task Created:")
    print(f"   Email: {task.email}")
    print(f"   Task: {task.task}")
    print(f"   Round: {task.round}")
    
    return {
        "status": "ok",
        "message": "Task created",
        "task_id": len(tasks) - 1
    }

@app.get("/tasks")
async def get_all_tasks():
    """Get all tasks"""
    return {
        "total": len(tasks),
        "tasks": tasks
    }

@app.get("/tasks/{email}")
async def get_tasks_by_email(email: str):
    """Get tasks for specific student"""
    student_tasks = [t for t in tasks if t["email"] == email]
    return {
        "email": email,
        "total": len(student_tasks),
        "tasks": student_tasks
    }

@app.get("/summary")
async def get_summary():
    """Get overall summary"""
    # Count by round
    round1_count = sum(1 for d in deployments if d.get("round") == 1)
    round2_count = sum(1 for d in deployments if d.get("round") == 2)
    
    # Count by status
    received_count = sum(1 for d in deployments if d.get("status") == "received")
    
    # Unique students
    unique_students = set(d["email"] for d in deployments)
    
    return {
        "total_deployments": len(deployments),
        "total_tasks": len(tasks),
        "round_1_deployments": round1_count,
        "round_2_deployments": round2_count,
        "received_deployments": received_count,
        "unique_students": len(unique_students),
        "student_emails": list(unique_students)
    }

@app.get("/export")
async def export_data():
    """Export all data as JSON"""
    return {
        "deployments": deployments,
        "tasks": tasks,
        "exported_at": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "evaluation-api"}

# Utility functions
def save_deployments():
    """Save deployments to file"""
    with open("deployments.json", "w") as f:
        json.dump(deployments, f, indent=2)

def save_tasks():
    """Save tasks to file"""
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)

def load_data():
    """Load data from files on startup"""
    global deployments, tasks
    
    if os.path.exists("deployments.json"):
        with open("deployments.json", "r") as f:
            deployments = json.load(f)
    
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as f:
            tasks = json.load(f)

# Load on startup
load_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)