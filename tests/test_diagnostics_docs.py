import unittest
from pathlib import Path


class DiagnosticsDocsTest(unittest.TestCase):
    def test_troubleshooting_guide_documents_copyable_diagnostics_contract(self):
        guide = Path("docs/port-check-troubleshooting.md").read_text(encoding="utf-8")

        required_terms = [
            "portforge doctor",
            "portforge doctor --json -o portforge-doctor.json",
            "portforge 3000 --json",
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


if __name__ == "__main__":
    unittest.main()
