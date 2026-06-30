import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from portforge.diagnostics import collect_diagnostics, detect_environment, format_diagnostics_report


class DiagnosticsTest(unittest.TestCase):
    def test_collect_diagnostics_marks_ready_when_required_tools_exist(self):
        def fake_which(name):
            return f"/usr/bin/{name}"

        with patch("portforge.diagnostics.platform.system", return_value="Linux"), patch(
            "portforge.diagnostics.platform.release", return_value="6.0"
        ), patch("portforge.diagnostics.platform.version", return_value="#1 SMP"), patch(
            "portforge.diagnostics.platform.machine", return_value="x86_64"
        ), patch("portforge.diagnostics.shutil.which", side_effect=fake_which), patch(
            "portforge.diagnostics.Path.read_text", side_effect=OSError
        ), patch("portforge.diagnostics.os.geteuid", return_value=0):
            diagnostics = collect_diagnostics()

        self.assertTrue(diagnostics.ready)
        self.assertTrue(diagnostics.has_port_checker)
        self.assertTrue(diagnostics.supported_platform)
        self.assertEqual(diagnostics.system, "Linux")
        self.assertEqual(diagnostics.environment, "native")
        self.assertFalse(diagnostics.is_wsl)
        self.assertEqual(diagnostics.status, "ready")
        self.assertEqual(diagnostics.failure_reasons, [])
        self.assertEqual(diagnostics.active_backend, "lsof")
        self.assertEqual(diagnostics.missing_required_tools, [])
        self.assertEqual(diagnostics.uid, 0)
        self.assertTrue(diagnostics.is_elevated)
        self.assertEqual(diagnostics.permission_scope, "elevated")

    def test_collect_diagnostics_reports_missing_port_checker(self):
        def fake_which(name):
            if name == "ps":
                return "/bin/ps"
            return None

        with patch("portforge.diagnostics.platform.system", return_value="Linux"), patch(
            "portforge.diagnostics.platform.release", return_value="6.0"
        ), patch("portforge.diagnostics.platform.version", return_value="#1 SMP"), patch(
            "portforge.diagnostics.platform.machine", return_value="x86_64"
        ), patch("portforge.diagnostics.shutil.which", side_effect=fake_which), patch(
            "portforge.diagnostics.Path.read_text", side_effect=OSError
        ), patch("portforge.diagnostics.os.geteuid", return_value=1000):
            diagnostics = collect_diagnostics()

        self.assertFalse(diagnostics.ready)
        self.assertFalse(diagnostics.has_port_checker)
        self.assertIsNone(diagnostics.active_backend)
        self.assertEqual(diagnostics.status, "degraded")
        self.assertEqual(diagnostics.failure_reasons, ["missing_port_check_backend"])
        payload = diagnostics.to_dict()
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["lookup_scope"], "listening_tcp_ports")
        self.assertEqual(payload["status"], "degraded")
        self.assertEqual(payload["environment"], "native")
        self.assertFalse(payload["is_wsl"])
        self.assertEqual(payload["uid"], 1000)
        self.assertFalse(payload["elevated"])
        self.assertEqual(payload["permission_scope"], "user")
        self.assertEqual(payload["failure_reasons"], ["missing_port_check_backend"])
        self.assertTrue(payload["supported_platform"])
        self.assertIn("Install lsof or ss", " ".join(payload["notes"]))
        self.assertIn("process names or owners", " ".join(payload["notes"]))
        self.assertIn("Install lsof or iproute2/ss", " ".join(payload["recommended_actions"]))
        self.assertIn("elevated permissions", " ".join(payload["recommended_actions"]))
        self.assertEqual(payload["missing_port_check_tools"], ["lsof", "ss"])

    def test_collect_diagnostics_uses_ss_when_lsof_is_missing(self):
        def fake_which(name):
            if name == "lsof":
                return None
            return f"/usr/bin/{name}"

        with patch("portforge.diagnostics.platform.system", return_value="Linux"), patch(
            "portforge.diagnostics.platform.release", return_value="6.0"
        ), patch("portforge.diagnostics.platform.version", return_value="#1 SMP"), patch(
            "portforge.diagnostics.platform.machine", return_value="x86_64"
        ), patch("portforge.diagnostics.shutil.which", side_effect=fake_which), patch(
            "portforge.diagnostics.Path.read_text", side_effect=OSError
        ):
            diagnostics = collect_diagnostics()

        self.assertTrue(diagnostics.ready)
        self.assertEqual(diagnostics.status, "ready")
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
        self.assertEqual(diagnostics.environment, "native")
        self.assertEqual(diagnostics.status, "unsupported")
        self.assertEqual(diagnostics.failure_reasons, ["unsupported_platform"])
        self.assertFalse(payload["supported_platform"])
        self.assertEqual(payload["status"], "unsupported")
        self.assertEqual(payload["failure_reasons"], ["unsupported_platform"])

    def test_missing_required_tool_is_reported_as_failure_reason(self):
        def fake_which(name):
            if name == "ps":
                return None
            return f"/usr/bin/{name}"

        with patch("portforge.diagnostics.platform.system", return_value="Linux"), patch(
            "portforge.diagnostics.platform.release", return_value="6.0"
        ), patch("portforge.diagnostics.platform.version", return_value="#1 SMP"), patch(
            "portforge.diagnostics.platform.machine", return_value="x86_64"
        ), patch("portforge.diagnostics.shutil.which", side_effect=fake_which), patch(
            "portforge.diagnostics.Path.read_text", side_effect=OSError
        ):
            diagnostics = collect_diagnostics()

        self.assertFalse(diagnostics.ready)
        self.assertEqual(diagnostics.status, "degraded")
        self.assertEqual(diagnostics.failure_reasons, ["missing_required_tools"])
        self.assertEqual(diagnostics.missing_required_tools, ["ps"])

    def test_detect_environment_marks_wsl_from_release_or_proc_version(self):
        self.assertEqual(detect_environment("Linux", "5.15.90.1-microsoft-standard-WSL2", "#1 SMP"), "wsl")

        with tempfile.TemporaryDirectory() as tmp:
            proc_version = Path(tmp) / "version"
            proc_version.write_text("Linux version with Microsoft WSL marker", encoding="utf-8")
            self.assertEqual(detect_environment("Linux", "6.0", "#1 SMP", proc_version), "wsl")

    def test_wsl_diagnostics_include_namespace_note_and_action(self):
        def fake_which(name):
            return f"/usr/bin/{name}"

        with patch("portforge.diagnostics.platform.system", return_value="Linux"), patch(
            "portforge.diagnostics.platform.release", return_value="5.15.90.1-microsoft-standard-WSL2"
        ), patch("portforge.diagnostics.platform.version", return_value="#1 SMP"), patch(
            "portforge.diagnostics.platform.machine", return_value="x86_64"
        ), patch("portforge.diagnostics.shutil.which", side_effect=fake_which):
            diagnostics = collect_diagnostics()

        payload = diagnostics.to_dict()
        self.assertEqual(payload["environment"], "wsl")
        self.assertTrue(payload["is_wsl"])
        self.assertIn("Linux/WSL network namespace", " ".join(payload["notes"]))
        self.assertIn("same WSL distro", " ".join(payload["recommended_actions"]))

    def test_format_diagnostics_report_includes_platform_notes_and_actions(self):
        def fake_which(name):
            return None

        with patch("portforge.diagnostics.platform.system", return_value="Darwin"), patch(
            "portforge.diagnostics.platform.release", return_value="25.0"
        ), patch("portforge.diagnostics.platform.machine", return_value="arm64"), patch(
            "portforge.diagnostics.shutil.which", side_effect=fake_which
        ), patch("portforge.diagnostics.os.geteuid", return_value=501):
            report = format_diagnostics_report(collect_diagnostics())

        self.assertIn("PortForge diagnostics", report)
        self.assertIn("Platform: Darwin 25.0 (arm64)", report)
        self.assertIn("Environment: native", report)
        self.assertIn("Permission scope: user", report)
        self.assertIn("Supported platform: yes", report)
        self.assertIn("Ready: no", report)
        self.assertIn("Status: degraded", report)
        self.assertIn("Failure reasons: missing_port_check_backend, missing_required_tools", report)
        self.assertIn("Lookup scope: listening_tcp_ports", report)
        self.assertIn("Active backend: none", report)
        self.assertIn("lsof", report)
        self.assertIn("ss", report)
        self.assertIn("macOS", report)
        self.assertIn("process names or owners", report)
        self.assertIn("Recommended actions", report)

    def test_unknown_permission_scope_is_stable_for_non_posix_platforms(self):
        def fake_which(name):
            return f"/usr/bin/{name}"

        with patch("portforge.diagnostics.platform.system", return_value="Windows"), patch(
            "portforge.diagnostics.platform.release", return_value="11"
        ), patch("portforge.diagnostics.platform.machine", return_value="AMD64"), patch(
            "portforge.diagnostics.shutil.which", side_effect=fake_which
        ), patch("portforge.diagnostics.os.geteuid", side_effect=AttributeError):
            diagnostics = collect_diagnostics()

        payload = diagnostics.to_dict()
        self.assertIsNone(payload["uid"])
        self.assertIsNone(payload["elevated"])
        self.assertEqual(payload["permission_scope"], "unknown")
        self.assertIn("Permission scope could not be detected", " ".join(payload["notes"]))


if __name__ == "__main__":
    unittest.main()
