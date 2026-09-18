import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloud_compliance_analyzer import analyze, evaluate


class ComplianceAnalyzerTests(unittest.TestCase):
    def test_missing_high_is_critical(self):
        row = {"evidence_status":"missing","criticality":"high","next_review_date":""}
        result = evaluate(row, date(2026, 9, 12))
        self.assertEqual(result["risk_score"], 15)
        self.assertEqual(result["risk_rating"], "Critical")

    def test_expired_current_becomes_stale(self):
        row = {"evidence_status":"current","criticality":"medium","next_review_date":"2026-09-01"}
        result = evaluate(row, date(2026, 9, 12))
        self.assertEqual(result["normalized_status"], "Stale")

    def test_outputs_created(self):
        source = Path(__file__).resolve().parents[1] / "data" / "sample_evidence_inventory.csv"
        with tempfile.TemporaryDirectory() as tmp:
            rows, poam = analyze(source, Path(tmp), date(2026, 9, 12))
            self.assertEqual(len(rows), 10)
            self.assertGreater(len(poam), 0)
            for name in ["gap_report.csv", "poam.csv", "monitoring_summary.html"]:
                self.assertTrue((Path(tmp) / name).exists())


if __name__ == "__main__":
    unittest.main()
