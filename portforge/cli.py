from __future__ import annotations

import argparse
from pathlib import Path

from .checker import check_port, kill_processes
from .diagnostics import collect_diagnostics, format_diagnostics_report
from .formatters import format_port_report, format_scan_report, to_json, to_json_object
from .presets import DEFAULT_PRESET, PORT_PRESETS

MIN_PORT = 1
MAX_PORT = 65535


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portforge",
        description="Find and free busy development ports in seconds.",
    )
    parser.add_argument("command", nargs="?", default="scan", help="Port number, 'scan', 'kill', or 'doctor'")
    parser.add_argument("port", nargs="?", type=int, help="Port number for kill command")
    parser.add_argument(
        "--preset",
        choices=sorted(PORT_PRESETS),
        default=DEFAULT_PRESET,
        help="Named port preset for scan when --ports is not provided",
    )
    parser.add_argument("-p", "--ports", help="Comma-separated ports for scan")
    parser.add_argument("-j", "--json", action="store_true", help="Output JSON")
    parser.add_argument("-o", "--output", help="Write output to file")
    parser.add_argument("-y", "--yes", action="store_true", help="Confirm destructive actions")
    parser.add_argument("-f", "--force", action="store_true", help="Use SIGKILL instead of SIGTERM")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "doctor":
        diagnostics = collect_diagnostics()
        output = to_json_object(diagnostics) if args.json else format_diagnostics_report(diagnostics)
        _emit(output, args.output)
        return 0 if diagnostics.ready else 1

    if args.command == "scan":
        ports = _parse_ports(args.ports) if args.ports else PORT_PRESETS[args.preset]
        checks = [check_port(port) for port in ports]
        output = to_json(checks) if args.json else format_scan_report(checks)
        _emit(output, args.output)
        return 0

    if args.command == "kill":
        if args.port is None:
            raise SystemExit("portforge kill requires a port number")
        port = _validate_port(args.port)
        check = check_port(port)
        if not check.busy:
            _emit(format_port_report(check), args.output)
            return 0
        if not args.yes:
            _emit(format_port_report(check), args.output)
            print("Refusing to kill without confirmation. Re-run with --yes or -y.")
            return 2
        killed = kill_processes(check.processes, force=args.force)
        output = f"Killed processes on port {port}: {', '.join(str(pid) for pid in killed)}\n"
        _emit(output, args.output)
        return 0

    try:
        port = _parse_port(args.command)
    except ValueError as exc:
        raise SystemExit(f"Unknown command or invalid port: {args.command}") from exc

    check = check_port(port)
    output = to_json([check]) if args.json else format_port_report(check)
    _emit(output, args.output)
    return 0


def _parse_ports(value: str) -> list[int]:
    ports: list[int] = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        ports.append(_parse_port(item))
    return ports


def _parse_port(value: str) -> int:
    return _validate_port(int(value))


def _validate_port(port: int) -> int:
    if not MIN_PORT <= port <= MAX_PORT:
        raise ValueError(f"Port must be between {MIN_PORT} and {MAX_PORT}: {port}")
    return port


def _emit(output: str, path: str | None = None) -> None:
    if path:
        Path(path).write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    raise SystemExit(main())
