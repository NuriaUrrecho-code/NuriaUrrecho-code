from __future__ import annotations

import cv2
import numpy as np

from app_state import load_config, load_selected_points, save_calibration_info


def compute_planar_reprojection_error(
    source_points: np.ndarray,
    target_points: np.ndarray,
    homography: np.ndarray,
) -> float:
    projected_points = cv2.perspectiveTransform(source_points.reshape(-1, 1, 2), homography)
    error = cv2.norm(target_points.reshape(-1, 1, 2), projected_points, cv2.NORM_L2) / len(source_points)
    return float(error)


def compute_homography() -> None:
    config = load_config()
    selected_points = load_selected_points()

    if len(selected_points) != 4:
        print("No hay 4 puntos guardados. Ejecuta primero calibration/select_points.py")
        return

    img_pts = np.array(selected_points, dtype=np.float32)
    world_pts = np.array(config["world_points_cm"], dtype=np.float32)

    if world_pts.shape != (4, 2):
        print("La configuracion world_points_cm debe contener 4 puntos [x, y]")
        return

    H, mask = cv2.findHomography(img_pts, world_pts, cv2.RANSAC, 3.0)
    if H is None:
        print("No se pudo calcular la homografia")
        return

    image_to_world_error = compute_planar_reprojection_error(img_pts, world_pts, H)
    H_inv = np.linalg.inv(H)
    world_to_image_error = compute_planar_reprojection_error(world_pts, img_pts, H_inv)
    inlier_mask = None if mask is None else [bool(value[0]) for value in mask.tolist()]

    np.save("calibration/H.npy", H)
    save_calibration_info(
        {
            "homography_path": "calibration/H.npy",
            "image_points": selected_points,
            "world_points_cm": config["world_points_cm"],
            "homography_method": "RANSAC",
            "homography_ransac_threshold_px": 3.0,
            "homography_inliers": inlier_mask,
            "homography_reprojection_error_world_units": image_to_world_error,
            "homography_inverse_reprojection_error_px": world_to_image_error,
        }
    )

    print("Homografia:\n", H)
    print(f"Error imagen->mundo: {image_to_world_error:.4f} cm")
    print(f"Error mundo->imagen: {world_to_image_error:.4f} px")


if __name__ == "__main__":
    compute_homography()
