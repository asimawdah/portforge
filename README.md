# PortForge

Find and free busy development ports in seconds.

PortForge helps developers quickly answer the question: **what is using port 3000?** It shows the process, PID, command, and gives you a safe command when you want to free the port.

## Install

```bash
pip install portforge
```

The installed command is:

```bash
portforge
```

## Usage

Check one port:

```bash
portforge 3000
```

Scan common development ports:

```bash
portforge scan
```

Scan a named preset:

```bash
portforge scan --preset frontend
```

Available presets:

| Preset | Ports |
| --- | --- |
| `common` | `3000`, `3001`, `5173`, `8000`, `8080`, `5000`, `5432`, `3306`, `6379` |
| `frontend` | `3000`, `3001`, `4173`, `5173`, `8080` |
| `backend` | `5000`, `8000`, `8080`, `9000` |
| `databases` | `3306`, `5432`, `6379`, `27017` |

Scan custom ports:

```bash
portforge scan -p 3000,5173,8000
```

Manual ports passed with `--ports` override the selected preset.

Run a platform readiness check:

```bash
portforge doctor
```

Output diagnostics as JSON for CI or bug reports:

```bash
portforge doctor --json -o portforge-doctor.json
```

`doctor --json` writes one JSON object because it represents one machine diagnostic report. Port and scan JSON output remains a list of port check objects. The stable diagnostics payload is documented in [`docs/diagnostics-json-contract.md`](docs/diagnostics-json-contract.md).

Before sharing diagnostic JSON in an issue or support thread, review the sharing checklist in [`docs/diagnostics-sharing-safety.md`](docs/diagnostics-sharing-safety.md). Keep stable fields such as `status`, `failure_reasons`, `lookup_scope`, `backend_priority`, `active_backend`, `permission_scope`, `environment`, and `troubleshooting_commands`, but redact private local paths, usernames, project names, customer names, and unrelated command output.

Output JSON:

```bash
portforge 3000 --json
```

Write output to a file:

```bash
portforge 3000 -o ports.json --json
```

Free a busy port after confirmation:

```bash
portforge kill 3000 --yes
```

## Safety notes

- Review the displayed process name, PID, user, and command before killing anything.
- Prefer the normal kill command first; use `--force` only when a process does not stop cleanly.
- Avoid running kill commands against system services or processes you do not recognize.
- When using `--json` or `--output`, review files before sharing them because command paths can include local usernames or project names.
- Run `portforge doctor` before reporting platform-specific failures so missing tools or unsupported environments are clear.
- Use the diagnostics sharing checklist before pasting bug-report JSON into public issues.

## Platform support

PortForge is designed for local development workflows on Unix-like systems where process and port inspection tools are available.

| Platform | Expected behavior |
| --- | --- |
| macOS | Uses `lsof` for TCP listener lookup and `ps` for command enrichment. |
| Linux | Uses `lsof` when available, then falls back to `ss`; `ps` enriches command output. |
| Windows | Native process lookup is planned. Use WSL for the current Unix-style backend. |

If port checks return no process for a busy port, run:

```bash
portforge doctor
```

Common causes:

- `lsof` and `ss` are both missing.
- Process details require higher permissions.
- The port is busy on UDP or on a socket state outside the current listening TCP lookup scope.
- Native Windows process lookup is being used instead of WSL.
- The command is run from a different WSL distro or namespace than the server process.

The diagnostics report now includes:

- `Supported platform`: whether the current OS is expected to work with PortForge's current backend.
- `Ready`: whether PortForge has a supported OS, a port lookup backend, and required process tools.
- `Status`: machine-readable state: `ready`, `degraded`, or `unsupported`.
- `Failure reasons`: stable reason codes such as `unsupported_platform`, `missing_port_check_backend`, and `missing_required_tools`.
- `Lookup scope`: the diagnostic scope, currently `listening_tcp_ports`.
- `Backend priority`: the lookup order PortForge will try, currently `lsof -> ss`.
- `Active backend`: the first available lookup backend PortForge will use, such as `lsof`, `ss`, or `none`.
- `Permission scope`: whether the current process appears `elevated`, `user`, or `unknown`.
- `Environment`: whether diagnostics are running in a native environment or WSL.
- `Troubleshooting commands`: copyable follow-up commands for bug reports, ready-machine checks, WSL checks, or safe elevated retry.
- `Recommended actions`: install or environment steps to make port checks reliable.
- JSON fields for `schema_version`, `system`, `release`, `machine`, `environment`, `is_wsl`, `uid`, `elevated`, `permission_scope`, `supported_platform`, `ready`, `status`, `failure_reasons`, `lookup_scope`, `backend_priority`, `active_backend`, `available_required_tools`, `available_port_check_tools`, `missing_required_tools`, `missing_port_check_tools`, `install_hints`, `troubleshooting_commands`, and `recommended_actions`.

For WSL, PortForge reports `environment: wsl` and checks the Linux/WSL network namespace. Run PortForge from the same WSL distro that owns the development server you want to inspect.

For a copyable report template and step-by-step remediation flow, see [`docs/port-check-troubleshooting.md`](docs/port-check-troubleshooting.md). For tools that consume `doctor --json`, see the diagnostics contract in [`docs/diagnostics-json-contract.md`](docs/diagnostics-json-contract.md). For privacy-safe issue reports, see [`docs/diagnostics-sharing-safety.md`](docs/diagnostics-sharing-safety.md).

## CLI shortcuts

- `--preset`: named port preset for scan when `--ports` is not provided
- `-p`, `--ports`: comma-separated ports for scan
- `-j`, `--json`: output JSON
- `-o`, `--output`: write output to file
- `-y`, `--yes`: confirm port-freeing action
- `-f`, `--force`: use a stronger termination signal

## Example

```text
$ portforge 3000
Port 3000 is busy

PID      USER         NAME             COMMAND
18422    asim         node             npm run dev

Actions:
  portforge kill 3000
```

```text
$ portforge scan
PortForge scan

PORT     STATUS   PROCESS
3000     busy     node
3001     free     -
5173     free     -
8000     busy     python
```

```text
$ portforge doctor
PortForge diagnostics

Platform: Darwin 25.0 (arm64)
Environment: native
Permission scope: user
Supported platform: yes
Ready: yes
Status: ready
Lookup scope: listening_tcp_ports
Backend priority: lsof -> ss
Active backend: lsof

Required tools:
  ps       ok (/bin/ps)

Port check tools:
  lsof     ok (/usr/sbin/lsof)
  ss       missing

Install hints:
- ss: ss is not required on macOS when lsof is available.

Notes:
- PortForge will use lsof first for TCP listener checks.
- PortForge backend priority is lsof -> ss, so diagnostics show both selected and fallback tools.
- PortForge checks listening TCP ports; UDP and non-listening socket states are outside this diagnostic scope.
- Non-elevated scans may hide process names or owners for listeners owned by other users.
- macOS usually works best with lsof available from the base system.

Recommended actions:
- If process names or owners are incomplete, rerun the same check with elevated permissions.
- Run `portforge scan --preset frontend` or `portforge 3000` to verify runtime behavior.

Troubleshooting commands:
- `portforge doctor --json -o portforge-doctor.json`
- `portforge scan --preset frontend`
- `portforge 3000 --json`
- `sudo portforge 3000 --json`
```

```json
{
  "schema_version": 2,
  "environment": "native",
  "permission_scope": "user",
  "ready": true,
  "status": "ready",
  "failure_reasons": [],
  "lookup_scope": "listening_tcp_ports",
  "backend_priority": ["lsof", "ss"],
  "active_backend": "lsof",
  "troubleshooting_commands": [
    "portforge doctor --json -o portforge-doctor.json",
    "portforge scan --preset frontend",
    "portforge 3000 --json",
    "sudo portforge 3000 --json"
  ]
}
```

When `Status` is `degraded` or `unsupported`, inspect `Failure reasons` first. Those values are stable enough for CI logs, issue templates, and bug reports.

## Development

```bash
python3 -m unittest discover -s tests -v
```
