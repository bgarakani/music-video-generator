# Active Context: Music Video Generation & Archival Remix Engine

## Current Work Focus

### Project Status
- **Phase**: Major refactoring completed - Premiere Pro-style interface implemented
- **Current Priority**: Professional video editing interface with clips-first workflow
- **Active Development**: New `premiere_style_archival_engine.py` with 3-phase pipeline

### Recent Changes
- **MAJOR REFACTORING**: Complete Premiere Pro-style archival analysis engine created
- **Clips-First Workflow**: Phase 1 generates all clips with audio and thumbnails FIRST
- **Professional Timeline**: Proportional clip widths matching actual scene durations
- **Stereo Audio Analysis**: Left/Right channel waveform visualization
- **Audio Spectrogram**: Real-time frequency analysis panel
- **Monitor Panel**: Professional playback controls with scrubbing and level meters
- **Multi-Zoom Timeline**: 6 zoom levels from fit-all to 1-second precision
- **Comprehensive Testing**: Complete test suite (`test_premiere_engine.py`)

## Active Decisions and Considerations

### Generator Strategy Evolution
- **Multiple Approaches**: Project maintains several generator variations rather than single "best" version
- **Error Handling Priority**: Robust error handling is critical due to numpy/librosa type issues
- **Progressive vs Random**: Ongoing evaluation of scene selection strategies
- **Output Quality**: Focus on both technical reliability and artistic merit

### Key Technical Challenges
1. **Numpy Type Safety**: Consistent issues with numpy scalar types requiring `safe_float()` and `safe_int()` methods
2. **Audio Loading Reliability**: librosa can fail unpredictably, requiring fallback strategies
3. **Scene Detection Tuning**: ContentDetector threshold optimization for different video types
4. **Memory Management**: Large video files require careful memory handling during processing

## Next Steps

### Immediate Priorities
- Test and validate all generator variations with diverse input types
- Improve documentation and user guidance
- Standardize output directory structures
- Enhance error reporting and user feedback

### Future Development Areas
- **Advanced Scene Analysis**: More sophisticated scene understanding beyond basic cuts
- **Music Structure Awareness**: Better synchronization with song structure (verse/chorus/bridge)
- **User Parameter Control**: Allow users to influence generator behavior
- **Performance Optimization**: Speed improvements for large video processing
- **Format Support**: Expand supported video/audio formats

## Important Patterns and Preferences

### Code Organization
- Each generator is self-contained with consistent method signatures
- Safety methods (`safe_float`, `safe_int`) are standard across all generators
- Progress reporting with descriptive messages is expected
- Error handling should be comprehensive but not verbose

### Testing Approach
- `simple_working_test.py` serves as comprehensive integration test
- Individual component tests validate specific functionality
- Test with librosa's built-in example data for reliability
- Always verify FFmpeg availability before video processing

### Output Standards
- Timestamped directories prevent overwriting previous runs
- Include both final video and analysis artifacts
- HTML reports with thumbnails provide valuable user feedback
- JSON metadata enables further processing and analysis

## Learnings and Project Insights

### What Works Well
- **Modular Generator Design**: Multiple specialized generators serve different use cases
- **Comprehensive Error Handling**: Robust error patterns prevent crashes
- **Rich Output**: HTML analysis reports greatly improve user understanding
- **Test-Driven Approach**: Comprehensive testing catches issues early

### Common Pitfalls
- **Numpy Type Issues**: Require consistent use of safety conversion methods
- **Audio Analysis Failures**: Always need fallback values and error handling
- **Scene Detection Sensitivity**: Threshold values need tuning for different content
- **Path Management**: Consistent directory structure is important for reliability

### Development Philosophy
- **Reliability Over Features**: Robust execution is more important than advanced features
- **Multiple Solutions**: Maintain different approaches rather than forced convergence
- **User Transparency**: Provide clear analysis and reporting of automated decisions
- **Iterative Improvement**: Incremental enhancement of working systems
