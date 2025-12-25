import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List

from job_applier.ai import generate_cover_letter
from job_applier.config import AppConfig
from job_applier.search.models import JobPosting


APPLICATIONS_DIR = Path("applications")


def _slugify(text: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in text).strip("-")


def save_shortlist(jobs: Iterable[JobPosting], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(job) for job in jobs]
    output_path.write_text(json.dumps(payload, indent=2))
    return output_path


def load_shortlist(input_path: Path) -> List[JobPosting]:
    data = json.loads(input_path.read_text())
    return [JobPosting(**item) for item in data]


def build_application_packets(
    config: AppConfig, jobs: Iterable[JobPosting], dry_run: bool
) -> List[Path]:
    packets: List[Path] = []
    for job in jobs:
        company_slug = _slugify(job.company or "company")
        title_slug = _slugify(job.title or "role")
        folder = APPLICATIONS_DIR / company_slug / title_slug
        if not dry_run:
            folder.mkdir(parents=True, exist_ok=True)
        cover_letter = generate_cover_letter(config, job)
        summary = (
            f"Company: {job.company}\n"
            f"Role: {job.title}\n"
            f"Location: {job.location}\n"
            f"Source: {job.source}\n"
            f"Apply URL: {job.url}\n"
        )
        if not dry_run:
            (folder / "cover_letter.txt").write_text(cover_letter)
            (folder / "summary.txt").write_text(summary)
        packets.append(folder)
    return packets
