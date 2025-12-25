import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_CONFIG_PATH = Path.home() / ".job_applier" / "config.json"


@dataclass
class Profile:
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    resume_path: str = ""
    skills: List[str] = field(default_factory=list)


@dataclass
class Preferences:
    roles: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    remote_only: bool = True


@dataclass
class AppConfig:
    profile: Profile = field(default_factory=Profile)
    preferences: Preferences = field(default_factory=Preferences)
    cover_letter_template: str = (
        "Hello {hiring_manager},\n\n"
        "I am excited to apply for {job_title} at {company}. "
        "My background includes {skills_summary}. "
        "I'd love to discuss how I can help {company} with {problem_focus}.\n\n"
        "Regards,\n{full_name}"
    )


def _coerce_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def load_config(path: Optional[Path] = None) -> AppConfig:
    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return AppConfig()
    data = json.loads(config_path.read_text())
    profile_data = data.get("profile", {})
    preferences_data = data.get("preferences", {})
    return AppConfig(
        profile=Profile(
            full_name=str(profile_data.get("full_name", "")),
            email=str(profile_data.get("email", "")),
            phone=str(profile_data.get("phone", "")),
            location=str(profile_data.get("location", "")),
            website=str(profile_data.get("website", "")),
            resume_path=str(profile_data.get("resume_path", "")),
            skills=_coerce_list(profile_data.get("skills")),
        ),
        preferences=Preferences(
            roles=_coerce_list(preferences_data.get("roles")),
            locations=_coerce_list(preferences_data.get("locations")),
            remote_only=bool(preferences_data.get("remote_only", True)),
        ),
        cover_letter_template=str(
            data.get("cover_letter_template", AppConfig.cover_letter_template)
        ),
    )


def save_config(config: AppConfig, path: Optional[Path] = None) -> Path:
    config_path = path or DEFAULT_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "profile": {
            "full_name": config.profile.full_name,
            "email": config.profile.email,
            "phone": config.profile.phone,
            "location": config.profile.location,
            "website": config.profile.website,
            "resume_path": config.profile.resume_path,
            "skills": list(config.profile.skills),
        },
        "preferences": {
            "roles": list(config.preferences.roles),
            "locations": list(config.preferences.locations),
            "remote_only": config.preferences.remote_only,
        },
        "cover_letter_template": config.cover_letter_template,
    }
    config_path.write_text(json.dumps(payload, indent=2))
    return config_path


def update_from_env(config: AppConfig) -> AppConfig:
    config.profile.full_name = os.getenv("JOB_APPLIER_FULL_NAME", config.profile.full_name)
    config.profile.email = os.getenv("JOB_APPLIER_EMAIL", config.profile.email)
    config.profile.phone = os.getenv("JOB_APPLIER_PHONE", config.profile.phone)
    config.profile.location = os.getenv("JOB_APPLIER_LOCATION", config.profile.location)
    config.profile.website = os.getenv("JOB_APPLIER_WEBSITE", config.profile.website)
    config.profile.resume_path = os.getenv(
        "JOB_APPLIER_RESUME_PATH", config.profile.resume_path
    )
    return config
