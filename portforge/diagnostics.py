from __future__ import annotations

import platform
import shutil
from dataclasses import dataclass


REQUIRED_TOOLS = ("ps",)
PORT_CHECK_TOOLS = ("lsof", "ss")


@dataclass(frozen=True)
class ToolStatus:
    name: str
    available: bool
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "available": self.available, "path": self.path}


@dataclass(frozen=True)
class PlatformDiagnostics:
    system: str
    release: str
    machine: str
    required_tools: list[ToolStatus]
    port_check_tools: list[ToolStatus]

    @property
    def has_port_checker(self) -> bool:
        return any(tool.available for tool in self.port_check_tools)

    @property
    def ready(self) -> bool:
        return self.has_port_checker and all(tool.available for tool in self.required_tools)

    def to_dict(self) -> dict[str, object]:
        return {
            "system": self.system,
            "release": self.release,
            "machine": self.machine,
            "ready": self.ready,
            "has_port_checker": self.has_port_checker,
            "required_tools": [tool.to_dict() for tool in self.required_tools],
            "port_check_tools": [tool.to_dict() for tool in self.port_check_tools],
            "notes": diagnostic_notes(self),
        }


def collect_diagnostics() -> PlatformDiagnostics:
    return PlatformDiagnostics(
        system=platform.system() or "unknown",
        release=platform.release() or "unknown",
        machine=platform.machine() or "unknown",
        required_tools=[_tool_status(tool) for tool in REQUIRED_TOOLS],
        port_check_tools=[_tool_status(tool) for tool in PORT_CHECK_TOOLS],
    )


def format_diagnostics_report(diagnostics: PlatformDiagnostics) -> str:
    lines = [
        "PortForge diagnostics",
        "",
        f"Platform: {diagnostics.system} {diagnostics.release} ({diagnostics.machine})",
        f"Ready: {'yes' if diagnostics.ready else 'no'}",
        "",
        "Required tools:",
    ]
    lines.extend(_format_tool_line(tool) for tool in diagnostics.required_tools)
    lines.append("")
    lines.append("Port check tools:")
    lines.extend(_format_tool_line(tool) for tool in diagnostics.port_check_tools)

    notes = diagnostic_notes(diagnostics)
    if notes:
        lines.append("")
        lines.append("Notes:")
        lines.extend(f"- {note}" for note in notes)

    return "\n".join(lines).rstrip() + "\n"


def diagnostic_notes(diagnostics: PlatformDiagnostics) -> list[str]:
    notes: list[str] = []
    if not diagnostics.has_port_checker:
        notes.append("Install lsof or ss so PortForge can inspect listening TCP ports.")
    if not all(tool.available for tool in diagnostics.required_tools):
        notes.append("Install ps so PortForge can enrich port results with process commands.")
    if diagnostics.system.lower() == "windows":
        notes.append("Native Windows process lookup is not implemented yet; use WSL for the current Unix-style backend.")
    if diagnostics.system.lower() == "darwin":
        notes.append("macOS usually works best with lsof available from the base system.")
    if diagnostics.system.lower() == "linux":
        notes.append("Linux can use lsof or ss; some process details may require sufficient permissions.")
    return notes


def _tool_status(name: str) -> ToolStatus:
    path = shutil.which(name)
    return ToolStatus(name=name, available=path is not None, path=path)


def _format_tool_line(tool: ToolStatus) -> str:
    status = "ok" if tool.available else "missing"
    suffix = f" ({tool.path})" if tool.path else ""
    return f"  {tool.name:<8} {status}{suffix}"
