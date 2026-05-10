from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app_state import save_calibration_info


def compute_mean_reprojection_error(
    objpoints: list[np.ndarray],
    imgpoints: list[np.ndarray],
    rvecs: list[np.ndarray],
    tvecs: list[np.ndarray],
    camera_matrix: np.ndarray,
    dist_coeffs: np.ndarray,
) -> float:
    total_error = 0.0
    total_views = 0

    for object_points, image_points, rvec, tvec in zip(objpoints, imgpoints, rvecs, tvecs):
        projected_points, _ = cv2.projectPoints(object_points, rvec, tvec, camera_matrix, dist_coeffs)
        error = cv2.norm(image_points, projected_points, cv2.NORM_L2) / len(projected_points)
        total_error += float(error)
        total_views += 1

    if total_views == 0:
        return 0.0

    return total_error / total_views


def calibrate_camera() -> None:
    pattern_size = (7, 7)
    objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0 : pattern_size[0], 0 : pattern_size[1]].T.reshape(-1, 2)

    objpoints = []
    imgpoints = []
    images = sorted(Path("data/calibration_images").glob("*.png"))

    if not images:
        print("No hay imagenes de calibracion en data/calibration_images")
        return

    image_size = None
    valid_images = 0

    for path in images:
        img = cv2.imread(str(path))
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, pattern_size, None)

        if found:
            objpoints.append(objp)
            imgpoints.append(corners)
            image_size = gray.shape[::-1]
            valid_images += 1

            cv2.drawChessboardCorners(img, pattern_size, corners, found)
            cv2.imshow("Corners", img)
            cv2.waitKey(200)

    cv2.destroyAllWindows()

    if not objpoints or image_size is None:
        print("No se detectaron esquinas validas para calibrar")
        return

    ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image_size, None, None)
    mean_reprojection_error = compute_mean_reprojection_error(
        objpoints,
        imgpoints,
        rvecs,
        tvecs,
        K,
        dist,
    )

    np.save("calibration/K.npy", K)
    np.save("calibration/dist.npy", dist)

    save_calibration_info(
        {
            "camera_calibration_rms": float(ret),
            "camera_calibration_mean_reprojection_error_px": float(mean_reprojection_error),
            "valid_calibration_images": valid_images,
            "intrinsics_path": "calibration/K.npy",
            "distortion_path": "calibration/dist.npy",
        }
    )

    print("Matriz de camara K:\n", K)
    print("Distorsion:\n", dist)
    print(f"Error medio de reproyeccion: {mean_reprojection_error:.4f} px")
    print(f"Calibracion completada con {valid_images} imagenes validas.")


if __name__ == "__main__":
    calibrate_camera()
