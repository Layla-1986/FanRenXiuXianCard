import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class CurrentModelsUsageParserTest(unittest.TestCase):
    def test_accepts_model_credits_and_current_limit_labels(self):
        fixture = {
            "modelsPage": True,
            "controls": [
                {"name": "Model Credits", "top": 0, "left": 0},
                {"name": "Available AI Credits: 0", "top": 20, "left": 0},
                {"name": "Gemini Models", "top": 80, "left": 0},
                {"name": "Weekly Limit Remaining", "top": 100, "left": 0},
                {"name": "You have used some of your weekly limit, it will fully refresh in 6 days, 19 hours.", "top": 112, "left": 0},
                {"name": "99%", "top": 100, "left": 180},
                {"name": "Five Hour Limit Remaining", "top": 130, "left": 0},
                {"name": "You have used some of your 5-hour limit, it will fully refresh in 14 minutes.", "top": 142, "left": 0},
                {"name": "94%", "top": 130, "left": 180},
                {"name": "Claude and GPT models", "top": 190, "left": 0},
                {"name": "Weekly Limit Remaining", "top": 210, "left": 0},
                {"name": "You have used some of your weekly limit, it will fully refresh in 6 days, 19 hours.", "top": 222, "left": 0},
                {"name": "78%", "top": 210, "left": 180},
                {"name": "Five Hour Limit Remaining", "top": 240, "left": 0},
                {"name": "100%", "top": 240, "left": 180},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            fixture_path = Path(directory) / "quota-fixture.json"
            fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
            completed = subprocess.run(
                [
                    "powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive",
                    "-ExecutionPolicy", "Bypass", "-File",
                    str(Path(__file__).resolve().parents[1] / "scripts" / "collect_antigravity_quota.ps1"),
                    "-FixturePath", str(fixture_path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(
            {
                "aiCredits": 0,
                "gemini": {"weeklyRemaining": 99, "fiveHourRemaining": 94, "weeklyReset": "6 days, 19 hours", "fiveHourReset": "14 minutes"},
                "claudeGpt": {"weeklyRemaining": 78, "fiveHourRemaining": 100, "weeklyReset": "6 days, 19 hours", "fiveHourReset": None},
            },
            json.loads(completed.stdout),
        )


if __name__ == "__main__":
    unittest.main()
