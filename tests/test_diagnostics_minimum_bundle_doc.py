import unittest
from pathlib import Path


class DiagnosticsMinimumBundleDocTest(unittest.TestCase):
    def test_minimum_maintainer_bundle_stays_documented(self):
        guide = Path("docs/diagnostics-sharing-safety.md").read_text(encoding="utf-8")

        required_terms = [
            "Minimum maintainer bundle",
            "smaller sanitized bundle",
            "root-cause signals",
            "schema_version",
            "status",
            "failure_reasons",
            "lookup_scope",
            "backend_priority",
            "active_backend",
            "available_port_check_tools",
            "missing_port_check_tools",
            "troubleshooting_commands",
        ]

        for term in required_terms:
            self.assertIn(term, guide)


if __name__ == "__main__":
    unittest.main()
