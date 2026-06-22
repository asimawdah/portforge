import json
import unittest

from portpilot.formatters import format_port_report, format_scan_report, to_json
from portpilot.models import PortCheck, ProcessInfo


class FormattersTest(unittest.TestCase):
    def test_format_port_report_for_busy_port(self):
        check = PortCheck(port=3000, processes=[ProcessInfo(pid=123, name="node", user="asim", command="npm run dev", address="localhost:3000")])

        text = format_port_report(check)

        self.assertIn("Port 3000 is busy", text)
        self.assertIn("node", text)
        self.assertIn("portpilot kill 3000", text)

    def test_format_port_report_for_free_port(self):
        text = format_port_report(PortCheck(port=5173, processes=[]))

        self.assertIn("Port 5173 is free", text)

    def test_format_scan_report_lists_busy_and_free_ports(self):
        checks = [
            PortCheck(port=3000, processes=[ProcessInfo(pid=123, name="node", user="asim", command="node server.js", address="*:3000")]),
            PortCheck(port=5173, processes=[]),
        ]

        text = format_scan_report(checks)

        self.assertIn("3000", text)
        self.assertIn("busy", text)
        self.assertIn("5173", text)
        self.assertIn("free", text)

    def test_to_json_outputs_machine_readable_report(self):
        data = json.loads(to_json([PortCheck(port=3000, processes=[])]))

        self.assertEqual(data[0]["port"], 3000)
        self.assertFalse(data[0]["busy"])


if __name__ == "__main__":
    unittest.main()
