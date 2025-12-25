from dataclasses import dataclass
from typing import Optional


@dataclass
class JobPosting:
    source: str
    title: str
    company: str
    location: str
    url: str
    description: str
    tags: Optional[str] = None
