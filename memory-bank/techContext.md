# Technical Context: Music Video Generator v2.0

## v2.0 Architecture Overview

### Two-Phase Design
The system is architected around two distinct phases that optimize for both efficiency and flexibility:

**Phase 1: Film Preparation (FilmLibrary)**
- One-time analysis per film per parameter set
- Computationally expensive operations (scene detection, clip extraction)
- Results cached to disk with parameter-based validation
- Approximately 60 seconds for 10-minute video

**Phase 2: Video Generation (MusicVideoGenerator)**
- Fast, repeatable video creation from cached film data
- Multiple songs can use the same film library
- Strategy-based scene selection
- Approximately 1-2 minutes for 3-minute music video

### Core Components

```
music_video_project/
├── music_video_generator.py           # CLI entry point
├── music_video_generator/             # Core package
│   ├── __init__.py                    # Package exports
│   ├── film_library.py                # Phase 1: Film analysis & caching
│   ├── music_video_generator.py       # Phase 2: Video generation
│   └── cli.py                         # Command-line interface logic
├── clips_library/                     # Cached film libraries
├── output/                            # Generated music videos
├── tests/                             # Comprehensive test suite
├── attic/                             # Legacy generators (archived)
└── docs/                              # Documentation and plans
```

## Technologies Used

### Core Libraries

**librosa (Audio Analysis)**
- Beat detection and tempo estimation
- Returns numpy arrays (important for type handling)
- Sample rate: 22050 Hz (default)

**MoviePy (Video Processing)**
- VideoFileClip for loading and manipulation
- Subclipping for scene extraction
- Concatenation for final assembly

**PySceneDetect (Scene Detection)**
- ContentDetector with configurable threshold (10-50 range)
- Scene boundary detection based on visual content changes

**NumPy (Numerical Computing)**
- Type safety critical: librosa returns numpy arrays not scalars
- Requires safe_float() and safe_int() conversion throughout

**FFmpeg (External Dependency)**
- Direct FFmpeg rendering for final output
- Must be in system PATH
- Critical for all video operations

## Known Technical Issues

### Resolved Issues
1. Numpy Type Errors - Fixed with safe_float/safe_int methods
2. librosa Tempo Array Format - Fixed in commit 40f5e8d
3. Code Duplication - Eliminated through v2.0 refactor

### Current Limitations
1. FFmpeg Dependency - External system dependency required
2. Memory for Large Videos - Videos over 1 hour can exhaust RAM
3. Beat Detection Genre Bias - Works best with clear rhythmic patterns
