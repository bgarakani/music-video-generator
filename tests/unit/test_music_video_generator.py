#!/usr/bin/env python3
"""Unit tests for MusicVideoGenerator class."""
import os
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

    @pytest.mark.skipif(not os.path.exists("test-assets/test_audio.wav"),
                        reason="Test audio not available")
    def test_analyze_audio(self, tmp_path):
        """Test audio analysis with librosa."""
        film_path = tmp_path / "test.mp4"
        film_path.touch()
        library = FilmLibrary(str(film_path), clips_library_dir=str(tmp_path / "lib"))

        gen = MusicVideoGenerator(library, "test-assets/test_audio.wav")
        result = gen.analyze_audio()

        assert 'duration' in result
        assert 'bpm' in result
        assert 'beats' in result
        assert 'tempo_confidence' in result
        assert result['duration'] > 0
        assert len(result['beats']) > 0

    def test_safe_float_conversion(self, tmp_path):
        """Test safe float conversion in generator."""
        film_path = tmp_path / "test.mp4"
        film_path.touch()
        library = FilmLibrary(str(film_path), clips_library_dir=str(tmp_path / "lib"))

        song_path = tmp_path / "test.mp3"
        song_path.touch()
        gen = MusicVideoGenerator(library, str(song_path))

        import numpy as np
        assert gen.safe_float(3.14) == 3.14
        assert gen.safe_float(np.float64(3.14)) == 3.14
        assert gen.safe_float("invalid") == 0.0

    def test_validate_insufficient_scenes(self, tmp_path, capsys):
        """Test validation warning when scenes < beats."""
        film_path = tmp_path / "test.mp4"
        film_path.touch()

        library = FilmLibrary(str(film_path), clips_library_dir=str(tmp_path / "lib"))
        library.scenes = [{'id': i, 'start': i, 'end': i+1, 'duration': 1}
                          for i in range(10)]  # Only 10 scenes

        song_path = tmp_path / "test.mp3"
        song_path.touch()

        gen = MusicVideoGenerator(library, str(song_path))
        gen.beat_times = [i * 0.5 for i in range(100)]  # 100 beats

        result = gen.validate_scene_beat_ratio()

        captured = capsys.readouterr()
        assert "⚠️  WARNING" in captured.out
        assert "10" in captured.out  # scene count
        assert "100" in captured.out  # beat count
        assert result is True  # Should allow continuing

    def test_validate_sufficient_scenes(self, tmp_path):
        """Test validation passes when scenes >= beats."""
        film_path = tmp_path / "test.mp4"
        film_path.touch()

        library = FilmLibrary(str(film_path), clips_library_dir=str(tmp_path / "lib"))
        library.scenes = [{'id': i, 'start': i, 'end': i+1, 'duration': 1}
                          for i in range(100)]  # 100 scenes

        song_path = tmp_path / "test.mp3"
        song_path.touch()

        gen = MusicVideoGenerator(library, str(song_path))
        gen.beat_times = [i * 0.5 for i in range(50)]  # 50 beats

        result = gen.validate_scene_beat_ratio()
        assert result is True
