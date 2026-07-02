# PortForge

Find and free busy development ports in seconds.

PortForge helps developers quickly answer the question: **what is using port 3000?** It shows the process, PID, command, and gives you a safe command when you want to free the port. It also adds practical hints for common development ports so you can recognize likely services before stopping anything.

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

## Port conflict hints

PortForge includes built-in hints for common local-development ports. These hints do not replace the actual process details; they give quick context so you can decide whether a busy port is probably safe to stop.

| Port | Common service hint |
| --- | --- |
| `3000` | Node, Next.js, or React dev server |
| `3001` | Alternate frontend/API dev server |
| `4173` | Vite preview |
| `5000` | Flask/API dev server |
| `5173` | Vite dev server |
| `8000` | Django, FastAPI, or Python dev server |
| `8080` | HTTP proxy, API, or dev server |
| `9000` | Backend service or MinIO |
| `3306` | MySQL/MariaDB |
| `5432` | PostgreSQL |
| `6379` | Redis |
| `27017` | MongoDB |

Example scan output with hints:

```text
$ portforge scan
PortForge scan

PORT     STATUS   PROCESS            HINT
3000     busy     node               Node/Next.js/React dev server
5173     free     -                  Vite dev server
5432     busy     postgres           PostgreSQL
```

Machine-readable JSON also includes a `hint` object when a known port has guidance:

```json
[
  {
    "port": 3000,
    "busy": true,
    "processes": [],
    "hint": {
      "service": "Node/Next.js/React dev server",
      "note": "Check npm, pnpm, yarn, or a frontend framework dev process."
    }
  }
]
```

## Safety notes

- Review the displayed process name, PID, user, and command before killing anything.
- Treat service hints as guidance only; always verify the actual process command before stopping a port.
- Prefer the normal kill command first; use `--force` only when a process does not stop cleanly.
- Avoid running kill commands against system services or processes you do not recognize.
- Be extra careful with database ports such as PostgreSQL, MySQL, Redis, and MongoDB because active projects may depend on them.
- When using `--json` or `--output`, review files before sharing them because command paths can include local usernames or project names.

## Platform support

PortForge is designed for local development workflows on Unix-like systems where process and port inspection tools are available. Windows support is planned, but it may require different process lookup behavior.

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

Hint:
  Common use: Node/Next.js/React dev server
  Check npm, pnpm, yarn, or a frontend framework dev process.

Actions:
  portforge kill 3000
```

```text
$ portforge scan
PortForge scan

PORT     STATUS   PROCESS            HINT
3000     busy     node               Node/Next.js/React dev server
3001     free     -                  Alternate frontend/API dev server
5173     free     -                  Vite dev server
8000     busy     python             Django/FastAPI/Python dev server
```

## Development

```bash
python3 -m unittest discover -s tests -v
```

## Roadmap

- [x] Check a single port
- [x] Scan common development ports
- [x] JSON output
- [x] Safe port freeing with explicit confirmation
- [x] Known service hints for common development ports
- [ ] Interactive confirmation
- [ ] Project directory detection from process cwd
- [ ] Windows support improvements
- [ ] Rich colored output

## License

MIT
