from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from main_position import (
    correct_planar_position,
    estimate_camera_center_from_pose,
    estimate_camera_height_from_pose,
)


class GeometryTests(unittest.TestCase):
    def test_estimate_camera_height_from_pose_returns_absolute_z(self) -> None:
        rotation = np.eye(3, dtype=np.float64)
        tvec = np.array([[0.0], [0.0], [-50.0]], dtype=np.float64)

        height_cm = estimate_camera_height_from_pose(rotation, tvec)

        self.assertAlmostEqual(height_cm, 50.0)

    def test_correct_planar_position_scales_when_object_is_above_plane(self) -> None:
        config = {"height_correction_mode": "manual_camera_height", "camera_height_cm": 50.0}

        x_corr, y_corr, used_height = correct_planar_position(
            x_cm=20.0,
            y_cm=10.0,
            object_radius_cm=2.5,
            config=config,
            estimated_camera_height_cm=40.0,
            camera_projection_xy_cm=(5.0, 2.0),
        )

        self.assertAlmostEqual(x_corr, 19.25)
        self.assertAlmostEqual(y_corr, 9.6)
        self.assertAlmostEqual(used_height, 50.0)

    def test_correct_planar_position_can_use_pose_estimated_height(self) -> None:
        config = {"height_correction_mode": "pose_estimated_height", "camera_height_cm": 50.0}

        _, _, used_height = correct_planar_position(
            x_cm=20.0,
            y_cm=10.0,
            object_radius_cm=2.5,
            config=config,
            estimated_camera_height_cm=36.5,
            camera_projection_xy_cm=(0.0, 0.0),
        )

        self.assertAlmostEqual(used_height, 36.5)

    def test_estimate_camera_center_from_pose_returns_world_coordinates(self) -> None:
        rotation = np.eye(3, dtype=np.float64)
        tvec = np.array([[-12.0], [-7.0], [-50.0]], dtype=np.float64)

        x_cm, y_cm, z_cm = estimate_camera_center_from_pose(rotation, tvec)

        self.assertAlmostEqual(x_cm, 12.0)
        self.assertAlmostEqual(y_cm, 7.0)
        self.assertAlmostEqual(z_cm, 50.0)


if __name__ == "__main__":
    unittest.main()
