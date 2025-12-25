import argparse
from pathlib import Path
from typing import List

from job_applier.apply.dispatcher import (
    build_application_packets,
    auto_apply_jobs,
    load_shortlist,
    save_shortlist,
)
from job_applier.config import AppConfig, load_config, save_config, update_from_env
from job_applier.search.models import JobPosting
from job_applier.search.providers import PROVIDERS, search_all
from job_applier.web import create_app


def _print_jobs(jobs: List[JobPosting]) -> None:
    for index, job in enumerate(jobs, start=1):
        print(f"{index}. {job.title} @ {job.company} ({job.location})")
        print(f"   Source: {job.source}")
        print(f"   Apply: {job.url}")
        if job.tags:
            print(f"   Tags: {job.tags}")
        if job.description:
            print(f"   Description: {job.description[:200].strip()}...")
        print()


def cmd_init(args: argparse.Namespace) -> None:
    config = AppConfig()
    config.profile.full_name = args.full_name
    config.profile.email = args.email
    config.profile.phone = args.phone
    config.profile.location = args.location
    config.profile.website = args.website
    config.profile.resume_path = args.resume_path
    config.profile.skills = args.skills or []
    config.preferences.roles = args.roles or []
    config.preferences.locations = args.locations or []
    if args.remote_only is True:
        config.preferences.remote_only = True
    elif args.no_remote_only is True:
        config.preferences.remote_only = False
    config_path = save_config(config, Path(args.config_path))
    print(f"Config saved to {config_path}")


def cmd_search(args: argparse.Namespace) -> None:
    config = update_from_env(load_config(Path(args.config_path)))
    query = args.query or " ".join(config.preferences.roles) or "software"
    limit = args.limit
    if args.provider:
        provider = PROVIDERS.get(args.provider)
        if not provider:
            raise SystemExit(
                f"Unknown provider {args.provider}. Available: {', '.join(PROVIDERS)}"
            )
        jobs = provider(query, limit)
    else:
        jobs = search_all(query, limit)
    if args.output:
        save_shortlist(jobs, Path(args.output))
        print(f"Saved {len(jobs)} jobs to {args.output}")
    else:
        _print_jobs(jobs)


def cmd_apply(args: argparse.Namespace) -> None:
    config = update_from_env(load_config(Path(args.config_path)))
    jobs = load_shortlist(Path(args.input))
    if not jobs:
        print("No jobs found in shortlist.")
        return
    packets = build_application_packets(config, jobs, dry_run=args.dry_run)
    print("Prepared application packets:")
    for packet in packets:
        print(f"- {packet}")
    if args.dry_run:
        print("Dry run enabled; no files were written.")
    if args.auto_apply:
        results = auto_apply_jobs(jobs)
        print("Auto-apply results:")
        for entry in results:
            status = entry.get("status")
            print(f"- {entry.get('title')} @ {entry.get('company')} [{status}]")


def cmd_show_config(args: argparse.Namespace) -> None:
    config = update_from_env(load_config(Path(args.config_path)))
    print("Profile:")
    print(f"  Name: {config.profile.full_name}")
    print(f"  Email: {config.profile.email}")
    print(f"  Phone: {config.profile.phone}")
    print(f"  Location: {config.profile.location}")
    print(f"  Website: {config.profile.website}")
    print(f"  Resume: {config.profile.resume_path}")
    print(f"  Skills: {', '.join(config.profile.skills)}")
    print("Preferences:")
    print(f"  Roles: {', '.join(config.preferences.roles)}")
    print(f"  Locations: {', '.join(config.preferences.locations)}")
    print(f"  Remote only: {config.preferences.remote_only}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "JobApplier - search public job boards and prepare application packets. "
            "This tool does not auto-submit applications; review each job before applying."
        )
    )
    parser.add_argument(
        "--config-path",
        default=str(Path.home() / ".job_applier" / "config.json"),
        help="Path to the config JSON file.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a config file.")
    init_parser.add_argument("--full-name", default="")
    init_parser.add_argument("--email", default="")
    init_parser.add_argument("--phone", default="")
    init_parser.add_argument("--location", default="")
    init_parser.add_argument("--website", default="")
    init_parser.add_argument("--resume-path", default="")
    init_parser.add_argument("--skills", nargs="*")
    init_parser.add_argument("--roles", nargs="*")
    init_parser.add_argument("--locations", nargs="*")
    remote_group = init_parser.add_mutually_exclusive_group()
    remote_group.add_argument("--remote-only", action="store_true", default=None)
    remote_group.add_argument("--no-remote-only", action="store_true", default=None)
    init_parser.set_defaults(func=cmd_init)

    search_parser = subparsers.add_parser("search", help="Search job boards.")
    search_parser.add_argument("--query", default="")
    search_parser.add_argument("--limit", type=int, default=20)
    search_parser.add_argument("--provider", default="")
    search_parser.add_argument("--output", help="Save results to JSON file.")
    search_parser.set_defaults(func=cmd_search)

    apply_parser = subparsers.add_parser(
        "apply", help="Prepare application packets from a shortlist."
    )
    apply_parser.add_argument("--input", required=True, help="Path to shortlist JSON.")
    apply_parser.add_argument("--dry-run", action="store_true")
    apply_parser.add_argument(
        "--auto-apply",
        action="store_true",
        help="Open apply URLs in your browser and write a log file.",
    )
    apply_parser.set_defaults(func=cmd_apply)

    show_parser = subparsers.add_parser("config", help="Show loaded config.")
    show_parser.set_defaults(func=cmd_show_config)

    web_parser = subparsers.add_parser("web", help="Run the web UI.")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=8000)
    web_parser.set_defaults(
        func=lambda args: create_app().run(host=args.host, port=args.port, debug=False)
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
