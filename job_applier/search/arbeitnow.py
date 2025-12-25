from typing import List

import requests

from job_applier.search.models import JobPosting


API_URL = "https://www.arbeitnow.com/api/job-board-api"


def search_arbeitnow(query: str, limit: int) -> List[JobPosting]:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    payload = response.json()
    jobs = []
    query_lower = query.lower()
    for job in payload.get("data", []):
        title = job.get("title", "")
        company = job.get("company_name", "")
        if query_lower not in title.lower() and query_lower not in company.lower():
            continue
        jobs.append(
            JobPosting(
                source="arbeitnow",
                title=title,
                company=company,
                location=job.get("location", ""),
                url=job.get("url", ""),
                description=job.get("description", ""),
                tags=", ".join(job.get("tags", []) or []),
            )
        )
        if len(jobs) >= limit:
            break
    return jobs
