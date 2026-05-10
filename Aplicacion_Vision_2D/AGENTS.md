# Repository Guidelines

## Project Structure & Module Organization
This repository contains a small Python computer-vision prototype for planar object localization with one camera.

- `main_position.py`: main runtime. Opens the camera, detects the orange object, estimates planar position, overlays AR markers, and publishes position data over MQTT.
- `calibration/`: camera and workspace calibration utilities.
- `calibration/capture_calibration_images.py`: saves chessboard images for calibration.
- `calibration/camera_calibration.py`: computes `K.npy` and `dist.npy`.
- `calibration/select_points.py`: collects 4 image points manually.
- `calibration/homography.py`: computes `H.npy` from image and world points.
- `data/calibration_images/`: saved calibration images.

There is currently no dedicated `tests/` directory.

## Build, Test, and Development Commands
Use Python 3 locally.

- `python3 main_position.py`: run the full detection and MQTT publishing pipeline.
- `python3 calibration/capture_calibration_images.py`: capture chessboard images from camera index `3`.
- `python3 calibration/camera_calibration.py`: generate camera intrinsics and distortion files.
- `python3 calibration/select_points.py`: click 4 planar reference points in the live image.
- `python3 calibration/homography.py`: generate the planar homography used by the main app.

Dependencies are implied by imports: `opencv-python`, `numpy`, and `paho-mqtt`.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation. Keep scripts simple and procedural unless a clear refactor justifies functions or classes.

- Use `snake_case` for variables and functions.
- Use `UPPER_CASE` for constants such as `MQTT_TOPIC` or `CAM_HEIGHT_CM`.
- Keep calibration artifacts in `.npy` files under `calibration/`.
- Prefer short, explicit comments for camera geometry or coordinate transforms.

No formatter or linter is configured in this repository, so keep style changes minimal and consistent with the existing code.

## Testing Guidelines
There is no automated test suite yet. Validate changes by running the relevant script and checking:

- camera opens correctly,
- calibration files load without errors,
- detected object position is stable,
- MQTT payload format stays unchanged.

If tests are added later, place them under `tests/` and name them `test_*.py`.

## Commit & Pull Request Guidelines
This folder is not currently a Git repository, so no commit history is available to infer conventions. Use short, imperative commit messages, for example: `Add homography validation step`.

Pull requests should include:

- a brief summary of the change,
- affected scripts or calibration files,
- manual validation steps,
- screenshots if camera overlay behavior changes.

## Configuration & Safety Notes
Camera index, MQTT broker, topic, object height, and camera height are hard-coded in `main_position.py`. Update them deliberately and document any calibration-dependent changes in the PR or handoff notes.
