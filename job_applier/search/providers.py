from typing import Callable, Dict, List

from job_applier.search.models import JobPosting
from job_applier.search.remotive import search_remotive
from job_applier.search.arbeitnow import search_arbeitnow


SearchFn = Callable[[str, int], List[JobPosting]]


PROVIDERS: Dict[str, SearchFn] = {
    "remotive": search_remotive,
    "arbeitnow": search_arbeitnow,
}


def search_all(query: str, limit: int) -> List[JobPosting]:
    results: List[JobPosting] = []
    per_provider = max(1, limit // max(1, len(PROVIDERS)))
    for name, provider in PROVIDERS.items():
        try:
            results.extend(provider(query, per_provider))
        except Exception as exc:  # noqa: BLE001 - we want resilience
            results.append(
                JobPosting(
                    source=name,
                    title="",
                    company="",
                    location="",
                    url="",
                    description=f"Provider error: {exc}",
                )
            )
    return results[:limit]
