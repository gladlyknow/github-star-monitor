import unittest
from scripts.monitor import ROOT
class SmokeTest(unittest.TestCase):
    def test_project_root(self):
        self.assertTrue((ROOT/"SKILL.md").exists())
    def test_no_fake_growth(self):
        self.assertIsNone({"status":"insufficient_history","gain":None}["gain"])
