from __future__ import annotations

import cv2

from app_state import load_config, save_selected_points


def select_points() -> list[list[int]]:
    config = load_config()
    cap = cv2.VideoCapture(config["camera_index"])
    if not cap.isOpened():
        print("No se pudo abrir la camara")
        return []

    points: list[list[int]] = []

    def click_event(event, x, y, flags, param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append([x, y])
            print(f"Punto {len(points)}: ({x}, {y})")

    cv2.namedWindow("Selecciona puntos")
    cv2.setMouseCallback("Selecciona puntos", click_event)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_draw = frame.copy()
        for point in points:
            cv2.circle(frame_draw, tuple(point), 5, (0, 0, 255), -1)

        cv2.putText(
            frame_draw,
            "Haz clic en 4 puntos del plano. q para salir.",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.imshow("Selecciona puntos", frame_draw)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or len(points) == 4:
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(points) == 4:
        save_selected_points(points)
        print("Puntos guardados en state/selected_points.json")
    else:
        print("Seleccion incompleta. No se han actualizado los puntos.")

    return points


if __name__ == "__main__":
    select_points()
