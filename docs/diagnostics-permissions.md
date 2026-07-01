# Diagnostics permission scope

`portforge doctor` reports a stable `permission_scope` field so bug reports can separate platform/tool problems from process visibility limits.

| Field | Meaning |
| --- | --- |
| `permission_scope: elevated` | The current POSIX effective user id is `0`. |
| `permission_scope: user` | The command is running as a normal user. Listener lookup can still work, but process names or owners may be incomplete for listeners owned by another account. |
| `permission_scope: unknown` | The platform does not expose a POSIX effective user id or the lookup failed. |

JSON diagnostics also include:

- `uid`: the detected effective user id, or `null` when unavailable.
- `elevated`: `true`, `false`, or `null` when unknown.
- `permission_scope`: a stable string for CI logs and issue reports.
- `missing_tools`: a de-duplicated list of missing required and port-check tools.
- `install_hints`: platform-specific installation or environment guidance keyed by missing tool name.

Recommended troubleshooting flow:

1. Run `portforge doctor`.
2. Check `status` and `failure_reasons` first.
3. If `missing_tools` is not empty, follow `install_hints` before retrying a scan.
4. If tools are available but process details are incomplete, compare `permission_scope` with the owner of the development service.
5. Re-run the same local check with a broader permission context only when the machine is trusted and the missing process details are needed.

Example JSON fragment:

```json
{
  "schema_version": 2,
  "environment": "native",
  "permission_scope": "user",
  "uid": 501,
  "elevated": false,
  "status": "degraded",
  "failure_reasons": ["missing_port_check_backend"],
  "missing_tools": ["lsof", "ss"],
  "install_hints": {
    "lsof": "Install lsof with your system package manager, for example apt install lsof or dnf install lsof.",
    "ss": "Install iproute2 to provide ss, for example apt install iproute2 or dnf install iproute."
  }
}
```
