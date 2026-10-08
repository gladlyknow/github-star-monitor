import unittest
from unittest.mock import patch
from scripts.intelligence import classify, render, translate

class IntelligenceTests(unittest.TestCase):
    def test_classify_security(self):
        self.assertEqual(classify({"description":"security audit scanner"})["area"],"代码安全与合规")
    def test_fallback_no_key(self):
        with patch.dict("os.environ",{},clear=True):
            self.assertEqual(translate([{"name":"a/b"}]),{})
    def test_markdown_first_day(self):
        snap={"captured_at":"2026-10-08T01:00:00+00:00","repositories":[{"name":"a/b","url":"https://github.com/a/b","stars":120,"description":"security audit scanner","growth":{"status":"insufficient_history","gain":None}}]}
        with patch.dict("os.environ",{},clear=True):
            report=render(snap)
        self.assertIn("无可比历史",report)
        self.assertIn("SaaS",report)
        self.assertIn("尚未翻译",report)

if __name__=="__main__":unittest.main()
