from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    name: str
    user: str
    command: str
    address: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PortCheck:
    port: int
    processes: list[ProcessInfo]

    @property
    def busy(self) -> bool:
        return bool(self.processes)

    def to_dict(self) -> dict[str, object]:
        return {
            "port": self.port,
            "busy": self.busy,
            "processes": [process.to_dict() for process in self.processes],
        }
