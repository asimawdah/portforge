# Diagnostics JSON contract

`portforge doctor --json` emits one machine-readiness report as a single JSON object. This contract is intended for CI logs, issue reports, and release checks where text output is harder to parse reliably.

## Stable shape

The report must include these top-level fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | integer | Contract version for diagnostics payloads. |
| `system` | string | `platform.system()` value, for example `Linux`, `Darwin`, or `Windows`. |
| `release` | string | OS release value. |
| `machine` | string | Machine architecture value. |
| `environment` | string | `native` or `wsl`. |
| `is_wsl` | boolean | Whether PortForge detected WSL. |
| `uid` | integer or null | POSIX effective user id when available. |
| `elevated` | boolean or null | Whether the process is elevated when this can be detected. |
| `permission_scope` | string | `elevated`, `user`, or `unknown`. |
| `supported_platform` | boolean | Whether the current platform is supported by the current Unix-style lookup backend. |
| `ready` | boolean | Whether required tools and at least one port-check backend are available on a supported platform. |
| `status` | string | `ready`, `degraded`, or `unsupported`. |
| `failure_reasons` | array of strings | Stable reason codes explaining a non-ready report. |
| `lookup_scope` | string | Currently `listening_tcp_ports`. |
| `has_port_checker` | boolean | Whether any supported listener lookup backend is available. |
| `backend_priority` | array of strings | Stable backend lookup order, currently `lsof`, then `ss`. |
| `active_backend` | string or null | First available backend PortForge will use. |
| `available_required_tools` | array of strings | Required helper tools found on the machine. |
| `available_port_check_tools` | array of strings | Listener lookup tools found on the machine. |
| `missing_tools` | array of strings | De-duplicated list of missing required and listener lookup tools. |
| `missing_required_tools` | array of strings | Missing helper tools. |
| `missing_port_check_tools` | array of strings | Missing listener lookup backends. |
| `install_hints` | object | Missing tool names mapped to platform-specific install guidance. |
| `troubleshooting_commands` | array of strings | Copyable follow-up commands for support reports, ready-machine verification, WSL checks, or safe elevated retry. |
| `required_tools` | array of objects | Full status records for required helper tools. |
| `port_check_tools` | array of objects | Full status records for listener lookup backends. |
| `notes` | array of strings | Human-facing context for the report. |
| `recommended_actions` | array of strings | Actionable next steps. |

## Stable status values

- `ready`: the platform is supported, at least one listener lookup backend exists, and required helper tools are available.
- `degraded`: the platform is supported, but one or more tools required for reliable checks are missing.
- `unsupported`: the current platform is not supported by the current lookup backend.

## Stable failure reason codes

- `unsupported_platform`: native platform support is not implemented for the current OS.
- `missing_port_check_backend`: neither `lsof` nor `ss` is available for listening TCP port checks.
- `missing_required_tools`: one or more helper tools, currently `ps`, are missing.

## Consumer rules

1. Read `schema_version` first and reject unknown future versions only when strict parsing is required.
2. Use `status` for the primary decision, then inspect `failure_reasons` for remediation.
3. Treat `notes`, `recommended_actions`, and `install_hints` as user-facing strings; do not use them as stable machine codes.
4. Use `backend_priority`, `active_backend`, and `lookup_scope` to explain why a port check may differ across macOS, Linux, WSL, and CI.
5. Run or share `troubleshooting_commands` only after reviewing whether elevated commands are appropriate for the current machine.
6. Do not share raw reports publicly without reviewing paths in nested tool records, because tool paths may expose local system details.

## Minimal ready example

```json
{
  "schema_version": 2,
  "system": "Linux",
  "release": "6.0",
  "machine": "x86_64",
  "environment": "native",
  "is_wsl": false,
  "uid": 1000,
  "elevated": false,
  "permission_scope": "user",
  "supported_platform": true,
  "ready": true,
  "status": "ready",
  "failure_reasons": [],
  "lookup_scope": "listening_tcp_ports",
  "has_port_checker": true,
  "backend_priority": ["lsof", "ss"],
  "active_backend": "lsof",
  "available_required_tools": ["ps"],
  "available_port_check_tools": ["lsof", "ss"],
  "missing_tools": [],
  "missing_required_tools": [],
  "missing_port_check_tools": [],
  "install_hints": {},
  "troubleshooting_commands": [
    "portforge doctor --json -o portforge-doctor.json",
    "portforge scan --preset frontend",
    "portforge 3000 --json",
    "sudo portforge 3000 --json"
  ],
  "required_tools": [{"name": "ps", "available": true, "path": "/usr/bin/ps"}],
  "port_check_tools": [
    {"name": "lsof", "available": true, "path": "/usr/bin/lsof"},
    {"name": "ss", "available": true, "path": "/usr/bin/ss"}
  ],
  "notes": ["PortForge will use lsof first for TCP listener checks."],
  "recommended_actions": ["Run `portforge scan --preset frontend` or `portforge 3000` to verify runtime behavior."]
}
```
