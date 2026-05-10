from __future__ import annotations

from pathlib import Path

import cv2

from app_state import load_config, save_calibration_info


def capture_calibration_images() -> None:
    config = load_config()
    cap = cv2.VideoCapture(config["camera_index"])

    if not cap.isOpened():
        print("No se pudo abrir la camara")
        return

    pattern_size = (7, 7)
    save_dir = Path("data/calibration_images")
    save_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(save_dir.glob("calib_*.png"))
    img_id = len(existing)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se puede leer la camara")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, pattern_size, None)

        frame_draw = frame.copy()

        if found:
            cv2.drawChessboardCorners(frame_draw, pattern_size, corners, found)
            cv2.putText(
                frame_draw,
                "Patron detectado - pulsa s para guardar",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
        else:
            cv2.putText(
                frame_draw,
                "Patron NO detectado",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        cv2.imshow("Captura calibracion", frame_draw)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s") and found:
            filename = save_dir / f"calib_{img_id:02d}.png"
            cv2.imwrite(str(filename), frame)
            print(f"Imagen guardada: {filename}")
            img_id += 1

        if key in [27, ord("q")]:
            break

    cap.release()
    cv2.destroyAllWindows()
    save_calibration_info({"calibration_images": img_id, "camera_index": config["camera_index"]})


if __name__ == "__main__":
    capture_calibration_images()
