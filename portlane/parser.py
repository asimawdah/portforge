from __future__ import annotations

from .models import ProcessInfo


def parse_lsof_output(output: str) -> list[ProcessInfo]:
    processes: list[ProcessInfo] = []
    lines = [line for line in output.splitlines() if line.strip()]
    if len(lines) <= 1:
        return processes

    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 9:
            continue
        name = parts[0]
        try:
            pid = int(parts[1])
        except ValueError:
            continue
        user = parts[2]
        address = " ".join(parts[8:])
        processes.append(ProcessInfo(pid=pid, name=name, user=user, command=name, address=address))
    return processes
