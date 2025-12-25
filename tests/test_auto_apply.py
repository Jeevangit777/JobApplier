import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from job_applier.apply.dispatcher import auto_apply_jobs
from job_applier.search.models import JobPosting


class AutoApplyJobsTests(unittest.TestCase):
    def test_auto_apply_writes_log_entries(self):
        jobs = [
            JobPosting(
                title="Software Engineer",
                company="Acme",
                location="Remote",
                url="https://example.com/apply",
                source="test",
                description="",
                tags=[],
            )
        ]

        with TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "application_log.json"
            results = auto_apply_jobs(jobs, log_path=log_path, open_url=lambda _: True)

            self.assertTrue(log_path.exists())
            payload = json.loads(log_path.read_text())
            self.assertEqual(payload, results)
            self.assertEqual(results[0]["status"], "opened")


if __name__ == "__main__":
    unittest.main()
