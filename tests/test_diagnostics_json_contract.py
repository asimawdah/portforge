import json
import unittest
from pathlib import Path

from portforge.diagnostics import PlatformDiagnostics, ToolStatus


class DiagnosticsJsonContractTest(unittest.TestCase):
    def test_documented_contract_fields_match_payload(self):
        diagnostics = PlatformDiagnostics(
            system="Linux",
            release="6.0",
            machine="x86_64",
            environment="native",
            uid=1000,
            required_tools=[ToolStatus("ps", True, "/usr/bin/ps")],
            port_check_tools=[
                ToolStatus("lsof", True, "/usr/bin/lsof"),
                ToolStatus("ss", False, None),
            ],
        )

        payload = diagnostics.to_dict()
        documented = Path("docs/diagnostics-json-contract.md").read_text(encoding="utf-8")
        expected_fields = {
            "schema_version",
            "system",
            "release",
            "machine",
            "environment",
            "is_wsl",
            "uid",
            "elevated",
            "permission_scope",
            "supported_platform",
            "ready",
            "status",
            "failure_reasons",
            "lookup_scope",
            "has_port_checker",
            "backend_priority",
            "active_backend",
            "available_required_tools",
            "available_port_check_tools",
            "missing_tools",
            "missing_required_tools",
            "missing_port_check_tools",
            "install_hints",
            "required_tools",
            "port_check_tools",
            "notes",
            "recommended_actions",
        }

        self.assertEqual(set(payload), expected_fields)
        for field in expected_fields:
            self.assertIn(f"`{field}`", documented)

        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["failure_reasons"], [])
        self.assertEqual(payload["lookup_scope"], "listening_tcp_ports")
        self.assertEqual(payload["backend_priority"], ["lsof", "ss"])
        self.assertEqual(payload["active_backend"], "lsof")
        self.assertEqual(payload["available_required_tools"], ["ps"])
        self.assertEqual(payload["available_port_check_tools"], ["lsof"])
        self.assertEqual(payload["missing_port_check_tools"], ["ss"])

    def test_documented_minimal_example_is_valid_json(self):
        contract = Path("docs/diagnostics-json-contract.md").read_text(encoding="utf-8")
        marker = "```json\n"
        start = contract.rindex(marker) + len(marker)
        end = contract.index("\n```", start)
        example = json.loads(contract[start:end])

        self.assertEqual(example["schema_version"], 2)
        self.assertEqual(example["status"], "ready")
        self.assertEqual(example["lookup_scope"], "listening_tcp_ports")
        self.assertEqual(example["backend_priority"], ["lsof", "ss"])
        self.assertIn("recommended_actions", example)


if __name__ == "__main__":
    unittest.main()
