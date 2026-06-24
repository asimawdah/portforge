from __future__ import annotations

PORT_PRESETS: dict[str, list[int]] = {
    "common": [3000, 3001, 5173, 8000, 8080, 5000, 5432, 3306, 6379],
    "frontend": [3000, 3001, 4173, 5173, 8080],
    "backend": [5000, 8000, 8080, 9000],
    "databases": [3306, 5432, 6379, 27017],
}

DEFAULT_PRESET = "common"
DEFAULT_SCAN_PORTS = PORT_PRESETS[DEFAULT_PRESET]
