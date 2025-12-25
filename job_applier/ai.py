import os
from typing import Dict

import requests

from job_applier.config import AppConfig
from job_applier.search.models import JobPosting


OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _fallback_cover_letter(config: AppConfig, job: JobPosting) -> str:
    skills_summary = ", ".join(config.profile.skills) or "relevant experience"
    return config.cover_letter_template.format(
        hiring_manager="Hiring Manager",
        job_title=job.title or "the role",
        company=job.company or "your company",
        skills_summary=skills_summary,
        problem_focus="delivering impact",
        full_name=config.profile.full_name or "",
    )


def generate_cover_letter(config: AppConfig, job: JobPosting) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_cover_letter(config, job)

    prompt = (
        "Write a concise, tailored cover letter for the role below. "
        "Use the candidate profile and keep it under 200 words.\n\n"
        f"Job Title: {job.title}\n"
        f"Company: {job.company}\n"
        f"Location: {job.location}\n"
        f"Description: {job.description[:1500]}\n\n"
        f"Candidate: {config.profile.full_name}\n"
        f"Skills: {', '.join(config.profile.skills)}\n"
        f"Resume: {config.profile.resume_path}\n"
    )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, object] = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": "You are a helpful career assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 400,
    }
    response = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=45)
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        return _fallback_cover_letter(config, job)
    return choices[0]["message"]["content"].strip()
