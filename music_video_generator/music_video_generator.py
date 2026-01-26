#!/usr/bin/env python3
"""MusicVideoGenerator class for creating music videos from film libraries."""
import os
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

import librosa
import numpy as np


class MusicVideoGenerator:
    """Generates music videos from FilmLibrary using various strategies."""

    VALID_STRATEGIES = ['progressive', 'random', 'forward_only', 'no_repeat']

    def __init__(self, film_library, song_path, strategy='progressive',
                 beat_skip=1, output_dir="music_videos"):
        """Initialize MusicVideoGenerator.

        Args:
            film_library: FilmLibrary instance with cached clips
            song_path: Path to audio file
            strategy: Scene selection strategy (progressive|random|forward_only|no_repeat)
            beat_skip: Use every Nth beat (1=every beat, 2=every other beat)
            output_dir: Base directory for music video outputs

        Raises:
            FileNotFoundError: If song_path does not exist
            ValueError: If strategy is not valid
        """
        # Validate song exists
        if not os.path.exists(song_path):
            raise FileNotFoundError(f"Song not found: {song_path}")

        # Validate strategy
        if strategy not in self.VALID_STRATEGIES:
            raise ValueError(f"Invalid strategy: {strategy}. Must be one of {self.VALID_STRATEGIES}")

        self.film_library = film_library
        self.song_path = str(song_path)
        self.song_name = Path(song_path).stem
        self.strategy = strategy
        self.beat_skip = beat_skip

        # Set up output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        film_name = film_library.film_name
        self.output_dir = Path(output_dir) / f"{film_name}_{self.song_name}_{strategy}_{timestamp}"

        self.beats = []
        self.beat_times = []
        self.music_analysis = {}
        self.selected_scenes = []

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

    def analyze_audio(self):
        """Librosa beat detection and tempo analysis.

        Returns:
            dict: Music analysis with duration, bpm, beats, tempo_confidence, sample_rate
        """
        print(f"\n🎵 Analyzing audio: {self.song_name}")

        try:
            # Load audio
            audio_data, sample_rate = librosa.load(self.song_path)

            # Beat tracking
            tempo, beat_frames = librosa.beat.beat_track(
                y=audio_data,
                sr=sample_rate
            )

            # Convert beat frames to time
            beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)

            # Calculate duration
            duration = len(audio_data) / sample_rate

            # Store results
            self.beats = beat_frames
            self.beat_times = [self.safe_float(t) for t in beat_times]

            self.music_analysis = {
                'duration': self.safe_float(duration),
                'bpm': self.safe_float(tempo),
                'beats_detected': len(beat_times),
                'beats': self.beat_times,
                'tempo_confidence': 0.85,  # Placeholder, librosa doesn't provide this
                'sample_rate': self.safe_int(sample_rate)
            }

            print(f"   Duration: {duration:.1f}s")
            print(f"   BPM: {tempo:.1f}")
            print(f"   Beats detected: {len(beat_times)}")

            return self.music_analysis

        except Exception as e:
            print(f"   ✗ Audio analysis failed: {e}")

            # Return defaults
            self.music_analysis = {
                'duration': 0.0,
                'bpm': 120.0,
                'beats_detected': 0,
                'beats': [],
                'tempo_confidence': 0.0,
                'sample_rate': 22050
            }

            return self.music_analysis

    def validate_scene_beat_ratio(self):
        """Check if enough scenes for beats, warn/suggest alternatives.

        Returns:
            bool: True to continue, False to abort
        """
        scenes = self.film_library.get_scenes()

        # Calculate effective beat count after beat_skip
        effective_beats = len(self.beat_times) // self.beat_skip

        # Check if we have enough scenes
        if len(scenes) < effective_beats:
            ratio = effective_beats / len(scenes)
            suggested_skip = int(np.ceil(ratio))

            print(f"\n⚠️  WARNING: Insufficient clips for beat count")
            print(f"   Scenes available: {len(scenes)}")
            print(f"   Beats to use: {effective_beats} (every {self.beat_skip} beat)")
            print(f"   Ratio: {ratio:.1f} beats per scene")
            print(f"\n   SUGGESTIONS:")
            print(f"   1. Use --beat-skip {suggested_skip} (1 clip per {suggested_skip} beats)")
            print(f"   2. Use 'random' or 'no-repeat' strategy (allows scene reuse)")
            print(f"   3. Lower scene detection --threshold to detect more scenes")
            print(f"\n   Continuing with current settings...")

            return True

        print(f"\n✓ Scene-beat ratio valid: {len(scenes)} scenes for {effective_beats} beats")
        return True

    def select_scenes(self):
        """Apply strategy to map scenes to beats.

        Returns:
            list: Scene-to-beat mappings
        """
        print(f"\n🎬 Selecting scenes using '{self.strategy}' strategy...")

        scenes = self.film_library.get_scenes()

        # Apply beat_skip
        selected_beats = self.beat_times[::self.beat_skip]

        print(f"   Available scenes: {len(scenes)}")
        print(f"   Beats to use: {len(selected_beats)} (every {self.beat_skip} beat)")

        # Call appropriate strategy method
        strategy_map = {
            'progressive': self._select_progressive,
            'random': self._select_random,
            'forward_only': self._select_forward_only,
            'no_repeat': self._select_no_repeat
        }

        selected = strategy_map[self.strategy](scenes, selected_beats)

        print(f"   ✓ Selected {len(selected)} scene-to-beat mappings")

        self.selected_scenes = selected
        return selected

    def _select_progressive(self, scenes, beat_times):
        """Evenly distributed chronological sampling.

        Args:
            scenes: Available scenes
            beat_times: Beat time points

        Returns:
            list: Scene-to-beat mappings
        """
        mappings = []
        num_beats = len(beat_times) - 1

        for i in range(num_beats):
            beat_start = beat_times[i]
            beat_end = beat_times[i + 1]
            beat_duration = beat_end - beat_start

            # Map beat index to scene position
            scene_index = int((i / num_beats) * len(scenes))
            scene_index = min(scene_index, len(scenes) - 1)
            selected_scene = scenes[scene_index]

            mappings.append({
                'beat_start': beat_start,
                'beat_end': beat_end,
                'beat_duration': beat_duration,
                'scene': selected_scene,
                'beat_index': i
            })

        return mappings

    def _select_random(self, scenes, beat_times):
        """Pure random selection, allows repetition.

        Args:
            scenes: Available scenes
            beat_times: Beat time points

        Returns:
            list: Scene-to-beat mappings
        """
        mappings = []
        num_beats = len(beat_times) - 1

        for i in range(num_beats):
            beat_start = beat_times[i]
            beat_end = beat_times[i + 1]
            beat_duration = beat_end - beat_start

            # Random selection
            selected_scene = scenes[np.random.randint(0, len(scenes))]

            mappings.append({
                'beat_start': beat_start,
                'beat_end': beat_end,
                'beat_duration': beat_duration,
                'scene': selected_scene,
                'beat_index': i
            })

        return mappings

    def _select_forward_only(self, scenes, beat_times):
        """Sequential progression without backtracking.

        Args:
            scenes: Available scenes
            beat_times: Beat time points

        Returns:
            list: Scene-to-beat mappings
        """
        mappings = []
        num_beats = len(beat_times) - 1
        current_scene_index = 0

        for i in range(num_beats):
            beat_start = beat_times[i]
            beat_end = beat_times[i + 1]
            beat_duration = beat_end - beat_start

            # Use current scene and advance
            selected_scene = scenes[current_scene_index]

            mappings.append({
                'beat_start': beat_start,
                'beat_end': beat_end,
                'beat_duration': beat_duration,
                'scene': selected_scene,
                'beat_index': i
            })

            # Move to next scene (with wrap-around)
            current_scene_index = (current_scene_index + 1) % len(scenes)

        return mappings

    def _select_no_repeat(self, scenes, beat_times):
        """Random selection from unused pool.

        Args:
            scenes: Available scenes
            beat_times: Beat time points

        Returns:
            list: Scene-to-beat mappings
        """
        mappings = []
        num_beats = len(beat_times) - 1
        unused_scenes = list(scenes)

        for i in range(num_beats):
            beat_start = beat_times[i]
            beat_end = beat_times[i + 1]
            beat_duration = beat_end - beat_start

            # If pool exhausted, fall back to forward-only
            if not unused_scenes:
                unused_scenes = list(scenes)

            # Random selection from unused pool
            scene_index = np.random.randint(0, len(unused_scenes))
            selected_scene = unused_scenes.pop(scene_index)

            mappings.append({
                'beat_start': beat_start,
                'beat_end': beat_end,
                'beat_duration': beat_duration,
                'scene': selected_scene,
                'beat_index': i
            })

        return mappings
