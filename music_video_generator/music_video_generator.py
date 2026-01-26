#!/usr/bin/env python3
"""MusicVideoGenerator class for creating music videos from film libraries."""
import os
from pathlib import Path
from datetime import datetime


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
