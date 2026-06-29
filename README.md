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
- The port is busy on a protocol or address family outside the current TCP listener lookup.
- Native Windows process lookup is being used instead of WSL.

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
Ready: yes

Required tools:
  ps       ok (/bin/ps)

Port check tools:
  lsof     ok (/usr/sbin/lsof)
  ss       missing

Notes:
- macOS usually works best with lsof available from the base system.
```

## Development

```bash
python3 -m unittest discover -s tests -v
```

Manual cross-platform checks before release:

```bash
portforge doctor
portforge scan --preset frontend
portforge 3000 --json
```

## Roadmap

- [x] Check a single port
- [x] Scan common development ports
- [x] JSON output
- [x] Safe port freeing with explicit confirmation
- [x] Platform diagnostics with `portforge doctor`
- [ ] Interactive confirmation
- [ ] Project directory detection from process cwd
- [ ] Windows support improvements
- [ ] Rich colored output

## License

MIT
