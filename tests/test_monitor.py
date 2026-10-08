import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import monitor

class MonitorTests(unittest.TestCase):
    def test_root(self):
        self.assertTrue((monitor.ROOT / "SKILL.md").exists())

    def test_discovery(self):
        with patch.object(monitor, "api", return_value={"items":[{"full_name":"a/b"}]}) as api:
            self.assertEqual(monitor.discover(), ["a/b"])
            self.assertIn("/search/repositories", api.call_args.args[0])

    def test_collect_filters_forks(self):
        with patch.object(monitor, "api", return_value={"fork":True}):
            self.assertIsNone(monitor.collect("a/b", "2026-10-08T00:00:00+00:00"))

    def test_first_run_and_idempotency(self):
        with tempfile.TemporaryDirectory() as tmp:
            stamp="2026-10-08T01:00:00+00:00"
            sample={"id":1,"name":"a/b","url":"https://github.com/a/b","stars":100,"description":"test","language":"Python","readme_excerpt":"test","captured_at":stamp}
            with patch.object(monitor,"ROOT",Path(tmp)), patch.object(monitor,"discover",return_value=["a/b"]), patch.object(monitor,"collect",return_value=sample):
                monitor.run()
                files=list((Path(tmp)/"data/snapshots").glob("*.json"))
                self.assertEqual(len(files),1)
                self.assertIsNone(__import__("json").loads(files[0].read_text())["repositories"][0]["growth"]["gain"])
                original=files[0].read_text()
                monitor.run()
                self.assertEqual(files[0].read_text(),original)

if __name__ == "__main__":
    unittest.main()
