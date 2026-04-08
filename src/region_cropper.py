"""
Region Cropper Module
Crops specific regions from dose report images for per-parameter OCR.
"""

import cv2
import json
import numpy as np
from pathlib import Path


# Default parameter names matching the 7 dosimetric parameters
PARAMETER_NAMES = [
    'total_dap',
    'exposure_images',
    'fluoro_time',
    'air_kerma',
    'dose_entree_peau_max',
    'total_dose',
    'frequence_acquisition',
]


class RegionCropper:
    """
    Crop individual parameter regions from a full dose report image.

    Crop coordinates can be specified as absolute pixel values
    (x, y, width, height) or as percentage-based values
    (x_pct, y_pct, width_pct, height_pct in the range 0–1).

    Configuration is read from config.json under the key "crop_regions".
    If no valid region is defined for a parameter (all zeros or missing),
    crop_parameter_regions() returns an empty dict so callers can fall back
    to full-image OCR.
    """

    def __init__(self, config_path='config.json'):
        """
        Initialize with optional path to config.json.

        Args:
            config_path (str): Path to the project config file.
        """
        self.config_path = Path(config_path)
        self.crop_regions = {}
        self._load_config()

    # ------------------------------------------------------------------
    # Configuration loading
    # ------------------------------------------------------------------

    def _load_config(self):
        """Load crop region definitions from config.json."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            self.crop_regions = cfg.get('crop_regions', {})
        except FileNotFoundError:
            self.crop_regions = {}
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠ Could not load crop regions from config: {e}")
            self.crop_regions = {}

    def set_crop_region(self, parameter_name, x, y, width, height,
                        use_percentage=False):
        """
        Programmatically set a crop region for a parameter.

        Args:
            parameter_name (str): One of the PARAMETER_NAMES.
            x (float): Left edge (pixels or fraction 0–1).
            y (float): Top edge (pixels or fraction 0–1).
            width (float): Region width (pixels or fraction 0–1).
            height (float): Region height (pixels or fraction 0–1).
            use_percentage (bool): True → values are fractions of image size.
        """
        self.crop_regions[parameter_name] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'use_percentage': use_percentage,
        }

    # ------------------------------------------------------------------
    # Core cropping logic
    # ------------------------------------------------------------------

    def _is_valid_region(self, region):
        """Return True if the region has non-zero dimensions."""
        w = region.get('width', 0)
        h = region.get('height', 0)
        return w > 0 and h > 0

    def _compute_pixel_coords(self, region, img_height, img_width):
        """
        Convert a region definition to integer pixel (x, y, w, h).

        Supports both absolute pixels and percentage-based coordinates.
        """
        use_pct = region.get('use_percentage', False)
        x = region.get('x', 0)
        y = region.get('y', 0)
        w = region.get('width', 0)
        h = region.get('height', 0)

        # Also support x_pct / y_pct / width_pct / height_pct keys
        if 'x_pct' in region or 'width_pct' in region:
            use_pct = True
            x = region.get('x_pct', x)
            y = region.get('y_pct', y)
            w = region.get('width_pct', w)
            h = region.get('height_pct', h)

        if use_pct:
            x = int(x * img_width)
            y = int(y * img_height)
            w = int(w * img_width)
            h = int(h * img_height)
        else:
            x, y, w, h = int(x), int(y), int(w), int(h)

        # Clamp position to image bounds, adjusting size to maintain intent
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)

        x_clamped = max(0, min(x, img_width - 1))
        y_clamped = max(0, min(y, img_height - 1))

        # Shrink width/height by the amount the origin was moved inward
        w_adjusted = w - (x_clamped - x)
        h_adjusted = h - (y_clamped - y)

        w_clamped = max(1, min(w_adjusted, img_width - x_clamped))
        h_clamped = max(1, min(h_adjusted, img_height - y_clamped))

        return x_clamped, y_clamped, w_clamped, h_clamped

    def crop_parameter_regions(self, image):
        """
        Crop each configured parameter region from the full image.

        Args:
            image: numpy array (BGR) representing the full dose report image.

        Returns:
            dict: {parameter_name: cropped_sub_image} for every parameter that
                  has a valid (non-zero) region defined.  Returns an empty dict
                  when no valid regions are configured (triggers full-image
                  fallback in the caller).
        """
        if image is None or image.size == 0:
            return {}

        img_height, img_width = image.shape[:2]
        crops = {}

        for param_name, region in self.crop_regions.items():
            if not self._is_valid_region(region):
                continue
            x, y, w, h = self._compute_pixel_coords(region, img_height, img_width)
            crops[param_name] = image[y:y + h, x:x + w].copy()

        return crops
