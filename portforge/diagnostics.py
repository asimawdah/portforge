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

    @property
    def active_backend(self) -> str | None:
        """Return the first port-checking backend PortForge will try on this machine."""

        for tool in self.port_check_tools:
            if tool.available:
                return tool.name
        return None

    @property
    def missing_required_tools(self) -> list[str]:
        return [tool.name for tool in self.required_tools if not tool.available]

    @property
    def missing_port_check_tools(self) -> list[str]:
        return [tool.name for tool in self.port_check_tools if not tool.available]

    def to_dict(self) -> dict[str, object]:
        return {
            "system": self.system,
            "release": self.release,
            "machine": self.machine,
            "ready": self.ready,
            "has_port_checker": self.has_port_checker,
            "active_backend": self.active_backend,
            "missing_required_tools": self.missing_required_tools,
            "missing_port_check_tools": self.missing_port_check_tools,
            "required_tools": [tool.to_dict() for tool in self.required_tools],
            "port_check_tools": [tool.to_dict() for tool in self.port_check_tools],
            "notes": diagnostic_notes(self),
            "recommended_actions": recommended_actions(self),
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
        f"Active backend: {diagnostics.active_backend or 'none'}",
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

    actions = recommended_actions(diagnostics)
    if actions:
        lines.append("")
        lines.append("Recommended actions:")
        lines.extend(f"- {action}" for action in actions)

    return "\n".join(lines).rstrip() + "\n"


def diagnostic_notes(diagnostics: PlatformDiagnostics) -> list[str]:
    notes: list[str] = []
    if diagnostics.active_backend:
        notes.append(f"PortForge will use {diagnostics.active_backend} first for TCP listener checks.")
    if not diagnostics.has_port_checker:
        notes.append("Install lsof or ss so PortForge can inspect listening TCP ports.")
    if diagnostics.missing_required_tools:
        tools = ", ".join(diagnostics.missing_required_tools)
        notes.append(f"Install missing required tool(s): {tools}.")
    if diagnostics.system.lower() == "windows":
        notes.append("Native Windows process lookup is not implemented yet; use WSL for the current Unix-style backend.")
    if diagnostics.system.lower() == "darwin":
        notes.append("macOS usually works best with lsof available from the base system.")
    if diagnostics.system.lower() == "linux":
        notes.append("Linux can use lsof or ss; some process details may require sufficient permissions.")
    return notes


def recommended_actions(diagnostics: PlatformDiagnostics) -> list[str]:
    actions: list[str] = []
    system = diagnostics.system.lower()

    if not diagnostics.has_port_checker:
        if system == "darwin":
            actions.append("Verify the base-system lsof install or reinstall Xcode Command Line Tools.")
        elif system == "linux":
            actions.append("Install lsof or iproute2/ss with your system package manager.")
        elif system == "windows":
            actions.append("Run PortForge inside WSL until native Windows lookup is implemented.")
        else:
            actions.append("Install lsof or ss before relying on port scans.")

    if diagnostics.missing_required_tools:
        actions.append("Install ps/procps so process commands can be shown next to busy ports.")

    if diagnostics.ready:
        actions.append("Run `portforge scan --preset frontend` or `portforge 3000` to verify runtime behavior.")

    return actions


def _tool_status(name: str) -> ToolStatus:
    path = shutil.which(name)
    return ToolStatus(name=name, available=path is not None, path=path)


def _format_tool_line(tool: ToolStatus) -> str:
    status = "ok" if tool.available else "missing"
    suffix = f" ({tool.path})" if tool.path else ""
    return f"  {tool.name:<8} {status}{suffix}"
