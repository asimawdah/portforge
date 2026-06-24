import unittest
from unittest.mock import patch

from portforge.cli import main
from portforge.models import PortCheck


class PresetCliTest(unittest.TestCase):
    def test_scan_default_preset_includes_common_development_ports(self):
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
        self.assertIn(8080, calls)

    def test_scan_uses_named_preset(self):
        calls = []

        def fake_check(port):
            calls.append(port)
            return PortCheck(port=port, processes=[])

        with patch("portforge.cli.check_port", side_effect=fake_check):
            exit_code = main(["scan", "--preset", "databases"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(calls, [3306, 5432, 6379, 27017])

    def test_manual_ports_override_named_preset(self):
        calls = []

        def fake_check(port):
            calls.append(port)
            return PortCheck(port=port, processes=[])

        with patch("portforge.cli.check_port", side_effect=fake_check):
            exit_code = main(["scan", "--preset", "frontend", "--ports", "1234,5678"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(calls, [1234, 5678])


if __name__ == "__main__":
    unittest.main()
