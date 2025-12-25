from typing import List

import requests

from job_applier.search.models import JobPosting


API_URL = "https://remotive.com/api/remote-jobs"


def search_remotive(query: str, limit: int) -> List[JobPosting]:
    response = requests.get(API_URL, params={"search": query}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    jobs = []
    for job in payload.get("jobs", [])[:limit]:
        jobs.append(
            JobPosting(
                source="remotive",
                title=job.get("title", ""),
                company=job.get("company_name", ""),
                location=job.get("candidate_required_location", ""),
                url=job.get("url", ""),
                description=job.get("description", ""),
                tags=", ".join(job.get("tags", []) or []),
            )
        )
    return jobs
