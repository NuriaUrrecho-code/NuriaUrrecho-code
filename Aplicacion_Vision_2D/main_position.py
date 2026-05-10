from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

try:
    import paho.mqtt.client as mqtt
except ModuleNotFoundError:
    mqtt = None

from app_state import BACKGROUND_IMAGE_PATH, append_position, ensure_state_dirs, load_config, load_selected_points


CALIBRATION_DIR = Path(__file__).resolve().parent / "calibration"
MAX_OBJECTS = 3
MIN_CONTOUR_AREA_PX = 500
MORPH_KERNEL_SIZE = (5, 5)
PREVIEW_EXIT_KEYS = [27, ord("q")]
DEFAULT_MAX_MISSING_FRAMES = 20
DEFAULT_MATCH_DISTANCE_CM = 8.0


def get_available_tracker_factories() -> dict[str, object]:
    """Return the tracker factories available in this OpenCV build."""
    tracker_factories: dict[str, object] = {}

    for name in ("CSRT", "KCF", "MIL"):
        factory = getattr(cv2, f"Tracker{name}_create", None)
        if factory is None:
            legacy = getattr(cv2, "legacy", None)
            if legacy is not None:
                factory = getattr(legacy, f"Tracker{name}_create", None)
        if factory is not None:
            tracker_factories[name] = factory

    return tracker_factories


def load_calibration() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load homography, intrinsics and distortion coefficients from disk."""
    h_path = CALIBRATION_DIR / "H.npy"
    k_path = CALIBRATION_DIR / "K.npy"
    dist_path = CALIBRATION_DIR / "dist.npy"

    if not h_path.exists() or not k_path.exists() or not dist_path.exists():
        raise FileNotFoundError(
            "Faltan archivos de calibracion. Ejecuta primero la calibracion de camara y la homografia."
        )

    return np.load(h_path), np.load(k_path), np.load(dist_path)


def build_pose(
    K: np.ndarray,
    dist: np.ndarray,
    image_points: list[list[float]],
    world_points: list[list[float]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Estimate the camera pose from 4 coplanar image-world correspondences."""
    if len(image_points) != 4 or len(world_points) != 4:
        raise FileNotFoundError(
            "Faltan 4 correspondencias plano-imagen para estimar la pose. Vuelve a seleccionar los puntos."
        )

    object_points = np.array(
        [[float(x_cm), float(y_cm), 0.0] for x_cm, y_cm in world_points],
        dtype=np.float32,
    )
    image_points_np = np.array(image_points, dtype=np.float32).reshape(-1, 1, 2)
    # solvePnP is more stable here if the image points are first expressed in
    # normalized coordinates, instead of mixing raw pixels with distortion.
    normalized_image_points = cv2.undistortPoints(image_points_np, K, dist).reshape(-1, 2)

    success, rvec, tvec = cv2.solvePnP(
        object_points,
        normalized_image_points,
        np.eye(3, dtype=np.float32),
        None,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not success:
        raise RuntimeError("No se pudo estimar la pose de la camara con solvePnP.")

    rotation, _ = cv2.Rodrigues(rvec)
    return rvec, tvec, rotation


def compute_pose_reprojection_error(
    rvec: np.ndarray,
    tvec: np.ndarray,
    K: np.ndarray,
    dist: np.ndarray,
    image_points: list[list[float]],
    world_points: list[list[float]],
) -> float:
    """Measure pose quality in normalized image coordinates."""
    object_points = np.array(
        [[float(x_cm), float(y_cm), 0.0] for x_cm, y_cm in world_points],
        dtype=np.float32,
    )
    projected_points, _ = cv2.projectPoints(
        object_points,
        rvec,
        tvec,
        np.eye(3, dtype=np.float32),
        None,
    )
    normalized_image_points = cv2.undistortPoints(
        np.array(image_points, dtype=np.float32).reshape(-1, 1, 2),
        K,
        dist,
    )
    error = cv2.norm(normalized_image_points, projected_points, cv2.NORM_L2) / len(projected_points)
    return float(error)


def estimate_camera_height_from_pose(rotation: np.ndarray, tvec: np.ndarray) -> float:
    """Recover camera height from the estimated extrinsic pose."""
    camera_center = -rotation.T @ tvec
    return abs(float(camera_center[2, 0]))


def estimate_camera_center_from_pose(rotation: np.ndarray, tvec: np.ndarray) -> tuple[float, float, float]:
    """Recover the camera center in world coordinates from the extrinsic pose."""
    camera_center = -rotation.T @ tvec
    return (
        float(camera_center[0, 0]),
        float(camera_center[1, 0]),
        abs(float(camera_center[2, 0])),
    )


def correct_planar_position(
    x_cm: float,
    y_cm: float,
    object_radius_cm: float,
    config: dict,
    estimated_camera_height_cm: float,
    camera_projection_xy_cm: tuple[float, float] = (0.0, 0.0),
) -> tuple[float, float, float]:
    """Compensate the planar position when the object center is above the work plane."""
    correction_mode = config.get("height_correction_mode", "manual_camera_height")
    if correction_mode == "pose_estimated_height":
        camera_height_cm = estimated_camera_height_cm
    else:
        camera_height_cm = float(config["camera_height_cm"])

    if camera_height_cm <= object_radius_cm:
        return x_cm, y_cm, camera_height_cm

    # The detected centroid belongs to a point above the plane. We shrink the
    # planar coordinates towards the camera projection using similar triangles.
    factor = camera_height_cm / (camera_height_cm - object_radius_cm)
    camera_x_cm, camera_y_cm = camera_projection_xy_cm
    x_corr = camera_x_cm + (x_cm - camera_x_cm) / factor
    y_corr = camera_y_cm + (y_cm - camera_y_cm) / factor
    return x_corr, y_corr, camera_height_cm


def world_to_pixel(
    x_cm: float,
    y_cm: float,
    z_cm: float,
    rvec: np.ndarray,
    tvec: np.ndarray,
    K: np.ndarray,
    dist: np.ndarray,
) -> tuple[int, int]:
    pt = np.array([[[x_cm, y_cm, z_cm]]], dtype=np.float64)
    px, _ = cv2.projectPoints(pt, rvec, tvec, K, dist)
    return tuple(px[0][0].astype(int))


def create_client(config: dict):
    """Create the MQTT client if the dependency and broker are available."""
    if mqtt is None:
        print("paho-mqtt no esta instalado. Se ejecutara sin publicar por MQTT.")
        return None

    try:
        client = mqtt.Client()
        client.connect(config["mqtt_broker"], config["mqtt_port"], keepalive=60)
        client.loop_start()
        return client
    except Exception as exc:
        print(f"No se pudo conectar al broker MQTT: {exc}")
        return None


def assign_ids(
    detections: list[dict[str, float]],
    tracks: dict[int, dict[str, float]],
    max_objects: int,
    max_missing_frames: int = DEFAULT_MAX_MISSING_FRAMES,
    match_distance_cm: float = DEFAULT_MATCH_DISTANCE_CM,
) -> list[dict[str, float]]:
    """Keep stable object identifiers across frames using nearest-neighbor matching."""
    assignments: list[dict[str, float]] = []
    remaining = list(enumerate(detections))
    matched_ids = set()
    matched_detection_indices = set()

    candidates: list[tuple[float, int, int]] = []
    max_distance_sq = match_distance_cm ** 2

    for object_id, track in tracks.items():
        prev_x = float(track["x"])
        prev_y = float(track["y"])
        for det_idx, detection in remaining:
            distance_sq = (float(detection["x"]) - prev_x) ** 2 + (float(detection["y"]) - prev_y) ** 2
            if distance_sq <= max_distance_sq:
                candidates.append((distance_sq, object_id, det_idx))

    candidates.sort(key=lambda item: item[0])

    # Greedy assignment works well here because the number of tracked objects
    # is small and the frame-to-frame motion is limited.
    for _, object_id, det_idx in candidates:
        if object_id in matched_ids or det_idx in matched_detection_indices:
            continue

        detection = detections[det_idx]
        detection["object_id"] = object_id
        assignments.append(detection)
        matched_ids.add(object_id)
        matched_detection_indices.add(det_idx)
        tracks[object_id] = {
            "x": float(detection["x"]),
            "y": float(detection["y"]),
            "missing_frames": 0,
        }

    for object_id, track in list(tracks.items()):
        if object_id in matched_ids:
            continue

        missing_frames = int(track.get("missing_frames", 0)) + 1
        if missing_frames > max_missing_frames:
            del tracks[object_id]
        else:
            track["missing_frames"] = missing_frames
            tracks[object_id] = track

    next_ids = [idx for idx in range(1, max_objects + 1) if idx not in tracks]
    unmatched_detections = [
        detections[idx] for idx in range(len(detections)) if idx not in matched_detection_indices
    ]
    unmatched_detections.sort(key=lambda item: item["x"])
    for object_id, detection in zip(next_ids, unmatched_detections):
        detection["object_id"] = object_id
        assignments.append(detection)
        tracks[object_id] = {
            "x": float(detection["x"]),
            "y": float(detection["y"]),
            "missing_frames": 0,
        }

    assignments.sort(key=lambda item: item["object_id"])
    return assignments


def create_tracker(tracker_name: str = "auto"):
    """Create the configured tracker, or the best available one in auto mode."""
    tracker_factories = get_available_tracker_factories()
    if not tracker_factories:
        raise RuntimeError("No hay trackers disponibles en esta instalacion de OpenCV.")

    normalized_name = str(tracker_name).upper()
    if normalized_name == "AUTO":
        for name in ("CSRT", "KCF", "MIL"):
            factory = tracker_factories.get(name)
            if factory is not None:
                return factory()
        raise RuntimeError("No hay trackers disponibles en esta instalacion de OpenCV.")

    factory = tracker_factories.get(normalized_name)
    if factory is None:
        available = ", ".join(tracker_factories.keys())
        raise RuntimeError(
            f"El tracker '{tracker_name}' no esta disponible. Disponibles: {available}."
        )

    return factory()


def contour_to_bbox(contour: np.ndarray) -> tuple[int, int, int, int]:
    """Convert a contour into an integer bounding box."""
    x, y, width, height = cv2.boundingRect(contour)
    return int(x), int(y), int(width), int(height)


def detect_objects(
    frame: np.ndarray,
    hsv_lower: np.ndarray,
    hsv_upper: np.ndarray,
    kernel: np.ndarray,
    max_objects: int,
) -> tuple[np.ndarray, list[dict[str, object]]]:
    """Detect orange objects in the current frame and return mask plus detections."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # A simple area filter removes small blobs caused by reflections and noise.
    valid_contours = [
        contour for contour in contours if cv2.contourArea(contour) > MIN_CONTOUR_AREA_PX
    ]
    valid_contours.sort(key=cv2.contourArea, reverse=True)
    valid_contours = valid_contours[:max_objects]

    detections: list[dict[str, object]] = []
    for contour in valid_contours:
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        detections.append(
            {
                "contour": contour,
                "bbox": contour_to_bbox(contour),
                "cx": cx,
                "cy": cy,
            }
        )

    return mask, detections


def detect_objects_with_background(
    frame: np.ndarray,
    background_frame: np.ndarray,
    kernel: np.ndarray,
    max_objects: int,
    threshold_value: int = 25,
) -> tuple[np.ndarray, list[dict[str, object]]]:
    """Detect objects by subtracting a stored static background."""
    frame_blur = cv2.GaussianBlur(frame, (5, 5), 0)
    background_blur = cv2.GaussianBlur(background_frame, (5, 5), 0)

    diff = cv2.absdiff(frame_blur, background_blur)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(diff_gray, threshold_value, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_contours = [
        contour for contour in contours if cv2.contourArea(contour) > MIN_CONTOUR_AREA_PX
    ]
    valid_contours.sort(key=cv2.contourArea, reverse=True)
    valid_contours = valid_contours[:max_objects]

    detections: list[dict[str, object]] = []
    for contour in valid_contours:
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        detections.append(
            {
                "contour": contour,
                "bbox": contour_to_bbox(contour),
                "cx": cx,
                "cy": cy,
            }
        )

    return mask, detections


def pixel_to_world(
    cx: int,
    cy: int,
    H: np.ndarray,
    K: np.ndarray,
    dist: np.ndarray,
) -> tuple[float, float]:
    """Project a detected image point onto the calibrated work plane."""
    pt_raw = np.array([[[cx, cy]]], dtype=np.float32)
    pt_ok = cv2.undistortPoints(pt_raw, K, dist, P=K)
    pt_h = np.array([[[pt_ok[0][0][0], pt_ok[0][0][1]]]], dtype=np.float32)
    world = cv2.perspectiveTransform(pt_h, H)
    x_cm, y_cm = world[0][0]
    return float(x_cm), float(y_cm)


def build_object_payload(
    object_id: int,
    cx: int,
    cy: int,
    H: np.ndarray,
    K: np.ndarray,
    dist: np.ndarray,
    object_radius_cm: float,
    config: dict,
    estimated_camera_height_cm: float,
    camera_projection_xy_cm: tuple[float, float],
) -> dict[str, float | int]:
    """Build the published position payload from an image-space detection."""
    x_cm, y_cm = pixel_to_world(cx, cy, H, K, dist)
    x_corr, y_corr, used_camera_height_cm = correct_planar_position(
        x_cm,
        y_cm,
        object_radius_cm,
        config,
        estimated_camera_height_cm,
        camera_projection_xy_cm,
    )
    return {
        "object_id": object_id,
        "x": round(float(x_corr), 2),
        "y": round(float(y_corr), 2),
        "x_uncorrected": round(float(x_cm), 2),
        "y_uncorrected": round(float(y_cm), 2),
        "z": round(object_radius_cm, 2),
        "camera_height_used_cm": round(float(used_camera_height_cm), 2),
        "cx": int(cx),
        "cy": int(cy),
    }


def publish_and_draw_detections(
    result: np.ndarray,
    assigned_detections: list[dict[str, float | int]],
    client,
    config: dict,
    save_positions: bool,
) -> None:
    """Publish positions and annotate the visualization frame."""
    if not assigned_detections:
        return

    for detection in assigned_detections:
        object_id = int(detection["object_id"])
        object_name = f"mandarina_{object_id}"
        object_payload = {
            "id": object_name,
            "x": detection["x"],
            "y": detection["y"],
            "z": detection["z"],
        }

        if client is not None:
            client.publish(config["mqtt_topic"], json.dumps(object_payload))

        if save_positions:
            append_position(object_payload)

        cv2.putText(
            result,
            object_name,
            (int(detection["cx"]) + 10, int(detection["cy"]) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

    summary_text = " | ".join(
        f"m{int(d['object_id'])}: ({float(d['x']):.1f}, {float(d['y']):.1f}, {float(d['z']):.1f})"
        for d in assigned_detections
    )
    cv2.putText(
        result,
        summary_text[:120],
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
    )

    uncorrected_text = " | ".join(
        f"m{int(d['object_id'])} sin corr: ({float(d['x_uncorrected']):.1f}, {float(d['y_uncorrected']):.1f})"
        for d in assigned_detections
    )
    cv2.putText(
        result,
        uncorrected_text[:120],
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2,
    )


def initialize_manual_trackers(
    frame: np.ndarray,
    max_objects: int,
    tracker_name: str,
) -> list[dict[str, object]]:
    """Initialize trackers from user-selected ROIs on the first frame."""
    # Manual initialization is intended for the "detect once, track later"
    # workflow used in the practices and in the project rubric.
    rois = cv2.selectROIs(
        "Seleccion manual de mandarinas",
        frame,
        showCrosshair=True,
        fromCenter=False,
    )
    cv2.destroyWindow("Seleccion manual de mandarinas")

    trackers: list[dict[str, object]] = []
    for index, roi in enumerate(rois[:max_objects], start=1):
        x, y, width, height = [int(value) for value in roi]
        if width <= 0 or height <= 0:
            continue
        tracker = create_tracker(tracker_name)
        tracker.init(frame, (x, y, width, height))
        trackers.append(
            {
                "tracker": tracker,
                "object_id": index,
            }
        )
    return trackers


def initialize_auto_trackers(
    frame: np.ndarray,
    hsv_lower: np.ndarray,
    hsv_upper: np.ndarray,
    kernel: np.ndarray,
    max_objects: int,
    tracker_name: str,
) -> tuple[np.ndarray, list[dict[str, object]]]:
    """Detect objects on the first frame and initialize one tracker per object."""
    mask, detections = detect_objects(frame, hsv_lower, hsv_upper, kernel, max_objects)

    trackers: list[dict[str, object]] = []
    for index, detection in enumerate(detections, start=1):
        bbox = detection["bbox"]
        tracker = create_tracker(tracker_name)
        tracker.init(frame, bbox)
        trackers.append(
            {
                "tracker": tracker,
                "object_id": index,
            }
        )

    return mask, trackers


def initialize_background_trackers(
    frame: np.ndarray,
    kernel: np.ndarray,
    max_objects: int,
    tracker_name: str,
) -> tuple[np.ndarray, list[dict[str, object]]]:
    """Detect objects on the first frame using background subtraction and seed trackers."""
    if not BACKGROUND_IMAGE_PATH.exists():
        raise FileNotFoundError(
            "No existe fondo guardado. Ejecuta primero la opcion de capturar fondo."
        )

    background_frame = cv2.imread(str(BACKGROUND_IMAGE_PATH))
    if background_frame is None:
        raise FileNotFoundError("No se pudo leer la imagen de fondo guardada.")

    if frame.shape != background_frame.shape:
        background_frame = cv2.resize(
            background_frame,
            (frame.shape[1], frame.shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )

    mask, detections = detect_objects_with_background(
        frame,
        background_frame,
        kernel,
        max_objects,
    )

    trackers: list[dict[str, object]] = []
    for index, detection in enumerate(detections, start=1):
        bbox = detection["bbox"]
        tracker = create_tracker(tracker_name)
        tracker.init(frame, bbox)
        trackers.append(
            {
                "tracker": tracker,
                "object_id": index,
            }
        )

    return mask, trackers


def run_initialized_tracking(initialization_mode: str, save_positions: bool = True) -> None:
    """Run tracking after a single automatic or manual initialization step."""
    config = load_config()
    H, K, dist = load_calibration()
    image_points = load_selected_points()
    world_points = config["world_points_cm"]
    rvec, tvec, rotation = build_pose(K, dist, image_points, world_points)

    cap = cv2.VideoCapture(config["camera_index"])
    if not cap.isOpened():
        print("No se pudo abrir la camara")
        return

    ret, first_frame = cap.read()
    if not ret:
        print("No se pudo leer el primer frame de la camara")
        cap.release()
        return

    client = create_client(config)
    kernel = np.ones(MORPH_KERNEL_SIZE, np.uint8)
    hsv_lower = np.array(config["hsv_lower"])
    hsv_upper = np.array(config["hsv_upper"])
    object_radius_cm = float(config["object_radius_cm"])
    max_objects = MAX_OBJECTS
    tracker_name = str(config.get("opencv_tracker", "auto"))
    camera_center_x_cm, camera_center_y_cm, estimated_camera_height_cm = (
        estimate_camera_center_from_pose(rotation, tvec)
    )

    if initialization_mode == "manual":
        trackers = initialize_manual_trackers(first_frame, max_objects, tracker_name)
        mask = None
    elif initialization_mode == "background":
        # Use the captured empty scene only to initialize the boxes once, then
        # keep tracking with the configured OpenCV tracker.
        mask, trackers = initialize_background_trackers(
            first_frame,
            kernel,
            max_objects,
            tracker_name,
        )
    else:
        # In automatic first-frame mode the detector is only used once to seed
        # the trackers. The rest of the sequence relies on tracking only.
        mask, trackers = initialize_auto_trackers(
            first_frame,
            hsv_lower,
            hsv_upper,
            kernel,
            max_objects,
            tracker_name,
        )

    if not trackers:
        print("No se pudo inicializar ningun tracker.")
        if client is not None:
            client.loop_stop()
            client.disconnect()
        cap.release()
        cv2.destroyAllWindows()
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = frame.copy()
        assigned_detections: list[dict[str, float | int]] = []

        for tracked_object in trackers:
            ok, bbox = tracked_object["tracker"].update(frame)
            if not ok:
                continue

            x, y, width, height = [int(value) for value in bbox]
            cx = x + width // 2
            cy = y + height // 2
            cv2.rectangle(result, (x, y), (x + width, y + height), (255, 0, 0), 2)
            cv2.circle(result, (cx, cy), 5, (0, 255, 255), -1)

            assigned_detections.append(
                build_object_payload(
                    int(tracked_object["object_id"]),
                    cx,
                    cy,
                    H,
                    K,
                    dist,
                    object_radius_cm,
                    config,
                    estimated_camera_height_cm,
                    (camera_center_x_cm, camera_center_y_cm),
                )
            )

        assigned_detections.sort(key=lambda item: int(item["object_id"]))
        publish_and_draw_detections(result, assigned_detections, client, config, save_positions)

        cv2.imshow("Resultado (AR)", result)
        if mask is not None:
            cv2.imshow("Mascara", mask)

        if cv2.waitKey(1) & 0xFF in PREVIEW_EXIT_KEYS:
            break

    if client is not None:
        client.loop_stop()
        client.disconnect()
    cap.release()
    cv2.destroyAllWindows()


def preview_camera() -> None:
    """Open a plain camera preview without detection or tracking."""
    config = load_config()
    cap = cv2.VideoCapture(config["camera_index"])
    if not cap.isOpened():
        print("No se pudo abrir la camara")
        return

    print("Vista previa activa. Pulsa q o ESC para salir.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Vista previa camara", frame)
        if cv2.waitKey(1) & 0xFF in PREVIEW_EXIT_KEYS:
            break

    cap.release()
    cv2.destroyAllWindows()


def capture_background_reference() -> None:
    """Capture and store a clean background frame for subtraction tests."""
    config = load_config()
    cap = cv2.VideoCapture(config["camera_index"])
    if not cap.isOpened():
        print("No se pudo abrir la camara")
        return

    print("Coloca la escena sin mandarinas. Pulsa c para capturar el fondo, q o ESC para salir.")
    captured_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        preview = frame.copy()
        cv2.putText(
            preview,
            "c: capturar fondo | q/ESC: salir",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.imshow("Captura de fondo", preview)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):
            captured_frame = frame.copy()
            break
        if key in PREVIEW_EXIT_KEYS:
            break

    if captured_frame is not None:
        ensure_state_dirs()
        cv2.imwrite(str(BACKGROUND_IMAGE_PATH), captured_frame)
        print(f"Fondo guardado en: {BACKGROUND_IMAGE_PATH}")
    else:
        print("No se guardo ningun fondo.")

    cap.release()
    cv2.destroyAllWindows()


def preview_background_detection() -> None:
    """Preview object detection using a previously captured background frame."""
    if not BACKGROUND_IMAGE_PATH.exists():
        raise FileNotFoundError(
            "No existe fondo guardado. Ejecuta primero la opcion de capturar fondo."
        )

    background_frame = cv2.imread(str(BACKGROUND_IMAGE_PATH))
    if background_frame is None:
        raise FileNotFoundError("No se pudo leer la imagen de fondo guardada.")

    config = load_config()
    cap = cv2.VideoCapture(config["camera_index"])
    if not cap.isOpened():
        print("No se pudo abrir la camara")
        return

    kernel = np.ones(MORPH_KERNEL_SIZE, np.uint8)
    max_objects = MAX_OBJECTS

    print("Prueba de deteccion por fondo activa. Pulsa q o ESC para salir.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame.shape != background_frame.shape:
            resized_background = cv2.resize(
                background_frame,
                (frame.shape[1], frame.shape[0]),
                interpolation=cv2.INTER_LINEAR,
            )
        else:
            resized_background = background_frame

        mask, detections = detect_objects_with_background(
            frame,
            resized_background,
            kernel,
            max_objects,
        )

        result = frame.copy()
        for detection in detections:
            contour = detection["contour"]
            x, y, width, height = detection["bbox"]
            cx = int(detection["cx"])
            cy = int(detection["cy"])
            cv2.drawContours(result, [contour], -1, (0, 255, 0), 2)
            cv2.rectangle(result, (x, y), (x + width, y + height), (255, 0, 0), 2)
            cv2.circle(result, (cx, cy), 5, (0, 255, 255), -1)

        cv2.putText(
            result,
            f"Detecciones por fondo: {len(detections)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.imshow("Deteccion por fondo", result)
        cv2.imshow("Mascara fondo", mask)

        if cv2.waitKey(1) & 0xFF in PREVIEW_EXIT_KEYS:
            break

    cap.release()
    cv2.destroyAllWindows()


def run_tracking_continuous(save_positions: bool = True) -> None:
    """Detect objects on every frame and keep identities over time."""
    config = load_config()
    H, K, dist = load_calibration()
    image_points = load_selected_points()
    world_points = config["world_points_cm"]
    rvec, tvec, rotation = build_pose(K, dist, image_points, world_points)
    cap = cv2.VideoCapture(config["camera_index"])
    if not cap.isOpened():
        print("No se pudo abrir la camara")
        return

    client = create_client(config)
    kernel = np.ones(MORPH_KERNEL_SIZE, np.uint8)
    hsv_lower = np.array(config["hsv_lower"])
    hsv_upper = np.array(config["hsv_upper"])
    object_radius_cm = float(config["object_radius_cm"])
    max_objects = MAX_OBJECTS
    tracks: dict[int, dict[str, float]] = {}
    camera_center_x_cm, camera_center_y_cm, estimated_camera_height_cm = (
        estimate_camera_center_from_pose(rotation, tvec)
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = frame.copy()

        mask, raw_detections = detect_objects(frame, hsv_lower, hsv_upper, kernel, max_objects)

        detections: list[dict[str, float]] = []
        for detection in raw_detections:
            contour = detection["contour"]
            cx = int(detection["cx"])
            cy = int(detection["cy"])
            cv2.drawContours(result, [contour], -1, (0, 255, 0), 2)
            cv2.circle(result, (cx, cy), 5, (0, 255, 255), -1)
            detections.append(
                build_object_payload(
                    0,
                    cx,
                    cy,
                    H,
                    K,
                    dist,
                    object_radius_cm,
                    config,
                    estimated_camera_height_cm,
                    (camera_center_x_cm, camera_center_y_cm),
                )
            )

        # Continuous mode keeps re-detecting objects, then uses the previous
        # estimated positions only to preserve object identities over time.
        assigned_detections = assign_ids(detections, tracks, max_objects)
        publish_and_draw_detections(result, assigned_detections, client, config, save_positions)

        cv2.imshow("Resultado (AR)", result)
        cv2.imshow("Mascara", mask)

        if cv2.waitKey(1) & 0xFF in PREVIEW_EXIT_KEYS:
            break

    if client is not None:
        client.loop_stop()
        client.disconnect()
    cap.release()
    cv2.destroyAllWindows()


def run_tracking(save_positions: bool = True) -> None:
    """Run the fixed final-delivery mode: automatic first-frame detection with KCF."""
    run_initialized_tracking("automatic", save_positions)


def run_tracking_background(save_positions: bool = True) -> None:
    """Run first-frame background detection followed by standard tracker updates."""
    run_initialized_tracking("background", save_positions)


if __name__ == "__main__":
    run_tracking()
