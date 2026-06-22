import unittest

from portpilot.parser import parse_lsof_output


class ParseLsofOutputTest(unittest.TestCase):
    def test_parse_lsof_output_returns_processes(self):
        raw = """COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node    12345 asim   22u  IPv4 123456      0t0  TCP localhost:3000 (LISTEN)
python  22222 asim    3u  IPv4 999999      0t0  TCP *:8000 (LISTEN)
"""

        processes = parse_lsof_output(raw)

        self.assertEqual(len(processes), 2)
        self.assertEqual(processes[0].name, "node")
        self.assertEqual(processes[0].pid, 12345)
        self.assertEqual(processes[0].user, "asim")
        self.assertIn("localhost:3000", processes[0].address)

    def test_parse_lsof_output_handles_empty_output(self):
        self.assertEqual(parse_lsof_output(""), [])


if __name__ == "__main__":
    unittest.main()
