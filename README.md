# PortLane

Find and free busy development ports in seconds.

PortLane helps developers quickly answer the question: **what is using port 3000?** It shows the process, PID, command, and gives you a safe command when you want to free the port.

## Install

```bash
pip install portlane
```

The installed command is:

```bash
portlane
```

## Usage

Check one port:

```bash
portlane 3000
```

Scan common development ports:

```bash
portlane scan
```

Scan custom ports:

```bash
portlane scan -p 3000,5173,8000
```

Output JSON:

```bash
portlane 3000 --json
```

Write output to a file:

```bash
portlane 3000 -o ports.json --json
```

Free a busy port after confirmation:

```bash
portlane kill 3000 --yes
```

## Safety notes

- Review the displayed process name, PID, user, and command before killing anything.
- Prefer the normal kill command first; use `--force` only when a process does not stop cleanly.
- Avoid running kill commands against system services or processes you do not recognize.
- When using `--json` or `--output`, review files before sharing them because command paths can include local usernames or project names.

## Platform support

PortLane is designed for local development workflows on Unix-like systems where process and port inspection tools are available. Windows support is planned, but it may require different process lookup behavior.

## CLI shortcuts

- `-p`, `--ports`: comma-separated ports for scan
- `-j`, `--json`: output JSON
- `-o`, `--output`: write output to file
- `-y`, `--yes`: confirm port-freeing action
- `-f`, `--force`: use a stronger termination signal

## Example

```text
$ portlane 3000
Port 3000 is busy

PID      USER         NAME             COMMAND
18422    asim         node             npm run dev

Actions:
  portlane kill 3000
```

```text
$ portlane scan
PortLane scan

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
- [x] Safe port freeing with explicit confirmation
- [ ] Interactive confirmation
- [ ] Project directory detection from process cwd
- [ ] Windows support improvements
- [ ] Rich colored output

## License

MIT
