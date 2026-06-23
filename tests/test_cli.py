import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from portforge.cli import main
from portforge.models import PortCheck, ProcessInfo


class CliTest(unittest.TestCase):
    def test_cli_checks_single_port_and_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "ports.json"
            check = PortCheck(port=3000, processes=[])

            with patch("portforge.cli.check_port", return_value=check):
                exit_code = main(["3000", "--json", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            self.assertIn('"port": 3000', output.read_text(encoding="utf-8"))

    def test_cli_scan_checks_default_ports(self):
        calls = []

        def fake_check(port):
            calls.append(port)
            return PortCheck(port=port, processes=[])

        with patch("portforge.cli.check_port", side_effect=fake_check):
            exit_code = main(["scan"])

        self.assertEqual(exit_code, 0)
        self.assertIn(3000, calls)
        self.assertIn(5173, calls)
        self.assertIn(8000, calls)

    def test_cli_rejects_invalid_single_port_ranges(self):
        with self.assertRaises(SystemExit):
            main(["0"])

        with self.assertRaises(SystemExit):
            main(["65536"])

    def test_cli_rejects_invalid_scan_port_ranges(self):
        with self.assertRaises(ValueError):
            main(["scan", "--ports", "3000,65536"])

    def test_cli_kill_rejects_invalid_port_ranges(self):
        with self.assertRaises(ValueError):
            main(["kill", "0", "--yes"])

    def test_cli_kill_requires_yes_for_non_interactive_kill(self):
        process = ProcessInfo(pid=123, name="node", user="asim", command="node server.js", address="*:3000")
        check = PortCheck(port=3000, processes=[process])

        with patch("portforge.cli.check_port", return_value=check), patch("portforge.cli.kill_processes") as kill:
            exit_code = main(["kill", "3000"])

        self.assertEqual(exit_code, 2)
        kill.assert_not_called()

        with patch("portforge.cli.check_port", return_value=check), patch("portforge.cli.kill_processes", return_value=[123]) as kill:
            exit_code = main(["kill", "3000", "--yes"])

        self.assertEqual(exit_code, 0)
        kill.assert_called_once()


if __name__ == "__main__":
    unittest.main()
