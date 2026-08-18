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
from datetime import datetime
from src.db.models import IssueModel, SessionLocal


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

GITHUB_OWNER = "langchain-ai"
REPO = "langchain"
URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{REPO}/issues"

header = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    header["Authorization"] = f"token {GITHUB_TOKEN}"


def fetch_target_issues(target_count=50, max_pages=10):
    db = SessionLocal()
    try:
        existing_records = db.query(IssueModel.number).all()
        existing_ids = set(r[0] for r in existing_records)
        print(f"found {len(existing_ids)} existing records in database")
        print(existing_ids)

        integrated_count = 0
        for page in range(50, max_pages + 1):
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
                if "pull_request" in item:
                    continue
                if item["number"] in existing_ids:
                    continue

                #Parse date
                created_at_date = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))

                closed_at_date = (datetime.fromisoformat(item["closed_at"].replace("Z", "+00:00"))
                                                        if item.get("closed_at")
                                                        else None)
                # extract label names
                label_names = [label["name"] for label in item.get("labels", [])]
                issue_obj = IssueModel(
                    number = item["number"],
                    title = item["title"],
                    body = item.get("body"),
                    state = item["state"],
                    created_at = created_at_date,
                    closed_at = closed_at_date,
                    labels = label_names
                )
                db.add(issue_obj)
                existing_ids.add(item["number"])
                integrated_count += 1

                if integrated_count >= target_count:
                    break
            db.commit()
            print(f"Committed page {page}. Total issues integrated {integrated_count}")

            if integrated_count >= target_count:
                break

        print(f"Ingestion complete! Added {integrated_count} new issues")
    except Exception as e:
        db.rollback()
        print(f"Something went wrong: {e}")
    finally:
        db.close()

# making an API call
if __name__ == "__main__":
    print(f"Fetching clean issues from {GITHUB_OWNER}/{REPO}...")
    fetch_target_issues(target_count=470, max_pages=80)
