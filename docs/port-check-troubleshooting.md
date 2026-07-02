# Port check troubleshooting

Use this guide when PortForge reports a port as free even though a development server appears to be running, or when a busy-port result has incomplete process details.

## Fast path

Run the machine diagnostics first:

```bash
portforge doctor
```

Save a machine-readable report when opening an issue or checking CI logs:

```bash
portforge doctor --json -o portforge-doctor.json
```

Then run the smallest port check that reproduces the problem:

```bash
portforge 3000 --json
```

`portforge doctor` now prints a `Troubleshooting commands` section, and `portforge doctor --json` includes a `troubleshooting_commands` array. Use those copyable commands as the next safe checks before guessing whether the scanner, permissions, or platform backend is the cause.

## How to read the report

Start with these fields before assuming the scanner is wrong:

| Field | What to check |
| --- | --- |
| `status` | `ready`, `degraded`, or `unsupported`. A degraded or unsupported report usually explains missing tools or unsupported lookup behavior. |
| `failure_reasons` | Stable reason codes. Check this before reading long notes. |
| `lookup_scope` | PortForge currently checks `listening_tcp_ports`; UDP and non-listening socket states are outside this scope. |
| `active_backend` | The backend PortForge will use first, such as `lsof`, `ss`, or `null` when none is available. |
| `backend_priority` | The lookup order, currently `lsof` then `ss`. |
| `available_port_check_tools` | Confirms whether `lsof` or `ss` is installed. |
| `missing_tools` | Tools to install before retrying. |
| `install_hints` | Platform-specific install or environment guidance. |
| `permission_scope` | Whether the command is running as `elevated`, `user`, or `unknown`. |
| `environment` | `native` or `wsl`; WSL checks the Linux/WSL namespace, not native Windows processes. |
| `troubleshooting_commands` | Copyable next commands for support reports, ready-machine verification, WSL checks, or elevated retry when process details are hidden. |

## Common outcomes

### `missing_port_check_backend`

PortForge cannot inspect listening TCP ports because neither `lsof` nor `ss` is available.

Recommended actions:

- Linux: install `lsof` or `iproute2`/`ss` with the system package manager.
- macOS: verify `lsof` is available from the base system or reinstall Xcode Command Line Tools.
- Windows: run PortForge inside WSL until native Windows lookup is implemented.

### `missing_required_tools`

PortForge may detect a listener but cannot enrich process details reliably because `ps` is missing.

Recommended action: install `procps` or `procps-ng` on Linux-like environments.

### `unsupported_platform`

The current native platform does not have a supported lookup backend yet.

Recommended action: run PortForge on macOS, Linux, or WSL.

### Busy port but no process details

If `status` is `ready` and the port still has incomplete process information:

1. Confirm the server is listening on TCP, not UDP.
2. Run PortForge from the same WSL distro or namespace that owns the server.
3. Compare `permission_scope` with the owner of the server process.
4. Retry with elevated permissions only on a trusted machine and only when process details are needed.

## Minimal issue report

Copy this shape into bug reports and replace values from `portforge doctor --json`:

```json
{
  "schema_version": 2,
  "system": "Linux",
  "release": "6.0",
  "machine": "x86_64",
  "environment": "native",
  "status": "degraded",
  "failure_reasons": ["missing_port_check_backend"],
  "lookup_scope": "listening_tcp_ports",
  "backend_priority": ["lsof", "ss"],
  "active_backend": null,
  "available_port_check_tools": [],
  "missing_tools": ["lsof", "ss"],
  "permission_scope": "user",
  "troubleshooting_commands": [
    "portforge doctor --json -o portforge-doctor.json",
    "portforge doctor"
  ]
}
```

Avoid pasting full command paths from scan output when they include private usernames, project directories, tokens, or customer data.
