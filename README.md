# Music Video Generator

An intelligent Music Video Generation & Archival Remix Engine that creates artistic video remixes by synchronizing archival film footage with music through AI-driven scene detection, audio analysis, and video manipulation.

## Features

- **Two-Phase Architecture**: Separate film preparation (one-time) from video generation (fast, repeatable)
- **Intelligent Caching**: Film analysis cached and reused across multiple music tracks
- **Four Scene Selection Strategies**:
  - **Progressive**: Evenly distributed chronological journey through the film
  - **Random**: Pure random selection with repetition for energetic cuts
  - **Forward-only**: Sequential progression, never backtracks
  - **No-repeat**: Random selection without repetition
- **Beat Synchronization**: Flexible beat-skip parameter (1=every beat, 2=every other beat, etc.)
- **Rich Metadata**: Comprehensive HTML reports with scene analysis, thumbnails, and playback
- **Production Ready**: Robust error handling, type-safe numpy conversions, extensive testing

## Installation

### Dependencies

```bash
pip install librosa moviepy scenedetect[opencv] numpy matplotlib opencv-python scipy
```

**FFmpeg is required** and must be installed separately:
```bash
# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Verify Installation

```bash
python test_setup.py
```

## Quick Start

### 1. Prepare Film Library (One-Time Per Film)

Analyze a film and build a reusable scene library:

```bash
python music_video_generator.py --prepare --film movie.mp4
```

This creates a scene library at `clips_library/{film_name}/` containing:
- Scene detection metadata
- Individual scene clips
- Thumbnail images
- Scene analysis (color, brightness, pace)

**Optional parameters:**
- `--threshold 30.0` - Scene detection sensitivity (10-50, default: 30)
- `--min-scene-len 1.0` - Minimum scene duration in seconds

### 2. Generate Music Video

Create a music video using the prepared film library:

```bash
# Basic usage (progressive strategy, every beat)
python music_video_generator.py --film movie.mp4 --song track.mp3

# Fewer cuts (every 2nd beat)
python music_video_generator.py --film movie.mp4 --song track.mp3 --beat-skip 2

# Random strategy with every 4th beat
python music_video_generator.py --film movie.mp4 --song track.mp3 --strategy random --beat-skip 4

# Forward-only progression
python music_video_generator.py --film movie.mp4 --song track.mp3 --strategy forward_only
```

**Strategy Details:**

| Strategy | Description | Best For |
|----------|-------------|----------|
| `progressive` | Evenly distributed journey through entire film | Narrative films, documentaries |
| `random` | Pure random selection with repetition | High-energy music, abstract visuals |
| `forward_only` | Sequential, never backtracks | Maintaining chronological flow |
| `no_repeat` | Random without repetition | Maximizing visual variety |

**Output:** `output/{film_name}_{song_name}_{timestamp}.mp4`

## Advanced Usage

### Custom Output Location

```bash
python music_video_generator.py --film movie.mp4 --song track.mp3 \
  --output my_remix.mp4
```

### Force Scene Re-analysis

```bash
python music_video_generator.py --prepare --film movie.mp4 --force
```

### Custom Cache Directory

```bash
python music_video_generator.py --film movie.mp4 --song track.mp3 \
  --clips-dir /path/to/clips_library
```

## Architecture

### Two-Phase Design

**Phase 1: Film Preparation** (slow, one-time per film)
- Scene detection with PySceneDetect
- Clip extraction
- Thumbnail generation
- Scene analysis (color, brightness, pace)
- Metadata persistence

**Phase 2: Video Generation** (fast, repeatable)
- Audio analysis with librosa (beat detection, tempo)
- Scene-beat ratio validation
- Strategy-based scene selection
- Video assembly with MoviePy
- FFmpeg final rendering

### Project Structure

```
music_video_project/
├── music_video_generator.py        # Main CLI entry point
├── music_video_generator/          # Core package
│   ├── film_library.py             # Film analysis & caching
│   └── music_video_generator.py    # Video generation
├── clips_library/                  # Cached film libraries
│   └── {film_name}/
│       ├── metadata.json           # Scene metadata
│       ├── clips/                  # Individual scene clips
│       └── thumbnails/             # Scene thumbnails
├── output/                         # Generated music videos
├── tests/                          # Comprehensive test suite
│   ├── unit/
│   ├── integration/
│   └── performance/
└── attic/                          # Legacy generators
```

## Testing

### Run All Tests

```bash
python run_tests.py
```

### Run Specific Test Categories

```bash
pytest tests/unit/                 # Unit tests only
pytest tests/integration/          # Integration tests
pytest tests/performance/          # Performance benchmarks
```

### Run Simple Working Test

```bash
python simple_working_test.py
```

Verifies:
- Library imports
- Librosa audio analysis
- Scene detection
- FFmpeg availability

## Legacy Generators

Previous generator implementations have been moved to `attic/` and are kept for reference:

- `ultraRobustArchivalTool.py` - Original production tool
- `premiere_style_archival_engine.py` - Premiere-style interface
- `progressive_sampling_generator.py` - Chronological sampling
- `robust_music_video_generator.py` - Numpy-safe implementation
- `forward_only_generator.py` - Forward-only progression
- And many more experimental versions

**Use the new `music_video_generator.py` for all new projects.**

## Technical Details

### Scene Detection

Uses PySceneDetect's ContentDetector:
- **Threshold**: 10-50 (default: 30)
  - Lower = more sensitive (more scenes)
  - Higher = less sensitive (fewer scenes)
- **Min Scene Length**: Filters out very short scenes

### Audio Analysis

Uses librosa for:
- Beat detection with `librosa.beat.beat_track()`
- Tempo estimation
- Onset strength analysis

### Type Safety

All generators use `safe_float()` and `safe_int()` helpers to handle numpy type conversions safely, preventing JSON serialization errors.

### Video Processing

- Scene extraction: MoviePy VideoFileClip
- Clip assembly: MoviePy concatenate_videoclips
- Final render: FFmpeg direct rendering (more reliable than MoviePy)

## Troubleshooting

### MoviePy Audio Crashes

**Symptom**: Segmentation fault or audio codec errors during final render
**Solution**: The tool uses FFmpeg direct rendering to avoid this issue

### Scene Detection Memory Issues

**Symptom**: Out of memory with long videos
**Solution**: Increase `--min-scene-len` parameter to reduce scene count

### Librosa Loading Failures

**Symptom**: `audioread` or `soundfile` errors
**Solution**: Ensure FFmpeg is properly installed and in PATH

### No Scenes Detected

**Symptom**: "No scenes detected" error
**Solution**: Lower the `--threshold` parameter (try 20.0 or 15.0)

## Performance

- **Audio analysis**: < 10 seconds for 3-minute track
- **Scene detection**: < 60 seconds for 10-minute video
- **Video generation**: ~1-2 minutes for 3-minute music video (after film prepared)

## Contributing

### Development Setup

```bash
# Install dev dependencies
pip install pytest pytest-cov pre-commit

# Install pre-commit hooks
pre-commit install
```

### Pre-commit Checks

Automatically runs before each commit:
- Black formatting
- Flake8 linting
- Bandit security scan
- Numpy safety validation
- Unit tests

### Adding New Features

1. Write tests first (TDD approach)
2. Implement feature
3. Run test suite: `python run_tests.py`
4. Verify numpy safety: `python scripts/check_numpy_safety.py`
5. Update documentation

## License

[Add your license here]

## Credits

Built with:
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) - Scene detection
- [librosa](https://librosa.org/) - Audio analysis
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing
- [FFmpeg](https://ffmpeg.org/) - Video encoding
