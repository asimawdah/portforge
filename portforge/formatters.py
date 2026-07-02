from __future__ import annotations

import json

from .hints import format_service_hint, get_service_hint
from .models import PortCheck, ProcessInfo


def format_port_report(check: PortCheck) -> str:
    hint = get_service_hint(check.port)
    if not check.busy:
        lines = [f"Port {check.port} is free"]
        if hint:
            lines.extend(["", "Hint:", f"  Common use: {hint.service}", f"  {hint.note}"])
        return "\n".join(lines).rstrip() + "\n"

    lines = [
        f"Port {check.port} is busy",
        "",
        _process_table(check.processes),
    ]
    if hint:
        lines.extend(["", "Hint:", f"  Common use: {hint.service}", f"  {hint.note}"])
    lines.extend(
        [
            "",
            "Actions:",
            f"  portforge kill {check.port}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def format_scan_report(checks: list[PortCheck]) -> str:
    lines = ["PortForge scan", "", f"{'PORT':<8} {'STATUS':<8} {'PROCESS':<18} HINT"]
    for check in checks:
        hint = format_service_hint(check.port)
        if check.busy:
            names = ", ".join(sorted({process.name for process in check.processes}))
            lines.append(f"{check.port:<8} {'busy':<8} {names:<18} {hint}")
        else:
            lines.append(f"{check.port:<8} {'free':<8} {'-':<18} {hint}")
    return "\n".join(lines) + "\n"


def to_json(checks: list[PortCheck]) -> str:
    rows: list[dict[str, object]] = []
    for check in checks:
        row = check.to_dict()
        hint = get_service_hint(check.port)
        row["hint"] = None if hint is None else {"service": hint.service, "note": hint.note}
        rows.append(row)
    return json.dumps(rows, indent=2) + "\n"


def to_json_object(item: object) -> str:
    """Format a single report object as JSON without wrapping it in a list."""

    to_dict = getattr(item, "to_dict", None)
    if not callable(to_dict):
        raise TypeError("JSON report objects must define to_dict()")
    return json.dumps(to_dict(), indent=2) + "\n"


def _process_table(processes: list[ProcessInfo]) -> str:
    lines = [f"{'PID':<8} {'USER':<12} {'NAME':<16} COMMAND"]
    for process in processes:
        lines.append(f"{process.pid:<8} {process.user:<12} {process.name:<16} {process.command}")
    return "\n".join(lines)
