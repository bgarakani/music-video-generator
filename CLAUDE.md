# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Music Video Generation & Archival Remix Engine** project that creates artistic video remixes by synchronizing archival film footage with music. The project uses AI-driven scene detection, audio analysis, and video manipulation to transform cultural heritage materials into new artistic expressions.

## Core Dependencies

Install required libraries with:
```bash
pip install librosa moviepy scenedetect[opencv] numpy matplotlib opencv-python
```

**Note:** FFmpeg must be installed on your system for video processing.

## Quick Start Commands

### Prepare Film Library (one-time per film)
```bash
python music_video_generator.py --prepare --film movie.mp4 --threshold 30.0
```

### Generate Music Video
```bash
# With every beat (default)
python music_video_generator.py --film movie.mp4 --song track.mp3

# With every 2nd beat (fewer cuts)
python music_video_generator.py --film movie.mp4 --song track.mp3 --beat-skip 2

# With random strategy and every 4th beat
python music_video_generator.py --film movie.mp4 --song track.mp3 --strategy random --beat-skip 4
```

## Testing & Development

### Run Complete Test Suite
```bash
python run_tests.py
```
This runs the comprehensive pytest-based test suite including:
- **Unit tests**: Audio processing, scene detection, film library, generators
- **Integration tests**: Full workflow, end-to-end generation
- **Performance benchmarks**: Scene detection, audio analysis timing
- **Code coverage report**: Generated in `htmlcov/index.html`

### Run Specific Test Categories
```bash
# Run only unit tests
python -m pytest tests/unit/ -v

# Run only integration tests
python -m pytest tests/integration/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Generate Test Assets
If test assets are missing or need regeneration:
```bash
# Generate 3-minute audio with varying BPM (120→60→90)
python tests/utils/create_test_audio.py

# Generate 10-minute video with 300+ color transitions
python tests/utils/create_test_video.py
```

## Core Architecture

### Active Tool

**music_video_generator.py** - Unified Music Video Generator v2.0
- Two-phase architecture: FilmLibrary + MusicVideoGenerator
- Intelligent caching with parameter tracking
- Four scene selection strategies: progressive, random, forward_only, no_repeat
- Beat-skip parameter for controlling cut frequency
- CLI interface with comprehensive options

### Legacy Generators (in attic/)

Old generators moved to `attic/` directory:
- ultraRobustArchivalTool.py - Original primary production tool
- ArchivalRemixEngine.py - Original archival remix engine
- progressive_sampling_generator.py - Creates journey through entire movie
- robust_music_video_generator.py - Handles numpy formatting issues
- bulletproof_generator.py - Error-resistant implementation
- forward_only_generator.py - Forward-only progression through scenes

### Key Processing Steps

1. **Scene Detection**: Uses PySceneDetect with ContentDetector to identify scene boundaries
2. **Audio Analysis**: Uses librosa for beat detection and tempo analysis  
3. **Video Synchronization**: Maps video scenes to musical beats/timing
4. **Output Generation**: Creates remixed videos using MoviePy

### Data Flow

```
Film Input → Scene Detection → Scene Analysis
Audio Input → Beat Detection → Tempo Analysis
    ↓                           ↓
Scene Metadata ←→ Beat Synchronization → Video Assembly → Final Output
```

## Directory Structure

- `films/` - Source video files (movies, archival footage)
- `music/` - Audio files for synchronization
- `archival_output/` - Generated output with timestamped directories
- `experiments/` - Experimental combinations (e.g., SpongBob + Eric B & Rakim)
- `input/` - Input staging area

### V2.0 Project Structure

The v2.0 refactor introduced a clean modular architecture:

**Root Files:**
- `music_video_generator.py` - Main CLI entry point
- `run_tests.py` - Comprehensive pytest-based test runner
- `setup.py` - Package installation configuration

**Core Package (`music_video_generator/`):**
- `film_library.py` - Film analysis and caching with metadata
- `music_video_generator.py` - Video generation with multiple strategies
- `cli.py` - Command-line interface

**Testing Infrastructure (`tests/`):**
- `unit/` - Unit tests for individual components
- `integration/` - End-to-end workflow tests
- `performance/` - Performance benchmarks
- `utils/` - Test asset generators (`create_test_audio.py`, `create_test_video.py`)

**Legacy Code (`attic/`):**
- All previous generator versions and legacy test scripts

## Output Structure

Each run creates a timestamped directory containing:
- `analysis.html` - Interactive analysis report with thumbnails
- `scene_metadata.json` - Scene timing and analysis data
- `thumbnails/` - Generated scene thumbnails
- `clips/` - Individual scene clips
- `remix_*.mp4` - Final generated video

## Version Evolution

The project shows iterative development with multiple generator versions:
- Original: Basic scene-to-beat mapping
- Robust: Error handling for numpy/audio issues
- Progressive: Journey through entire movie chronologically
- Bulletproof: Maximum error resistance
- Ultra-Robust: Full analysis with HTML reporting

## Common Issues & Solutions

- **Numpy formatting errors**: Use `safe_float()` and `safe_int()` helper methods
- **Audio loading failures**: Test with librosa's built-in example first
- **Scene detection problems**: Adjust ContentDetector threshold (default: 30.0)
- **MoviePy crashes**: Ensure FFmpeg is properly installed and accessible

## Development Patterns

### Error Handling Standards
All generators implement these safety patterns:
- `safe_float()` and `safe_int()` methods for numpy type conversion
- Try-catch blocks around librosa operations
- Fallback values (0.0, 0) for failed conversions
- Progress indicators with descriptive messages

### Generator Inheritance Hierarchy
Several generators extend base classes:
- `PerfectForwardGenerator` extends `ForwardOnlyGenerator`
- `BulletproofGenerator` extends `PerfectForwardGenerator`
- `ConservativeBulletproofGenerator` extends `PerfectForwardGenerator`

### Consistent Class Structure
All main generator classes follow this pattern:
```python
class GeneratorName:
    def __init__(self, video_path, audio_path, output_path="default.mp4")
    def safe_float(self, value)  # Type safety
    def safe_int(self, value)    # Type safety
    def detect_scenes()          # Scene detection
    def analyze_audio()          # Beat detection
    def generate_music_video()   # Main orchestration
```

## Key Algorithms

### Progressive Sampling Strategy
The `progressive_sampling_generator.py` creates a chronological journey through the film:
- Samples scenes progressively from start to end
- Maintains narrative flow while syncing to music beats
- Avoids repetition by tracking used scenes

### Adaptive Tempo Matching
The adaptive tempo generators adjust video pacing to match music:
- Analyze song tempo using librosa beat detection
- Map scene durations to beat intervals
- Handle tempo changes within songs

### Scene Selection Strategies
- **Random**: Pure random selection for energetic cuts
- **Progressive**: Chronological progression through film
- **Forward-only**: Never repeats scenes, moves forward only
- **Conservative**: Cautious approach with extensive error checking