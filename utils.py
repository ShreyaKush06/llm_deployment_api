import os
import tempfile
import subprocess
import requests
from github import Github


def create_repo_and_deploy(data):
    email = data['email']
    task = data['task']
    nonce = data['nonce']
    brief = data['brief']
    eval_url = data['evaluation_url']
    attachments = data.get('attachments', [])

    gh = Github(os.getenv('GITHUB_TOKEN'))
    user = gh.get_user()

    # Create a unique repo name, safe for GitHub naming
    repo_name = f"{task}-{nonce}".replace(' ', '-').lower()[:30]

    # Create GitHub repo, public with MIT license
    repo = user.create_repo(repo_name, private=False, license_template='mit')

    # Create temporary folder to prepare repo files
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)

    # Create index.html with brief content (can enhance based on attachments)
    with open('index.html', 'w') as f:
        f.write(f"<html><body><h2>{brief}</h2></body></html>")

    # Create README.md
    with open('README.md', 'w') as f:
        f.write(f"# {task}\n\nThis app was automatically generated.\n\n**Brief:** {brief}")

    # Initialize git, add files, commit
    subprocess.run(['git', 'init'], check=True)
    subprocess.run(['git', 'config', 'user.email', email], check=True)
    subprocess.run(['git', 'config', 'user.name', user.login], check=True)
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)
    subprocess.run(['git', 'branch', '-M', 'main'], check=True)

    repo_url = f"https://github.com/{user.login}/{repo_name}.git"

    # Add remote and push to GitHub
    subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
    subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)

    # Enable GitHub Pages for the repo using GitHub CLI
    subprocess.run(['gh', 'api', f"repos/{user.login}/{repo_name}/pages", '-X', 'POST',
                    '-F', 'source[branch]=main', '-F', 'source[path]=/'] , check=True)

    pages_url = f"https://{user.login}.github.io/{repo_name}/"
    commit_sha = subprocess.getoutput('git rev-parse HEAD')

    # Notify evaluation API
    payload = {
        'email': email,
        'task': task,
        'round': data['round'],
        'nonce': nonce,
        'repo_url': repo_url,
        'commit_sha': commit_sha,
        'pages_url': pages_url
    }

    res = requests.post(eval_url, json=payload, headers={'Content-Type': 'application/json'})

    return {
        'status': 'success',
        'evaluation_response_status': res.status_code,
        'repo_url': repo_url,
        'pages_url': pages_url
    }
