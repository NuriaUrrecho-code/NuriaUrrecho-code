from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / "state"
LOGS_DIR = STATE_DIR / "logs"
CONFIG_PATH = STATE_DIR / "config.json"
POINTS_PATH = STATE_DIR / "selected_points.json"
LAST_POSITION_PATH = STATE_DIR / "last_position.json"
CALIBRATION_INFO_PATH = STATE_DIR / "calibration_info.json"
POSITION_LOG_PATH = LOGS_DIR / "positions.jsonl"
BACKGROUND_IMAGE_PATH = STATE_DIR / "background_reference.png"

DEFAULT_CONFIG = {
    "project_title": "Posicionamiento planar de mandarinas",
    "authors": [
        "Carla Castellanos",
        "Gabriel Arnedo",
        "Nuria Urrecho",
        "Pablo Gomez",
    ],
    "camera_index": 3,
    "mqtt_broker": "broker.emqx.io",
    "mqtt_port": 1883,
    "mqtt_topic": "richi5/mandarinas/posicion",
    "object_radius_cm": 1.5,
    "camera_height_cm": 37.0,
    "height_correction_mode": "manual_camera_height",
    "detection_mode": "automatic",
    "tracking_mode": "first_frame",
    "opencv_tracker": "kcf",
    "target_world": [15.0, 10.0],
    "hsv_lower": [5, 100, 100],
    "hsv_upper": [20, 255, 255],
    "world_points_cm": [
        [0.0, 0.0],
        [29.7, 0.0],
        [29.7, 21.0],
        [0.0, 21.0],
    ],
}


def ensure_state_dirs() -> None:
    STATE_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)


def _timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: Any) -> None:
    ensure_state_dirs()
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def load_config() -> dict[str, Any]:
    ensure_state_dirs()
    config = DEFAULT_CONFIG.copy()
    config.update(load_json(CONFIG_PATH, {}))
    # Final delivery mode is fixed: automatic detection on the first frame
    # and KCF tracking. The camera height can remain manual if measured.
    config["detection_mode"] = "automatic"
    config["tracking_mode"] = "first_frame"
    config["opencv_tracker"] = "kcf"
    return config


def save_config(config: dict[str, Any]) -> None:
    save_json(CONFIG_PATH, config)


def save_selected_points(points: list[list[int]]) -> None:
    save_json(
        POINTS_PATH,
        {
            "saved_at": _timestamp(),
            "points": points,
        },
    )


def load_selected_points() -> list[list[float]]:
    data = load_json(POINTS_PATH, {})
    return data.get("points", [])


def save_calibration_info(payload: dict[str, Any]) -> None:
    current = load_json(CALIBRATION_INFO_PATH, {})
    current.update(payload)
    current["updated_at"] = _timestamp()
    save_json(CALIBRATION_INFO_PATH, current)


def append_position(payload: dict[str, Any]) -> None:
    ensure_state_dirs()
    entry = {"timestamp": _timestamp(), **payload}
    with POSITION_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    save_json(LAST_POSITION_PATH, entry)
