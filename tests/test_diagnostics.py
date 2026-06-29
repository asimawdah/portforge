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
        self.assertTrue(diagnostics.supported_platform)
        self.assertEqual(diagnostics.system, "Linux")
        self.assertEqual(diagnostics.active_backend, "lsof")
        self.assertEqual(diagnostics.missing_required_tools, [])

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
        self.assertIsNone(diagnostics.active_backend)
        payload = diagnostics.to_dict()
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["lookup_scope"], "listening_tcp_ports")
        self.assertTrue(payload["supported_platform"])
        self.assertIn("Install lsof or ss", " ".join(payload["notes"]))
        self.assertIn("Install lsof or iproute2/ss", " ".join(payload["recommended_actions"]))
        self.assertEqual(payload["missing_port_check_tools"], ["lsof", "ss"])

    def test_collect_diagnostics_uses_ss_when_lsof_is_missing(self):
        def fake_which(name):
            if name == "lsof":
                return None
            return f"/usr/bin/{name}"

        with patch("portforge.diagnostics.platform.system", return_value="Linux"), patch(
            "portforge.diagnostics.platform.release", return_value="6.0"
        ), patch("portforge.diagnostics.platform.machine", return_value="x86_64"), patch(
            "portforge.diagnostics.shutil.which", side_effect=fake_which
        ):
            diagnostics = collect_diagnostics()

        self.assertTrue(diagnostics.ready)
        self.assertEqual(diagnostics.active_backend, "ss")
        self.assertEqual(diagnostics.missing_port_check_tools, ["lsof"])

    def test_unsupported_platform_is_not_ready_even_when_tools_exist(self):
        def fake_which(name):
            return f"/usr/bin/{name}"

        with patch("portforge.diagnostics.platform.system", return_value="Windows"), patch(
            "portforge.diagnostics.platform.release", return_value="11"
        ), patch("portforge.diagnostics.platform.machine", return_value="AMD64"), patch(
            "portforge.diagnostics.shutil.which", side_effect=fake_which
        ):
            diagnostics = collect_diagnostics()

        payload = diagnostics.to_dict()
        self.assertFalse(diagnostics.ready)
        self.assertFalse(diagnostics.supported_platform)
        self.assertFalse(payload["supported_platform"])
        self.assertIn("WSL", " ".join(payload["recommended_actions"]))

    def test_format_diagnostics_report_includes_platform_notes_and_actions(self):
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
        self.assertIn("Supported platform: yes", report)
        self.assertIn("Ready: no", report)
        self.assertIn("Lookup scope: listening_tcp_ports", report)
        self.assertIn("Active backend: none", report)
        self.assertIn("lsof", report)
        self.assertIn("ss", report)
        self.assertIn("macOS", report)
        self.assertIn("Recommended actions", report)


if __name__ == "__main__":
    unittest.main()
