import unittest
from pathlib import Path


class PortCheckIssueTemplateContractTest(unittest.TestCase):
    def test_port_check_issue_template_collects_diagnostics_contract_fields(self):
        template = Path(".github/ISSUE_TEMPLATE/port-check-bug.yml").read_text(encoding="utf-8")

        required_terms = [
            "portforge doctor --json -o portforge-doctor.json",
            "portforge 3000 --json",
            "schema_version",
            "status",
            "failure_reasons",
            "lookup_scope",
            "backend_priority",
            "active_backend",
            "available_port_check_tools",
            "missing_tools",
            "permission_scope",
            "troubleshooting_commands",
            "Privacy review",
            "private usernames",
            "project paths",
            "tokens",
            "customer data",
        ]

        for term in required_terms:
            self.assertIn(term, template)

    def test_port_check_issue_template_requires_core_report_sections(self):
        template = Path(".github/ISSUE_TEMPLATE/port-check-bug.yml").read_text(encoding="utf-8")

        required_ids = [
            "id: portforge-version",
            "id: environment",
            "id: status",
            "id: diagnostics-json",
            "id: reproduction",
            "id: expected",
            "id: actual",
            "id: safety-review",
        ]

        for field_id in required_ids:
            self.assertIn(field_id, template)

        self.assertGreaterEqual(template.count("required: true"), len(required_ids))


if __name__ == "__main__":
    unittest.main()
