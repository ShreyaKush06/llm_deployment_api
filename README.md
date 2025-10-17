# LLM Code Deployment API

FastAPI-based system for automated HTML/CSS/JS generation and deployment using LLM.

## Features
- Automated code generation from natural language briefs
- GitHub repository creation and deployment
- GitHub Pages hosting
- Round-based evaluation system
- Revision handling

## Tech Stack
- FastAPI
- Python 3.8+
- aipipe API (OpenAI-compatible)
- GitHub API
- SQLite

## Setup

### Prerequisites
- Python 3.8+
- GitHub account
- GitHub Personal Access Token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/llm-deployment-api.git
cd llm-deployment-api
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export GITHUB_TOKEN="your_github_token"
export GITHUB_USERNAME="your_github_username"
export STUDENT_SECRET="your_unique_secret"
export EVALUATION_URL="http://localhost:8001/notify"
```

5. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /health
```

### Deploy Code
```bash
POST /deploy
Content-Type: application/json

{
  "email": "your@email.com",
  "task": "Create a responsive portfolio website",
  "round": 1,
  "nonce": "unique_string",
  "attachments": []
}
```

## Testing

Run the test suite:
```bash
python full_test.py
```

## Deployment

See deployment instructions for Railway, Render, or other platforms in the documentation.

## License
MIT License
