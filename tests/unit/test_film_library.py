#!/usr/bin/env python3
"""Unit tests for FilmLibrary class."""
import pytest
from pathlib import Path
from music_video_generator.film_library import FilmLibrary


class TestFilmLibrary:
    """Test FilmLibrary class."""

    def test_init_with_valid_film(self, tmp_path):
        """Test FilmLibrary initialization with valid film path."""
        # Create a mock film path
        film_path = tmp_path / "test_movie.mp4"
        film_path.touch()

        library = FilmLibrary(str(film_path), threshold=30.0)

        assert library.film_path == str(film_path)
        assert library.threshold == 30.0
        assert library.min_scene_len == 1.0
        assert library.film_name == "test_movie"

    def test_init_with_invalid_film(self):
        """Test FilmLibrary initialization with non-existent film."""
        with pytest.raises(FileNotFoundError):
            FilmLibrary("nonexistent.mp4")

    def test_safe_float_conversion(self, tmp_path):
        """Test safe float conversion utility."""
        film_path = tmp_path / "test.mp4"
        film_path.touch()
        library = FilmLibrary(str(film_path))

        import numpy as np
        assert library.safe_float(3.14) == 3.14
        assert library.safe_float(np.float64(3.14)) == 3.14
        assert library.safe_float("invalid") == 0.0
        assert library.safe_float(None) == 0.0

    def test_safe_int_conversion(self, tmp_path):
        """Test safe int conversion utility."""
        film_path = tmp_path / "test.mp4"
        film_path.touch()
        library = FilmLibrary(str(film_path))

        import numpy as np
        assert library.safe_int(42) == 42
        assert library.safe_int(np.int64(42)) == 42
        assert library.safe_int("invalid") == 0
        assert library.safe_int(None) == 0
