from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceHint:
    """Human-readable guidance for ports commonly used in local development."""

    service: str
    note: str


SERVICE_HINTS: dict[int, ServiceHint] = {
    3000: ServiceHint("Node/Next.js/React dev server", "Check npm, pnpm, yarn, or a frontend framework dev process."),
    3001: ServiceHint("Alternate frontend/API dev server", "Often used when port 3000 is already occupied."),
    3306: ServiceHint("MySQL/MariaDB", "Confirm this is not a local database you still need before stopping it."),
    4173: ServiceHint("Vite preview", "Usually started with `vite preview` or a framework preview command."),
    5000: ServiceHint("Flask/API dev server", "Common for Python APIs and local backend services."),
    5173: ServiceHint("Vite dev server", "Usually started by a frontend app with `npm run dev`."),
    5432: ServiceHint("PostgreSQL", "Use caution before stopping database services with active projects."),
    6379: ServiceHint("Redis", "Use caution if queues, caches, or workers depend on this instance."),
    8000: ServiceHint("Django/FastAPI/Python dev server", "Common for Python web apps and API servers."),
    8080: ServiceHint("HTTP proxy/API/dev server", "Common for backend services, proxies, and admin UIs."),
    9000: ServiceHint("Backend service or MinIO", "Check the command to confirm the owning service."),
    27017: ServiceHint("MongoDB", "Use caution before stopping a local database used by active projects."),
}


def get_service_hint(port: int) -> ServiceHint | None:
    """Return a practical local-development hint for a known port."""

    return SERVICE_HINTS.get(port)


def format_service_hint(port: int) -> str:
    """Return a compact label suitable for tables and CLI reports."""

    hint = get_service_hint(port)
    if hint is None:
        return "-"
    return hint.service
