import unittest
from pathlib import Path


class DiagnosticsDocsTest(unittest.TestCase):
    def test_troubleshooting_guide_documents_copyable_diagnostics_contract(self):
        guide = Path("docs/port-check-troubleshooting.md").read_text(encoding="utf-8")

        required_terms = [
            "portforge doctor",
            "portforge doctor --json -o portforge-doctor.json",
            "portforge 3000 --json",
            "troubleshooting_commands",
            "Troubleshooting commands",
            "status",
            "failure_reasons",
            "lookup_scope",
            "active_backend",
            "backend_priority",
            "available_port_check_tools",
            "missing_tools",
            "install_hints",
            "permission_scope",
            "environment",
            "missing_port_check_backend",
            "missing_required_tools",
            "unsupported_platform",
            "listening_tcp_ports",
        ]

        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, guide)

    def test_troubleshooting_guide_warns_before_sharing_sensitive_local_details(self):
        guide = Path("docs/port-check-troubleshooting.md").read_text(encoding="utf-8").lower()

        self.assertIn("avoid pasting full command paths", guide)
        self.assertIn("private usernames", guide)
        self.assertIn("project directories", guide)
        self.assertIn("customer data", guide)

    def test_readme_doctor_example_matches_current_diagnostics_sections(self):
        readme = Path("README.md").read_text(encoding="utf-8")

        required_terms = [
            "Permission scope: user",
            "Backend priority: lsof -> ss",
            "Troubleshooting commands:",
            "portforge doctor --json -o portforge-doctor.json",
            "portforge 3000 --json",
            '"permission_scope": "user"',
            '"backend_priority": ["lsof", "ss"]',
            '"troubleshooting_commands"',
        ]

        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, readme)


if __name__ == "__main__":
    unittest.main()
