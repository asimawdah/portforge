from __future__ import annotations

import os
import platform
import shutil
from dataclasses import dataclass
from pathlib import Path


REQUIRED_TOOLS = ("ps",)
PORT_CHECK_TOOLS = ("lsof", "ss")
DIAGNOSTICS_SCHEMA_VERSION = 2
LOOKUP_SCOPE = "listening_tcp_ports"
SUPPORTED_SYSTEMS = {"darwin", "linux"}
STATUS_READY = "ready"
STATUS_DEGRADED = "degraded"
STATUS_UNSUPPORTED = "unsupported"
PERMISSION_SCOPE_ELEVATED = "elevated"
PERMISSION_SCOPE_USER = "user"
PERMISSION_SCOPE_UNKNOWN = "unknown"
TOOL_INSTALL_HINTS: dict[str, dict[str, str]] = {
    "darwin": {
        "lsof": "lsof is included with macOS; reinstall Xcode Command Line Tools if it is unavailable.",
        "ss": "ss is not required on macOS when lsof is available.",
        "ps": "ps is included with macOS; reinstall Xcode Command Line Tools if it is unavailable.",
    },
    "linux": {
        "lsof": "Install lsof with your system package manager, for example apt install lsof or dnf install lsof.",
        "ss": "Install iproute2 to provide ss, for example apt install iproute2 or dnf install iproute.",
        "ps": "Install procps/procps-ng so PortForge can enrich busy-port output with process commands.",
    },
    "windows": {
        "lsof": "Native Windows lookup is not implemented; run PortForge inside WSL for the current Unix-style backend.",
        "ss": "Native Windows lookup is not implemented; run PortForge inside WSL for the current Unix-style backend.",
        "ps": "Native Windows lookup is not implemented; run PortForge inside WSL for the current Unix-style backend.",
    },
}


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
    environment: str = "native"
    uid: int | None = None

    @property
    def system_key(self) -> str:
        return self.system.lower()

    @property
    def environment_key(self) -> str:
        return self.environment.lower()

    @property
    def is_wsl(self) -> bool:
        return self.environment_key == "wsl"

    @property
    def supported_platform(self) -> bool:
        return self.system_key in SUPPORTED_SYSTEMS

    @property
    def has_port_checker(self) -> bool:
        return any(tool.available for tool in self.port_check_tools)

    @property
    def ready(self) -> bool:
        return self.supported_platform and self.has_port_checker and all(tool.available for tool in self.required_tools)

    @property
    def status(self) -> str:
        if self.ready:
            return STATUS_READY
        if not self.supported_platform:
            return STATUS_UNSUPPORTED
        return STATUS_DEGRADED

    @property
    def backend_priority(self) -> list[str]:
        """Return the stable backend order PortForge will try for listener checks."""

        return [tool.name for tool in self.port_check_tools]

    @property
    def available_port_check_tools(self) -> list[str]:
        return [tool.name for tool in self.port_check_tools if tool.available]

    @property
    def available_required_tools(self) -> list[str]:
        return [tool.name for tool in self.required_tools if tool.available]

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

    @property
    def missing_tools(self) -> list[str]:
        return _dedupe(self.missing_required_tools + self.missing_port_check_tools)

    @property
    def is_elevated(self) -> bool | None:
        if self.uid is None:
            return None
        return self.uid == 0

    @property
    def permission_scope(self) -> str:
        if self.is_elevated is None:
            return PERMISSION_SCOPE_UNKNOWN
        if self.is_elevated:
            return PERMISSION_SCOPE_ELEVATED
        return PERMISSION_SCOPE_USER

    @property
    def failure_reasons(self) -> list[str]:
        reasons: list[str] = []
        if not self.supported_platform:
            reasons.append("unsupported_platform")
        if not self.has_port_checker:
            reasons.append("missing_port_check_backend")
        if self.missing_required_tools:
            reasons.append("missing_required_tools")
        return reasons

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": DIAGNOSTICS_SCHEMA_VERSION,
            "system": self.system,
            "release": self.release,
            "machine": self.machine,
            "environment": self.environment,
            "is_wsl": self.is_wsl,
            "uid": self.uid,
            "elevated": self.is_elevated,
            "permission_scope": self.permission_scope,
            "supported_platform": self.supported_platform,
            "ready": self.ready,
            "status": self.status,
            "failure_reasons": self.failure_reasons,
            "lookup_scope": LOOKUP_SCOPE,
            "has_port_checker": self.has_port_checker,
            "backend_priority": self.backend_priority,
            "active_backend": self.active_backend,
            "available_required_tools": self.available_required_tools,
            "available_port_check_tools": self.available_port_check_tools,
            "missing_tools": self.missing_tools,
            "missing_required_tools": self.missing_required_tools,
            "missing_port_check_tools": self.missing_port_check_tools,
            "install_hints": install_hints(self),
            "troubleshooting_commands": troubleshooting_commands(self),
            "required_tools": [tool.to_dict() for tool in self.required_tools],
            "port_check_tools": [tool.to_dict() for tool in self.port_check_tools],
            "notes": diagnostic_notes(self),
            "recommended_actions": recommended_actions(self),
        }


def collect_diagnostics() -> PlatformDiagnostics:
    system = platform.system() or "unknown"
    release = platform.release() or "unknown"
    version = platform.version() or ""
    return PlatformDiagnostics(
        system=system,
        release=release,
        machine=platform.machine() or "unknown",
        environment=detect_environment(system, release, version),
        uid=current_uid(),
        required_tools=[_tool_status(tool) for tool in REQUIRED_TOOLS],
        port_check_tools=[_tool_status(tool) for tool in PORT_CHECK_TOOLS],
    )


def current_uid() -> int | None:
    """Return the current POSIX user id when available.

    Windows does not expose ``os.geteuid``. Keeping this value optional lets JSON
    diagnostics stay stable across native Windows, WSL, macOS, and Linux.
    """

    get_euid = getattr(os, "geteuid", None)
    if get_euid is None:
        return None
    try:
        return int(get_euid())
    except (OSError, AttributeError, TypeError, ValueError):
        return None


def detect_environment(system: str, release: str, version: str, os_release_path: str | Path = "/proc/version") -> str:
    """Return a stable environment label for diagnostics output."""

    if system.lower() != "linux":
        return "native"

    haystack = f"{release}\n{version}".lower()
    if "microsoft" in haystack or "wsl" in haystack:
        return "wsl"

    try:
        proc_version = Path(os_release_path).read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        proc_version = ""

    if "microsoft" in proc_version or "wsl" in proc_version:
        return "wsl"

    return "native"


def format_diagnostics_report(diagnostics: PlatformDiagnostics) -> str:
    lines = [
        "PortForge diagnostics",
        "",
        f"Platform: {diagnostics.system} {diagnostics.release} ({diagnostics.machine})",
        f"Environment: {diagnostics.environment}",
        f"Permission scope: {diagnostics.permission_scope}",
        f"Supported platform: {'yes' if diagnostics.supported_platform else 'no'}",
        f"Ready: {'yes' if diagnostics.ready else 'no'}",
        f"Status: {diagnostics.status}",
        f"Lookup scope: {LOOKUP_SCOPE}",
        f"Backend priority: {' -> '.join(diagnostics.backend_priority)}",
        f"Active backend: {diagnostics.active_backend or 'none'}",
    ]

    if diagnostics.failure_reasons:
        lines.append(f"Failure reasons: {', '.join(diagnostics.failure_reasons)}")

    lines.extend(["", "Required tools:"])
    lines.extend(_format_tool_line(tool) for tool in diagnostics.required_tools)
    lines.append("")
    lines.append("Port check tools:")
    lines.extend(_format_tool_line(tool) for tool in diagnostics.port_check_tools)

    hints = install_hints(diagnostics)
    if hints:
        lines.append("")
        lines.append("Install hints:")
        lines.extend(f"- {tool}: {hint}" for tool, hint in hints.items())

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

    commands = troubleshooting_commands(diagnostics)
    if commands:
        lines.append("")
        lines.append("Troubleshooting commands:")
        lines.extend(f"- `{command}`" for command in commands)

    return "\n".join(lines).rstrip() + "\n"


def diagnostic_notes(diagnostics: PlatformDiagnostics) -> list[str]:
    notes: list[str] = []
    if diagnostics.active_backend:
        notes.append(f"PortForge will use {diagnostics.active_backend} first for TCP listener checks.")
    notes.append(
        "PortForge backend priority is "
        f"{' -> '.join(diagnostics.backend_priority)}, so diagnostics show both selected and fallback tools."
    )
    notes.append("PortForge checks listening TCP ports; UDP and non-listening socket states are outside this diagnostic scope.")
    if diagnostics.permission_scope == PERMISSION_SCOPE_USER:
        notes.append("Non-elevated scans may hide process names or owners for listeners owned by other users.")
    if diagnostics.permission_scope == PERMISSION_SCOPE_UNKNOWN:
        notes.append("Permission scope could not be detected on this platform, so process visibility may vary.")
    if diagnostics.is_wsl:
        notes.append("WSL is detected; PortForge will inspect the Linux/WSL network namespace, not native Windows processes.")
    if not diagnostics.supported_platform:
        notes.append("This platform is not yet supported by the current Unix-style lookup backend.")
    if not diagnostics.has_port_checker:
        notes.append("Install lsof or ss so PortForge can inspect listening TCP ports.")
    if diagnostics.missing_required_tools:
        tools = ", ".join(diagnostics.missing_required_tools)
        notes.append(f"Install missing required tool(s): {tools}.")
    if diagnostics.system_key == "windows":
        notes.append("Native Windows process lookup is not implemented yet; use WSL for the current Unix-style backend.")
    if diagnostics.system_key == "darwin":
        notes.append("macOS usually works best with lsof available from the base system.")
    if diagnostics.system_key == "linux":
        notes.append("Linux can use lsof or ss; some process details may require sufficient permissions.")
    return notes


def install_hints(diagnostics: PlatformDiagnostics) -> dict[str, str]:
    """Return stable, platform-specific install guidance for missing tools."""

    system_hints = TOOL_INSTALL_HINTS.get(diagnostics.system_key, {})
    generic_hints = {
        "lsof": "Install lsof with your system package manager.",
        "ss": "Install a package that provides ss, commonly iproute2 on Linux.",
        "ps": "Install a package that provides ps, commonly procps/procps-ng on Linux.",
    }
    hints: dict[str, str] = {}
    for tool in diagnostics.missing_tools:
        hints[tool] = system_hints.get(tool, generic_hints.get(tool, f"Install {tool} before relying on this diagnostic check."))
    return hints


def recommended_actions(diagnostics: PlatformDiagnostics) -> list[str]:
    actions: list[str] = []
    system = diagnostics.system_key

    if not diagnostics.supported_platform:
        if system == "windows":
            actions.append("Run PortForge inside WSL until native Windows lookup is implemented.")
        else:
            actions.append("Use macOS, Linux, or WSL for reliable PortForge listener checks.")

    if diagnostics.is_wsl and diagnostics.ready:
        actions.append("Run the command from the same WSL distro that owns the development server you want to inspect.")

    if diagnostics.permission_scope == PERMISSION_SCOPE_USER:
        actions.append("If process names or owners are incomplete, rerun the same check with elevated permissions.")

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

    return _dedupe(actions)


def troubleshooting_commands(diagnostics: PlatformDiagnostics) -> list[str]:
    """Return copyable follow-up commands for support reports and manual checks."""

    commands = ["portforge doctor --json -o portforge-doctor.json"]

    if diagnostics.ready:
        commands.extend(["portforge scan --preset frontend", "portforge 3000 --json"])
    elif diagnostics.supported_platform:
        commands.append("portforge doctor")
    elif diagnostics.system_key == "windows":
        commands.append("wsl portforge doctor")
    else:
        commands.append("portforge doctor")

    if diagnostics.permission_scope == PERMISSION_SCOPE_USER and diagnostics.has_port_checker:
        commands.append("sudo portforge 3000 --json")

    return _dedupe(commands)


def _tool_status(name: str) -> ToolStatus:
    path = shutil.which(name)
    return ToolStatus(name=name, available=path is not None, path=path)


def _format_tool_line(tool: ToolStatus) -> str:
    status = "ok" if tool.available else "missing"
    suffix = f" ({tool.path})" if tool.path else ""
    return f"  {tool.name:<8} {status}{suffix}"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
