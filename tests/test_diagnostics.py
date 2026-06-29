import unittest
from unittest.mock import patch

from portforge.diagnostics import collect_diagnostics, format_diagnostics_report


class DiagnosticsTest(unittest.TestCase):
    def test_collect_diagnostics_marks_ready_when_required_tools_exist(self):
        def fake_which(name):
            return f"/usr/bin/{name}"

        with patch("portforge.diagnostics.platform.system", return_value="Linux"), patch(
            "portforge.diagnostics.platform.release", return_value="6.0"
        ), patch("portforge.diagnostics.platform.machine", return_value="x86_64"), patch(
            "portforge.diagnostics.shutil.which", side_effect=fake_which
        ):
            diagnostics = collect_diagnostics()

        self.assertTrue(diagnostics.ready)
        self.assertTrue(diagnostics.has_port_checker)
        self.assertEqual(diagnostics.system, "Linux")

    def test_collect_diagnostics_reports_missing_port_checker(self):
        def fake_which(name):
            if name == "ps":
                return "/bin/ps"
            return None

        with patch("portforge.diagnostics.platform.system", return_value="Linux"), patch(
            "portforge.diagnostics.platform.release", return_value="6.0"
        ), patch("portforge.diagnostics.platform.machine", return_value="x86_64"), patch(
            "portforge.diagnostics.shutil.which", side_effect=fake_which
        ):
            diagnostics = collect_diagnostics()

        self.assertFalse(diagnostics.ready)
        self.assertFalse(diagnostics.has_port_checker)
        self.assertIn("Install lsof or ss", " ".join(diagnostics.to_dict()["notes"]))

    def test_format_diagnostics_report_includes_platform_and_notes(self):
        def fake_which(name):
            return None

        with patch("portforge.diagnostics.platform.system", return_value="Darwin"), patch(
            "portforge.diagnostics.platform.release", return_value="25.0"
        ), patch("portforge.diagnostics.platform.machine", return_value="arm64"), patch(
            "portforge.diagnostics.shutil.which", side_effect=fake_which
        ):
            report = format_diagnostics_report(collect_diagnostics())

        self.assertIn("PortForge diagnostics", report)
        self.assertIn("Platform: Darwin 25.0 (arm64)", report)
        self.assertIn("Ready: no", report)
        self.assertIn("lsof", report)
        self.assertIn("ss", report)
        self.assertIn("macOS", report)


if __name__ == "__main__":
    unittest.main()
