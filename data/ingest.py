"""
data/ingest.py

Module Purpose:
----------------
Serves as primary data ingestion pipeline for the GitHub Issue Triage Engine.
It queries the GitHub REST API to fetch historical closed issues from target repository

Operational Features:
-----------------
* Handles authenticated GitHub API requests using Personal Access Token (PAT)
* Implements page-based pagination to handle API payload limits (per_page=100)
* Filters out pull requests to maintain dataset integrity for RAG and evaluation metrics
* Collects and previews genuine issue metadata before persisting record into PostgresSQL.
"""

"""
TODO:
* Pull the database issue 'number' to a set
* Before sending to database, check if it is present in set, if not, store it.
* Figure out how to map response to the entity 'issues' (Database table)
"""

import requests
import os
from dotenv import load_dotenv


def fetch_target_issues(target_count = 5, max_pages=10):
    repo_issues = []
    for page in range(1, max_pages + 1):
        parameters = {
            "state": "closed",
            "page": page,
            "per_page": 100,
            "sort": "created",
            "direction": "desc"
        }
        response = requests.get(URL, headers=header, params=parameters)  # API call with required params

        # break if response is not "successful" (200)
        if response.status_code != 200:
            break

        # store the response in a variable
        data = response.json()
        if not data:
            break

        for item in data:
            # filter all the PR and take only real issues
            if "pull_request" not in item:
                repo_issues.append(item)
                if len(repo_issues) >= target_count:
                    return repo_issues
    return repo_issues


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

GITHUB_OWNER = "langchain-ai"
REPO = "langchain"
URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{REPO}/issues"

header = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    header["Authorization"] = f"token {GITHUB_TOKEN}"

# making an API call
if __name__ == "__main__":
    print(f"Fetching clean issues from {GITHUB_OWNER}/{REPO}...")
    repoIssues = fetch_target_issues(target_count=5, max_pages=10)

    print(f"\nSuccessfully retrieved {len(repoIssues)} genuine issues:\n" + "-" * 60)

    # Formatted terminal output displaying ID, Title, and Created At timestamp
    for idx, issue in enumerate(repoIssues, start=1):
        print(f"Issue #{idx}")
        print(f"[number\t\t\t: {issue['id']}")
        print(f"title\t\t: {issue['title']}")
        print(f"body\t\t: {issue['body']}")
        print(f"state\t\t: {issue['state']}")
        print(f"created_at\t: {issue['created_at']}]")
        print(f"closed_at\t\t: {issue['closed_at']}")
        print(f"label\t\t: {issue['labels']}")
        break
        print("\n")