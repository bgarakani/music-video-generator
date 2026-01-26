#!/usr/bin/env python3
"""FilmLibrary class for scene detection and clip management."""
import os
import json
from pathlib import Path
from datetime import datetime


class FilmLibrary:
    """Manages film scene detection and clip library."""

    def __init__(self, film_path, threshold=30.0, min_scene_len=1.0,
                 force_regenerate=False, clips_library_dir="clips_library"):
        """Initialize FilmLibrary.

        Args:
            film_path: Path to source video file
            threshold: Scene detection sensitivity (10-50 range)
            min_scene_len: Minimum scene duration in seconds
            force_regenerate: Force regeneration even if cache exists
            clips_library_dir: Base directory for clip library storage
        """
        # Validate film exists
        if not os.path.exists(film_path):
            raise FileNotFoundError(f"Film not found: {film_path}")

        self.film_path = str(film_path)
        self.film_name = Path(film_path).stem
        self.threshold = threshold
        self.min_scene_len = min_scene_len
        self.force_regenerate = force_regenerate

        # Set up library directories
        self.library_dir = Path(clips_library_dir) / self.film_name
        self.clips_dir = self.library_dir / "clips"
        self.thumbnails_dir = self.library_dir / "thumbnails"

        self.scenes = []
        self.metadata = {}

    def safe_float(self, value):
        """Safely convert value to Python float.

        Args:
            value: Value to convert (supports numpy types)

        Returns:
            float: Converted value or 0.0 on failure
        """
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def safe_int(self, value):
        """Safely convert value to Python int.

        Args:
            value: Value to convert (supports numpy types)

        Returns:
            int: Converted value or 0 on failure
        """
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _load_metadata(self):
        """Load metadata from JSON file.

        Returns:
            bool: True if successfully loaded
        """
        metadata_path = self.library_dir / "metadata.json"

        if not metadata_path.exists():
            return False

        try:
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            return True
        except (json.JSONDecodeError, IOError):
            return False

    def _check_cache(self):
        """Check if valid cached clips exist with matching parameters.

        Returns:
            bool: True if cache exists and parameters match
        """
        # Try to load metadata (also populates self.metadata)
        if not self._load_metadata():
            return False

        # Check if parameters match
        cached_params = self.metadata.get("scene_detection_params", {})

        if (cached_params.get("threshold") == self.threshold and
            cached_params.get("min_scene_len") == self.min_scene_len):
            return True

        return False

    def _load_from_cache(self):
        """Load scenes and metadata from existing cache.

        Returns:
            bool: True if successfully loaded from cache
        """
        if not self._load_metadata():
            print(f"✗ Failed to load cache: metadata not found or invalid")
            return False

        self.scenes = self.metadata.get("scenes", [])

        # Validate scenes is a list
        if not isinstance(self.scenes, list):
            print(f"✗ Failed to load cache: invalid scenes format")
            self.scenes = []
            return False

        print(f"✓ Loaded {len(self.scenes)} scenes from cache")
        print(f"  Cache location: {self.library_dir}")

        return True

    def get_scenes(self):
        """Return list of available scenes with metadata.

        Returns:
            list: Scene metadata dictionaries
        """
        return self.scenes
