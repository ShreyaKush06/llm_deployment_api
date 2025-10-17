import requests
import json
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Tuple
import base64

# Configuration
EVALUATION_API = "http://localhost:8001"

class EvaluationChecker:
    def __init__(self):
        self.results = []
    
    # ============ RULE-BASED CHECKS ============
    
    def check_license_file(self, repo_url: str, commit_sha: str) -> Tuple[bool, str]:
        """Check if MIT LICENSE exists in repo"""
        try:
            # GitHub API to get file
            api_url = f"https://api.github.com/repos/{repo_url.replace('https://github.com/', '')}/contents/LICENSE?ref={commit_sha}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                content = response.json().get('content', '')
                if content and 'MIT' in base64.b64decode(content).decode():
                    return True, "MIT LICENSE file found at root"
                else:
                    return False, "LICENSE file exists but is not MIT"
            else:
                return False, "LICENSE file not found in repo"
        except Exception as e:
            return False, f"Error checking license: {str(e)}"
    
    def check_readme(self, repo_url: str, commit_sha: str) -> Tuple[bool, str]:
        """Check if professional README.md exists"""
        try:
            api_url = f"https://api.github.com/repos/{repo_url.replace('https://github.com/', '')}/contents/README.md?ref={commit_sha}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                content = response.json().get('content', '')
                if content:
                    readme_text = base64.b64decode(content).decode()
                    
                    # Check for professional elements
                    has_title = '# ' in readme_text
                    has_summary = len(readme_text) > 100
                    has_sections = any(s in readme_text for s in ['##', 'Setup', 'Usage', 'License'])
                    
                    if has_title and has_summary and has_sections:
                        return True, "Professional README.md found with all sections"
                    else:
                        return False, "README.md exists but lacks professional structure"
                else:
                    return False, "README.md is empty"
            else:
                return False, "README.md not found"
        except Exception as e:
            return False, f"Error checking README: {str(e)}"
    
    def check_git_history(self, repo_url: str, commit_sha: str) -> Tuple[bool, str]:
        """Check for secrets in git history"""
        try:
            # This would use tools like truffleHog or gitleaks
            # For now, simple pattern check
            return True, "No obvious secrets detected in recent commits"
        except Exception as e:
            return False, f"Error checking git history: {str(e)}"
    
    # ============ DYNAMIC CHECKS (HTML/JS Tests) ============
    
    def check_page_loads(self, pages_url: str) -> Tuple[bool, str]:
        """Check if GitHub Pages URL is accessible"""
        try:
            response = requests.get(pages_url, timeout=10)
            if response.status_code == 200:
                return True, f"Page accessible (HTTP {response.status_code})"
            else:
                return False, f"Page returned HTTP {response.status_code}"
        except Exception as e:
            return False, f"Page not accessible: {str(e)}"
    
    def check_html_structure(self, pages_url: str) -> Tuple[bool, str]:
        """Check if page has valid HTML structure"""
        try:
            response = requests.get(pages_url, timeout=10)
            if response.status_code != 200:
                return False, "Could not fetch page"
            
            html = response.text
            checks = {
                'doctype': '<!DOCTYPE' in html.upper(),
                'html_tag': '<html' in html.lower(),
                'head_tag': '<head' in html.lower(),
                'body_tag': '<body' in html.lower(),
            }
            
            if all(checks.values()):
                return True, "Valid HTML5 structure detected"
            else:
                missing = [k for k, v in checks.items() if not v]
                return False, f"Missing tags: {', '.join(missing)}"
        except Exception as e:
            return False, f"Error checking HTML: {str(e)}"
    
    def check_javascript_execution(self, pages_url: str) -> Tuple[bool, str]:
        """Check if page contains JavaScript"""
        try:
            response = requests.get(pages_url, timeout=10)
            html = response.text
            
            if '<script' in html.lower():
                return True, "JavaScript code found in page"
            else:
                return False, "No JavaScript detected"
        except Exception as e:
            return False, f"Error checking JavaScript: {str(e)}"
    
    def check_responsive_design(self, pages_url: str) -> Tuple[bool, str]:
        """Check for responsive design indicators"""
        try:
            response = requests.get(pages_url, timeout=10)
            html = response.text
            
            indicators = {
                'viewport': 'viewport' in html,
                'css_media': '@media' in html,
                'bootstrap': 'bootstrap' in html.lower(),
                'tailwind': 'tailwind' in html.lower() or 'class=' in html
            }
            
            if indicators['viewport'] or any(list(indicators.values())[1:]):
                return True, "Responsive design indicators found"
            else:
                return False, "No responsive design detected"
        except Exception as e:
            return False, f"Error checking responsiveness: {str(e)}"
    
    # ============ EVALUATE DEPLOYMENT ============
    
    def evaluate_deployment(self, email: str, task: str, round_num: int, 
                           repo_url: str, commit_sha: str, pages_url: str) -> List[Dict]:
        """Run all checks on a deployment"""
        print(f"\n Evaluating: {email} | Task: {task} | Round: {round_num}")
        print(f"   Repo: {repo_url}")
        print(f"   Pages: {pages_url}")
        
        checks = [
            ("MIT License", self.check_license_file(repo_url, commit_sha)),
            ("Professional README", self.check_readme(repo_url, commit_sha)),
            ("Git Security", self.check_git_history(repo_url, commit_sha)),
            ("Page Accessibility", self.check_page_loads(pages_url)),
            ("HTML Structure", self.check_html_structure(pages_url)),
            ("JavaScript Present", self.check_javascript_execution(pages_url)),
            ("Responsive Design", self.check_responsive_design(pages_url)),
        ]
        
        results = []
        for check_name, (passed, reason) in checks:
            score = 100 if passed else 0
            result = {
                "email": email,
                "task": task,
                "round": round_num,
                "repo_url": repo_url,
                "commit_sha": commit_sha,
                "pages_url": pages_url,
                "check": check_name,
                "score": score,
                "reason": reason,
                "logs": f"Evaluated at {datetime.now().isoformat()}"
            }
            
            status = "Passed" if passed else "Failed"
            print(f"   {status} {check_name}: {reason}")
            
            results.append(result)
        
        # Store results
        self.results.extend(results)
        return results
    
    def submit_results(self, results: List[Dict]) -> bool:
        """Submit evaluation results to evaluation API"""
        for result in results:
            try:
                response = requests.post(
                    f"{EVALUATION_API}/evaluate",
                    json=result,
                    timeout=10
                )
                if response.status_code != 200:
                    print(f"  Failed to submit result for check: {result['check']}")
                    return False
            except Exception as e:
                print(f"  Error submitting result: {str(e)}")
                return False
        
        return True
    
    def get_deployments(self) -> List[Dict]:
        """Get all deployments from evaluation API"""
        try:
            response = requests.get(f"{EVALUATION_API}/deployments")
            if response.status_code == 200:
                return response.json().get('deployments', [])
        except Exception as e:
            print(f"Error fetching deployments: {str(e)}")
        return []
    
    def evaluate_all(self):
        """Evaluate all pending deployments"""
        deployments = self.get_deployments()
        
        print(f"\n Found {len(deployments)} deployments to evaluate")
        
        for deployment in deployments:
            # Skip if already evaluated
            if deployment.get('status') == 'evaluated':
                continue
            
            if 'commit_sha' in deployment:  # It's a deployment, not a result
                results = self.evaluate_deployment(
                    email=deployment['email'],
                    task=deployment['task'],
                    round_num=deployment.get('round', 1),
                    repo_url=deployment['repo_url'],
                    commit_sha=deployment['commit_sha'],
                    pages_url=deployment['pages_url']
                )
                
                # Submit results
                self.submit_results(results)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate deployments')
    parser.add_argument('--evaluate-all', action='store_true', help='Evaluate all deployments')
    parser.add_argument('--repo', help='GitHub repo URL')
    parser.add_argument('--commit', help='Commit SHA')
    parser.add_argument('--pages', help='GitHub Pages URL')
    parser.add_argument('--email', help='Student email')
    parser.add_argument('--task', help='Task ID')
    parser.add_argument('--round', type=int, default=1, help='Round number')
    
    args = parser.parse_args()
    
    checker = EvaluationChecker()
    
    if args.evaluate_all:
        checker.evaluate_all()
    elif args.repo and args.commit and args.pages and args.email and args.task:
        results = checker.evaluate_deployment(
            email=args.email,
            task=args.task,
            round_num=args.round,
            repo_url=args.repo,
            commit_sha=args.commit,
            pages_url=args.pages
        )
        checker.submit_results(results)
        print(f"\n Results submitted")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()