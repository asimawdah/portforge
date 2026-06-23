from __future__ import annotations

import os
import signal
import subprocess

from .models import PortCheck, ProcessInfo
from .parser import parse_lsof_output

DEFAULT_SCAN_PORTS = [3000, 3001, 5173, 8000, 8080, 5000, 5432, 3306, 6379]


def check_port(port: int) -> PortCheck:
    processes = _check_with_lsof(port)
    if not processes:
        processes = _check_with_ss(port)
    return PortCheck(port=port, processes=processes)


def kill_processes(processes: list[ProcessInfo], force: bool = False) -> list[int]:
    killed: list[int] = []
    sig = signal.SIGKILL if force else signal.SIGTERM
    for process in processes:
        os.kill(process.pid, sig)
        killed.append(process.pid)
    return killed


def _check_with_lsof(port: int) -> list[ProcessInfo]:
    try:
        result = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    processes = parse_lsof_output(result.stdout)
    return [_with_full_command(process) for process in processes]


def _check_with_ss(port: int) -> list[ProcessInfo]:
    try:
        result = subprocess.run(
            ["ss", "-ltnp", f"sport = :{port}"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    processes: list[ProcessInfo] = []
    for line in result.stdout.splitlines():
        if f":{port}" not in line or "pid=" not in line:
            continue
        pid = _extract_between(line, "pid=", ",")
        name = _extract_between(line, 'users:(("', '"') or "unknown"
        if not pid:
            continue
        process = ProcessInfo(pid=int(pid), name=name, user="", command=name, address=line.strip())
        processes.append(_with_full_command(process))
    return processes


def _with_full_command(process: ProcessInfo) -> ProcessInfo:
    try:
        result = subprocess.run(
            ["ps", "-p", str(process.pid), "-o", "command="],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return process
    command = result.stdout.strip() or process.command
    return ProcessInfo(pid=process.pid, name=process.name, user=process.user, command=command, address=process.address)


def _extract_between(text: str, start: str, end: str) -> str:
    if start not in text:
        return ""
    tail = text.split(start, 1)[1]
    if end not in tail:
        return tail
    return tail.split(end, 1)[0]
