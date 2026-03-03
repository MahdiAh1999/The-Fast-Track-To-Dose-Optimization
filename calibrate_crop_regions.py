"""
Crop Region Calibration Utility
================================
Interactive helper that lets you determine the pixel coordinates of each
dosimetric parameter on a sample dose report image, then saves the results
to config.json so the pipeline can use per-region OCR.

Usage
-----
    python calibrate_crop_regions.py <path/to/sample_image>

The script prints usage instructions and, when OpenCV's GUI is available,
opens an interactive window where you can draw rectangles.  In headless
environments (no display) it falls back to a CLI prompt that asks you to
enter coordinates manually.

Output
------
The discovered coordinates are written to the ``crop_regions`` section of
``config.json``.
"""

import sys
import json
import cv2
import numpy as np
from pathlib import Path


# The seven parameters to calibrate (must match config.json / region_cropper.py)
PARAMETERS = [
    'total_dap',
    'exposure_images',
    'fluoro_time',
    'air_kerma',
    'dose_entree_peau_max',
    'total_dose',
    'frequence_acquisition',
]

CONFIG_PATH = Path('config.json')

# Rectangle drawing state
_rect_start = None
_rect_end = None
_drawing = False
_confirmed = False


def _mouse_callback(event, x, y, flags, param):
    global _rect_start, _rect_end, _drawing, _confirmed
    if event == cv2.EVENT_LBUTTONDOWN:
        _rect_start = (x, y)
        _rect_end = (x, y)
        _drawing = True
        _confirmed = False
    elif event == cv2.EVENT_MOUSEMOVE and _drawing:
        _rect_end = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        _rect_end = (x, y)
        _drawing = False


def _interactive_calibration(image, param_name):
    """
    Open an OpenCV window and let the user draw a rectangle.
    Returns (x, y, width, height) in pixel coordinates, or None on skip.
    """
    global _rect_start, _rect_end, _drawing, _confirmed
    _rect_start = None
    _rect_end = None
    _drawing = False
    _confirmed = False

    win = 'Calibration -- draw a rectangle then press ENTER (skip: s, quit: q)'
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, 1200, 800)
    cv2.setMouseCallback(win, _mouse_callback)

    print(f"\n  → Draw a rectangle around: {param_name.upper().replace('_', ' ')}")
    print("    Press ENTER to confirm, 's' to skip, 'q' to quit.")

    base = image.copy()
    while True:
        display = base.copy()
        if _rect_start and _rect_end:
            cv2.rectangle(display, _rect_start, _rect_end, (0, 255, 0), 2)
        cv2.imshow(win, display)
        key = cv2.waitKey(20) & 0xFF
        if key == 13 or key == 10:  # ENTER
            break
        if key == ord('s'):
            cv2.destroyWindow(win)
            return None
        if key == ord('q'):
            cv2.destroyAllWindows()
            sys.exit(0)

    cv2.destroyWindow(win)

    if _rect_start is None or _rect_end is None:
        return None

    x1, y1 = _rect_start
    x2, y2 = _rect_end
    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x2 - x1)
    h = abs(y2 - y1)

    if w == 0 or h == 0:
        print("  ⚠ Zero-size rectangle – skipping.")
        return None

    return x, y, w, h


def _cli_calibration(param_name, img_height, img_width):
    """
    Headless fallback: ask the user to type pixel coordinates.
    Returns (x, y, width, height) or None on skip.
    """
    print(f"\n  → Enter coordinates for: {param_name.upper().replace('_', ' ')}")
    print(f"    Image size: {img_width} x {img_height} (width x height)")
    print("    Press ENTER with no input to skip this parameter.")
    try:
        raw = input("    x y width height (space-separated): ").strip()
        if not raw:
            return None
        parts = raw.split()
        if len(parts) != 4:
            print("  ⚠ Expected 4 numbers – skipping.")
            return None
        x, y, w, h = map(int, parts)
        return x, y, w, h
    except (ValueError, EOFError):
        return None


def _load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def _save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Crop regions saved to {CONFIG_PATH}")


def calibrate(image_path):
    """
    Run the calibration workflow for a given sample image.

    Args:
        image_path (str): Path to the sample dose report image.
    """
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)

    image = cv2.imread(str(img_path))
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        sys.exit(1)

    img_height, img_width = image.shape[:2]
    print(f"\nImage: {img_path.name}  ({img_width} x {img_height} px)")
    print("="*60)

    # Detect if a display is available
    has_display = True
    try:
        cv2.namedWindow('test', cv2.WINDOW_NORMAL)
        cv2.destroyWindow('test')
    except cv2.error:
        has_display = False

    if not has_display:
        print("ℹ No display detected – using CLI mode.")

    crop_regions = {}

    for param in PARAMETERS:
        if has_display:
            result = _interactive_calibration(image, param)
        else:
            result = _cli_calibration(param, img_height, img_width)

        if result is None:
            print(f"  ↩  Skipped {param}")
            crop_regions[param] = {"x": 0, "y": 0, "width": 0, "height": 0}
        else:
            x, y, w, h = result
            crop_regions[param] = {"x": x, "y": y, "width": w, "height": h}
            print(f"  ✓  {param}: x={x}, y={y}, w={w}, h={h}")

    # Merge into existing config
    cfg = _load_config()
    cfg['crop_regions'] = crop_regions
    _save_config(cfg)

    print("\nCalibration complete!")
    print("You can now run main.py – the pipeline will use these crop regions.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python calibrate_crop_regions.py <path/to/sample_image>")
        sys.exit(1)
    calibrate(sys.argv[1])
