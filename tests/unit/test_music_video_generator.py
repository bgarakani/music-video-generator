#!/usr/bin/env python3
"""Unit tests for MusicVideoGenerator class."""
import pytest
from pathlib import Path
from unittest.mock import Mock
from music_video_generator.music_video_generator import MusicVideoGenerator
from music_video_generator.film_library import FilmLibrary


class TestMusicVideoGenerator:
    """Test MusicVideoGenerator class."""

    def test_init_with_valid_inputs(self, tmp_path):
        """Test MusicVideoGenerator initialization."""
        # Create mock FilmLibrary
        film_path = tmp_path / "test.mp4"
        film_path.touch()

        library = FilmLibrary(str(film_path), clips_library_dir=str(tmp_path / "lib"))
        library.scenes = [{'id': 0, 'start': 0, 'end': 2, 'duration': 2}]

        song_path = tmp_path / "test.mp3"
        song_path.touch()

        gen = MusicVideoGenerator(library, str(song_path), strategy='progressive')

        assert gen.film_library == library
        assert gen.song_path == str(song_path)
        assert gen.strategy == 'progressive'
        assert gen.beat_skip == 1

    def test_init_with_invalid_song(self, tmp_path):
        """Test initialization with non-existent song."""
        film_path = tmp_path / "test.mp4"
        film_path.touch()
        library = FilmLibrary(str(film_path), clips_library_dir=str(tmp_path / "lib"))

        with pytest.raises(FileNotFoundError):
            MusicVideoGenerator(library, "nonexistent.mp3")

    def test_init_with_invalid_strategy(self, tmp_path):
        """Test initialization with invalid strategy."""
        film_path = tmp_path / "test.mp4"
        film_path.touch()
        library = FilmLibrary(str(film_path), clips_library_dir=str(tmp_path / "lib"))

        song_path = tmp_path / "test.mp3"
        song_path.touch()

        with pytest.raises(ValueError):
            MusicVideoGenerator(library, str(song_path), strategy='invalid')
