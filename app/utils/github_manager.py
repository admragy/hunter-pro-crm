"""
GitHub Manager - إدارة GitHub مباشرة
OmniCRM / Hunter Pro CRM
Developer: admragy
"""

import os
import subprocess
from datetime import datetime
from typing import Dict, Optional, List
from github import Github
from github import InputGitTreeElement
import logging

logger = logging.getLogger(__name__)


class GitHubManager:
    """مدير GitHub لرفع التعديلات مباشرة"""

    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.username = os.getenv('GITHUB_USERNAME', 'admragy')
        self.repo_name = os.getenv('GITHUB_REPO', 'hunter-pro-crm')

        if not self.token:
            logger.warning("GITHUB_TOKEN not found in environment variables")
            self.github = None
            self.repo = None
        else:
            self.github = Github(self.token)
            try:
                self.repo = self.github.get_user().get_repo(self.repo_name)
            except:
                logger.warning(f"Repository {self.repo_name} not found")
                self.repo = None

    def get_file_content(self, file_path: str) -> str:
        """قراءة ملف من GitHub"""
        if not self.repo:
            return ""
        
        try:
            file = self.repo.get_contents(file_path)
            return file.decoded_content.decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting file {file_path}: {e}")
            return ""

    def update_file(self, file_path: str, content: str, message: str = None) -> Dict:
        """تعديل ملف على GitHub مباشرة"""
        if not self.repo:
            return {"status": "error", "message": "No repository connection"}
        
        try:
            file = self.repo.get_contents(file_path)
            
            self.repo.update_file(
                path=file_path,
                message=message or f"Updated {file_path} at {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                content=content,
                sha=file.sha
            )
            
            return {"status": "success", "file": file_path}
        except Exception as e:
            logger.error(f"Error updating file {file_path}: {e}")
            return {"status": "error", "message": str(e)}

    def create_file(self, file_path: str, content: str, message: str = None) -> Dict:
        """إنشاء ملف جديد على GitHub"""
        if not self.repo:
            return {"status": "error", "message": "No repository connection"}
        
        try:
            self.repo.create_file(
                path=file_path,
                message=message or f"Created {file_path} at {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                content=content
            )
            
            return {"status": "created", "file": file_path}
        except Exception as e:
            logger.error(f"Error creating file {file_path}: {e}")
            return {"status": "error", "message": str(e)}

    def commit_and_push(self, message: str = None, branch: str = 'main') -> Dict:
        """ترحيل وحفظ جميع التغييرات المحلية"""
        try:
            # إضافة جميع الملفات
            subprocess.run(['git', 'add', '.'], check=True)

            # إنشاء commit
            commit_message = message or f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)

            # رفع إلى GitHub
            subprocess.run(['git', 'push', 'origin', branch], check=True)

            return {
                "status": "success",
                "message": "All changes pushed to GitHub",
                "username": self.username,
                "repo": self.repo_name
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Error pushing to GitHub: {e}")
            return {"status": "error", "message": str(e)}

    def create_pull_request(
        self, 
        title: str, 
        body: str, 
        source_branch: str, 
        target_branch: str = 'main'
    ) -> Dict:
        """إنشاء طلب سحب"""
        if not self.repo:
            return {"status": "error", "message": "No repository connection"}
        
        try:
            # إنشاء Pull Request
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=source_branch,
                base=target_branch
            )
            
            return {
                "status": "created", 
                "pr_number": pr.number, 
                "url": pr.html_url
            }
        except Exception as e:
            logger.error(f"Error creating pull request: {e}")
            return {"status": "error", "message": str(e)}

    def get_repo_info(self) -> Dict:
        """معلومات المستودع"""
        if not self.repo:
            return {
                "error": "No repository connection",
                "username": self.username,
                "repo_name": self.repo_name
            }
        
        return {
            "name": self.repo.name,
            "full_name": self.repo.full_name,
            "url": self.repo.html_url,
            "default_branch": self.repo.default_branch,
            "stars": self.repo.stargazers_count,
            "forks": self.repo.forks_count,
            "open_issues": self.repo.open_issues_count,
            "description": self.repo.description
        }

    def list_branches(self) -> List[str]:
        """قائمة الفروع"""
        if not self.repo:
            return []
        
        try:
            branches = self.repo.get_branches()
            return [branch.name for branch in branches]
        except Exception as e:
            logger.error(f"Error listing branches: {e}")
            return []

    def create_branch(self, branch_name: str, source_branch: str = 'main') -> Dict:
        """إنشاء فرع جديد"""
        if not self.repo:
            return {"status": "error", "message": "No repository connection"}
        
        try:
            source = self.repo.get_branch(source_branch)
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source.commit.sha
            )
            
            return {
                "status": "created",
                "branch": branch_name,
                "source": source_branch
            }
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {e}")
            return {"status": "error", "message": str(e)}

    def get_latest_commit(self, branch: str = 'main') -> Dict:
        """آخر commit"""
        if not self.repo:
            return {"error": "No repository connection"}
        
        try:
            commits = self.repo.get_commits(sha=branch)
            latest = commits[0]
            
            return {
                "sha": latest.sha,
                "message": latest.commit.message,
                "author": latest.commit.author.name,
                "date": latest.commit.author.date.isoformat(),
                "url": latest.html_url
            }
        except Exception as e:
            logger.error(f"Error getting latest commit: {e}")
            return {"error": str(e)}


# استخدام بسيط
if __name__ == "__main__":
    manager = GitHubManager()
    
    # معلومات المستودع
    info = manager.get_repo_info()
    print(f"Repository: {info.get('full_name')}")
    print(f"Stars: {info.get('stars')}")
    
    # آخر commit
    commit = manager.get_latest_commit()
    print(f"Latest commit: {commit.get('message')}")
