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
