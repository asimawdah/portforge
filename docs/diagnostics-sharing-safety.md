# Diagnostics sharing safety

PortForge diagnostics are designed to make platform-specific port-check failures easier to debug without asking users to expose unnecessary local details.

Use this checklist before copying `portforge doctor --json` or `portforge 3000 --json` into a GitHub issue, chat message, CI artifact, or support ticket.

## Recommended report flow

1. Run the readiness report and save it locally:

   ```bash
   portforge doctor --json -o portforge-doctor.json
   ```

2. Run the smallest affected port check:

   ```bash
   portforge 3000 --json
   ```

3. Review both outputs before sharing them.
4. Keep the stable troubleshooting fields that help maintainers reproduce the issue.
5. Redact local details that are not needed to understand the platform failure.

## Keep these fields

These fields are useful for maintainers and automation because they explain whether the machine is supported, which lookup backend will run, and what the user should try next:

- `schema_version`
- `system`
- `machine`
- `environment`
- `is_wsl`
- `permission_scope`
- `supported_platform`
- `ready`
- `status`
- `failure_reasons`
- `lookup_scope`
- `backend_priority`
- `active_backend`
- `available_required_tools`
- `available_port_check_tools`
- `missing_required_tools`
- `missing_port_check_tools`
- `install_hints`
- `troubleshooting_commands`
- `recommended_actions`

## Redact before sharing

Review and redact values that can reveal private local context:

- Absolute tool paths that include usernames, home directories, workspace names, or company/project names.
- Process `command` values from `portforge <port> --json` when they include tokens, secrets, customer names, private repository names, or local file paths.
- Usernames, machine names, shell history fragments, and environment-specific values that are not required for the bug report.
- Any copied command output that includes authentication headers, `.env` values, API keys, database URLs, cookies, or bearer tokens.

## Safe placeholder style

Use stable placeholders instead of deleting entire fields. This keeps bug reports useful while protecting private data:

```json
{
  "schema_version": 2,
  "system": "Linux",
  "machine": "x86_64",
  "environment": "native",
  "status": "degraded",
  "failure_reasons": ["missing_port_check_backend"],
  "lookup_scope": "listening_tcp_ports",
  "backend_priority": ["lsof", "ss"],
  "active_backend": null,
  "permission_scope": "user",
  "required_tools": [
    {"name": "ps", "available": true, "path": "<redacted>"}
  ],
  "port_check_tools": [
    {"name": "lsof", "available": false, "path": null},
    {"name": "ss", "available": false, "path": null}
  ],
  "troubleshooting_commands": [
    "portforge doctor --json -o portforge-doctor.json",
    "portforge doctor"
  ]
}
```

## Maintainer review gates

Before asking for more diagnostic output, maintainers should first check whether the report already includes:

- `status` and `failure_reasons`.
- `backend_priority` and `active_backend`.
- `permission_scope`.
- `environment` and `is_wsl`.
- `lookup_scope`.
- Sanitized `required_tools` and `port_check_tools` entries.

Avoid asking users to paste full terminal sessions or unsanitized shell logs when the stable diagnostic fields are enough.
