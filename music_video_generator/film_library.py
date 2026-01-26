#!/usr/bin/env python3
"""FilmLibrary class for scene detection and clip management."""
import os
import json
from pathlib import Path
from datetime import datetime
import warnings
import gc
# Suppress specific PySceneDetect deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="scenedetect")

from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.editor import VideoFileClip
import cv2
import numpy as np


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

    def detect_scenes(self):
        """Run PySceneDetect scene detection.

        Returns:
            list: Scene metadata dictionaries
        """
        print(f"\n🎬 Detecting scenes in {self.film_name}...")
        print(f"   Threshold: {self.threshold}")
        print(f"   Min scene length: {self.min_scene_len}s")

        video_manager = None
        try:
            # Set up scene detection
            video_manager = VideoManager([self.film_path])
            scene_manager = SceneManager()
            scene_manager.add_detector(
                ContentDetector(threshold=self.threshold)
            )

            # Detect scenes
            video_manager.set_duration()
            video_manager.start()
            scene_manager.detect_scenes(frame_source=video_manager)
            scene_list = scene_manager.get_scene_list()

            print(f"   Found {len(scene_list)} raw scenes")

            # Process scenes
            self.scenes = []
            filtered_scene_id = 0
            for i, scene in enumerate(scene_list):
                start_time = self.safe_float(scene[0].get_seconds())
                end_time = self.safe_float(scene[1].get_seconds())
                duration = end_time - start_time

                # Filter by minimum duration
                if duration < self.min_scene_len:
                    continue

                scene_info = {
                    'id': filtered_scene_id,  # Use sequential ID for kept scenes
                    'start': start_time,
                    'end': end_time,
                    'duration': duration,
                    'clip_filename': f"scene_{filtered_scene_id:04d}.mp4",
                    'thumbnail_filename': f"thumb_{filtered_scene_id:04d}.jpg"
                }

                self.scenes.append(scene_info)
                filtered_scene_id += 1

                # Progress reporting
                if (i + 1) % 20 == 0:
                    print(f"   Analyzed {i + 1}/{len(scene_list)} raw scenes...")

            print(f"   ✓ Detected {len(self.scenes)} scenes (filtered by min_scene_len)")

            return self.scenes

        except Exception as e:
            print(f"   ✗ Scene detection failed: {e}")
            return []
        finally:
            if video_manager is not None:
                video_manager.release()

    def extract_clips(self, scenes):
        """Extract individual scene clips to clips/ directory.

        Args:
            scenes: List of scene metadata dictionaries (will be modified with 'has_clip' flag)

        Returns:
            int: Count of successfully exported clips
        """
        # Validate input
        if not scenes or not isinstance(scenes, list):
            print("   ✗ No scenes provided for clip extraction")
            return 0

        print(f"\n🎞️  Extracting {len(scenes)} scene clips...")

        # Ensure clips directory exists
        self.clips_dir.mkdir(parents=True, exist_ok=True)

        clips_exported = 0
        clips_failed = []

        video = None
        try:
            # Load video without audio (faster, clips don't need audio)
            video = VideoFileClip(self.film_path, audio=False)
            video_duration = video.duration

            for i, scene in enumerate(scenes):
                # Progress reporting every 20 clips
                if (i + 1) % 20 == 0:
                    print(f"   Extracting clip {i + 1}/{len(scenes)}...")

                try:
                    start_time = scene['start']
                    end_time = min(scene['end'], video_duration)
                    clip_path = self.clips_dir / scene['clip_filename']

                    # Validate bounds
                    if start_time >= video_duration:
                        clips_failed.append(i)
                        continue

                    # Ensure minimum duration
                    if end_time - start_time < 0.1:
                        clips_failed.append(i)
                        continue

                    # Extract clip
                    clip = video.subclip(start_time, end_time)

                    # Export with settings from v20
                    clip.write_videofile(
                        str(clip_path),
                        codec='libx264',
                        audio=False,
                        verbose=False,
                        logger=None,
                        preset='fast',
                        threads=2,
                        fps=15,  # Lower FPS for efficiency
                        write_logfile=False
                    )

                    clip.close()
                    clips_exported += 1

                    # Update scene metadata
                    scene['has_clip'] = True

                except Exception as e:
                    clips_failed.append(i)
                    scene['has_clip'] = False
                    continue

            print(f"   ✓ Exported {clips_exported} clips")
            if clips_failed:
                print(f"   ⚠ Failed to export {len(clips_failed)} clips")

            return clips_exported

        except Exception as e:
            print(f"   ✗ Clip extraction failed: {e}")
            return 0
        finally:
            # Always cleanup resources
            if video is not None:
                video.close()
            gc.collect()

    def generate_thumbnails(self, scenes):
        """Generate thumbnail images for each scene.

        Args:
            scenes: List of scene metadata dictionaries
        """
        # Validate input
        if not scenes or not isinstance(scenes, list):
            print("   ✗ No scenes provided for thumbnail generation")
            return

        print(f"\n🖼️  Generating thumbnails for {len(scenes)} scenes...")

        # Ensure thumbnails directory exists
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)

        try:
            video = VideoFileClip(self.film_path, audio=False)

            for i, scene in enumerate(scenes):
                try:
                    # Get middle frame of scene
                    middle_time = (scene['start'] + scene['end']) / 2
                    frame = video.get_frame(middle_time)

                    # Save thumbnail
                    thumb_path = self.thumbnails_dir / scene['thumbnail_filename']
                    thumb_height = 120
                    aspect_ratio = frame.shape[1] / frame.shape[0]
                    thumb_width = int(thumb_height * aspect_ratio)
                    thumb = cv2.resize(frame, (thumb_width, thumb_height))
                    thumb_bgr = cv2.cvtColor(thumb, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(str(thumb_path), thumb_bgr)

                except Exception as e:
                    print(f"   ⚠ Failed to generate thumbnail for scene {i}: {e}")
                    continue

            video.close()
            print(f"   ✓ Generated {len(scenes)} thumbnails")

        except Exception as e:
            print(f"   ✗ Thumbnail generation failed: {e}")

    def analyze_scenes(self, scenes):
        """Add color, brightness, pace analysis to scene metadata.

        Args:
            scenes: List of scene metadata dictionaries

        Returns:
            list: Scenes with added analysis metadata
        """
        # Validate input
        if not scenes or not isinstance(scenes, list):
            print("   ✗ No scenes provided for analysis")
            return scenes

        print(f"\n🔍 Analyzing {len(scenes)} scenes...")

        try:
            video = VideoFileClip(self.film_path, audio=False)
            video_duration = video.duration
            failed_analyses = 0

            for scene in scenes:
                try:
                    # Get middle frame
                    middle_time = (scene['start'] + scene['end']) / 2
                    frame = video.get_frame(middle_time)

                    # Color analysis
                    avg_color = np.mean(frame, axis=(0, 1))
                    scene['avg_color_rgb'] = avg_color.tolist()
                    scene['avg_color_hex'] = '#{:02x}{:02x}{:02x}'.format(
                        int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
                    )

                    # Brightness analysis
                    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                    scene['avg_brightness'] = float(np.mean(gray))

                    # Pace analysis
                    duration = scene['duration']
                    if duration < 2:
                        scene['pace'] = 'fast'
                    elif duration > 10:
                        scene['pace'] = 'slow'
                    else:
                        scene['pace'] = 'medium'

                    # Position ratio in film
                    scene['position_ratio'] = scene['start'] / video_duration

                except Exception as e:
                    # Set defaults on failure
                    scene['avg_brightness'] = 0.0
                    scene['avg_color_rgb'] = [0.0, 0.0, 0.0]
                    scene['avg_color_hex'] = '#000000'
                    scene['pace'] = 'medium'
                    scene['position_ratio'] = 0.0
                    failed_analyses += 1
                    continue

            video.close()
            print(f"   ✓ Analyzed {len(scenes)} scenes")
            if failed_analyses > 0:
                print(f"   ⚠ Failed to analyze {failed_analyses} scenes")

            return scenes

        except Exception as e:
            print(f"   ✗ Scene analysis failed: {e}")
            return scenes

    def get_scenes(self):
        """Return list of available scenes with metadata.

        Returns:
            list: Scene metadata dictionaries
        """
        return self.scenes
