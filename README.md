# JobApplier

JobApplier is a CLI + web UI for searching public job boards and preparing
application packets (cover letters + summaries). It can open apply links in your
browser, but it does **not** submit applications on your behalf.

## Install

```bash
pip install -r requirements.txt
```

## CLI usage

Create a config file:

```bash
python -m job_applier init \
  --full-name "Jane Doe" \
  --email "jane@email.com" \
  --phone "123-456-7890" \
  --location "Edmonton, AB" \
  --website "https://example.com" \
  --resume-path "/path/to/resume.pdf" \
  --skills "C#" ".NET" "ASP.NET Core" \
  --roles "Software Developer" \
  --locations "Edmonton, AB"
```

Search jobs:

```bash
python -m job_applier search --query "Software Developer" --limit 20
```

Prepare application packets from a shortlist:

```bash
python -m job_applier apply --input shortlist.json
```

Auto-apply (opens apply URLs in your browser and logs results):

```bash
python -m job_applier apply --input shortlist.json --auto-apply
```

## Web UI

Run the web app locally:

```bash
python -m job_applier web --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000` in your browser.

To auto-apply from the UI, select jobs and check **Auto-apply** before
submitting. The server will open the apply links in your default browser and
log the results to `applications/application_log.json`.
