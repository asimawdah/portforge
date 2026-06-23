from __future__ import annotations

import json

from .models import PortCheck, ProcessInfo


def format_port_report(check: PortCheck) -> str:
    if not check.busy:
        return f"Port {check.port} is free\n"

    lines = [
        f"Port {check.port} is busy",
        "",
        _process_table(check.processes),
        "",
        "Actions:",
        f"  portlane kill {check.port}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def format_scan_report(checks: list[PortCheck]) -> str:
    lines = ["PortLane scan", "", f"{'PORT':<8} {'STATUS':<8} PROCESS"]
    for check in checks:
        if check.busy:
            names = ", ".join(sorted({process.name for process in check.processes}))
            lines.append(f"{check.port:<8} {'busy':<8} {names}")
        else:
            lines.append(f"{check.port:<8} {'free':<8} -")
    return "\n".join(lines) + "\n"


def to_json(checks: list[PortCheck]) -> str:
    return json.dumps([check.to_dict() for check in checks], indent=2) + "\n"


def _process_table(processes: list[ProcessInfo]) -> str:
    lines = [f"{'PID':<8} {'USER':<12} {'NAME':<16} COMMAND"]
    for process in processes:
        lines.append(f"{process.pid:<8} {process.user:<12} {process.name:<16} {process.command}")
    return "\n".join(lines)
