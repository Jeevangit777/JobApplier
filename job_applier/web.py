import json
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import List

from flask import Flask, render_template, request

from job_applier.apply.dispatcher import auto_apply_jobs, build_application_packets
from job_applier.config import AppConfig, load_config, save_config, update_from_env
from job_applier.search.models import JobPosting
from job_applier.search.providers import PROVIDERS, search_all


DATA_DIR = Path(".job_applier_web")
CONFIG_DIR = DATA_DIR / "configs"
RESUME_DIR = DATA_DIR / "resumes"


def _ensure_dirs() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    RESUME_DIR.mkdir(parents=True, exist_ok=True)


def _parse_list(raw_value: str) -> List[str]:
    if not raw_value:
        return []
    items = [item.strip() for item in raw_value.replace("\n", ",").split(",")]
    return [item for item in items if item]


def _build_config(form: dict, resume_path: str) -> AppConfig:
    config = AppConfig()
    config.profile.full_name = form.get("full_name", "")
    config.profile.email = form.get("email", "")
    config.profile.phone = form.get("phone", "")
    config.profile.location = form.get("location", "")
    config.profile.website = form.get("website", "")
    config.profile.resume_path = resume_path
    config.profile.skills = _parse_list(form.get("skills", ""))
    config.preferences.roles = _parse_list(form.get("roles", ""))
    config.preferences.locations = _parse_list(form.get("locations", ""))
    config.preferences.remote_only = form.get("remote_only") == "on"
    return config


def _save_config(config: AppConfig) -> str:
    config_id = uuid.uuid4().hex
    path = CONFIG_DIR / f"{config_id}.json"
    save_config(config, path)
    return config_id


def _load_config(config_id: str) -> AppConfig:
    return update_from_env(load_config(CONFIG_DIR / f"{config_id}.json"))


def _save_resume(file_storage) -> str:
    if not file_storage or not file_storage.filename:
        return ""
    filename = f"{uuid.uuid4().hex}_{Path(file_storage.filename).name}"
    destination = RESUME_DIR / filename
    file_storage.save(destination)
    return str(destination)


def _search_jobs(provider_key: str, query: str, limit: int) -> List[JobPosting]:
    if provider_key:
        provider = PROVIDERS.get(provider_key)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_key}")
        return provider(query, limit)
    return search_all(query, limit)


def _deserialize_jobs(payload: str) -> List[JobPosting]:
    data = json.loads(payload)
    return [JobPosting(**item) for item in data]


def create_app() -> Flask:
    _ensure_dirs()
    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def index():
        return render_template(
            "index.html",
            providers=PROVIDERS,
            jobs=None,
            packets=None,
            error=None,
        )

    @app.route("/search", methods=["POST"])
    def search():
        resume_path = _save_resume(request.files.get("resume"))
        config = _build_config(request.form, resume_path)
        config_id = _save_config(config)
        query = request.form.get("query", "")
        limit = int(request.form.get("limit", "20"))
        provider_key = request.form.get("provider", "")
        error = None
        jobs: List[JobPosting] = []
        try:
            jobs = _search_jobs(provider_key, query, limit)
        except ValueError as exc:
            error = str(exc)
        return render_template(
            "index.html",
            providers=PROVIDERS,
            jobs=jobs,
            jobs_payload=[asdict(job) for job in jobs] if jobs else [],
            config_id=config_id,
            packets=None,
            error=error,
        )

    @app.route("/apply", methods=["POST"])
    def apply():
        config_id = request.form.get("config_id", "")
        jobs_payload = request.form.get("jobs_payload", "")
        selected_indices = request.form.getlist("selected")
        jobs = _deserialize_jobs(jobs_payload) if jobs_payload else []
        selected = [
            job
            for index, job in enumerate(jobs)
            if str(index) in selected_indices
        ]
        config = _load_config(config_id) if config_id else AppConfig()
        packets = build_application_packets(config, selected, dry_run=False)
        apply_results = None
        if request.form.get("auto_apply") == "on":
            apply_results = auto_apply_jobs(selected)
        return render_template(
            "index.html",
            providers=PROVIDERS,
            jobs=None,
            packets=packets,
            apply_results=apply_results,
            error=None,
        )

    return app
