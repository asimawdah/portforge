# PortPilot

Find and free busy development ports in seconds.

PortPilot helps developers quickly answer the question: **what is using port 3000?** It shows the process, PID, command, and gives you a safe kill command when you want to free the port.

## Install

```bash
pip install portpilot
```

The installed command is:

```bash
portpilot
```

## Usage

Check one port:

```bash
portpilot 3000
```

Scan common development ports:

```bash
portpilot scan
```

Scan custom ports:

```bash
portpilot scan -p 3000,5173,8000
```

Output JSON:

```bash
portpilot 3000 --json
```

Write output to a file:

```bash
portpilot 3000 -o ports.json --json
```

Free a busy port safely:

```bash
portpilot kill 3000 --yes
```

Force kill with SIGKILL:

```bash
portpilot kill 3000 --yes --force
```

## CLI shortcuts

- `-p`, `--ports`: comma-separated ports for scan
- `-j`, `--json`: output JSON
- `-o`, `--output`: write output to file
- `-y`, `--yes`: confirm kill action
- `-f`, `--force`: use SIGKILL instead of SIGTERM

## Example

```text
$ portpilot 3000
Port 3000 is busy

PID      USER         NAME             COMMAND
18422    asim         node             npm run dev

Actions:
  portpilot kill 3000
```

```text
$ portpilot scan
PortPilot scan

PORT     STATUS   PROCESS
3000     busy     node
3001     free     -
5173     free     -
8000     busy     python
```

## Development

```bash
python3 -m unittest discover -s tests -v
```

## Roadmap

- [x] Check a single port
- [x] Scan common development ports
- [x] JSON output
- [x] Safe kill with explicit confirmation
- [ ] Interactive kill confirmation
- [ ] Project directory detection from process cwd
- [ ] Windows support improvements
- [ ] Rich colored output

## License

MIT
