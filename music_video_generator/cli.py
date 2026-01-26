#!/usr/bin/env python3
"""Command-line interface for Music Video Generator."""
import argparse
import sys
from pathlib import Path
from .film_library import FilmLibrary
from .music_video_generator import MusicVideoGenerator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Music Video Generator - Create artistic remixes from film and music",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Prepare film library (one-time operation)
  python music_video_generator.py --prepare --film movie.mp4

  # Generate music video with progressive strategy
  python music_video_generator.py --film movie.mp4 --song track.mp3

  # Use every 2nd beat for fewer cuts
  python music_video_generator.py --film movie.mp4 --song track.mp3 --beat-skip 2

  # Use random strategy with every 4th beat
  python music_video_generator.py --film movie.mp4 --song track.mp3 --strategy random --beat-skip 4
        """
    )

    # Operation mode
    parser.add_argument('--prepare', action='store_true',
                       help='Prepare film library only (no music video generation)')

    # Required arguments
    parser.add_argument('--film', required=True, type=str,
                       help='Path to film/video file')
    parser.add_argument('--song', type=str,
                       help='Path to song/audio file (required unless --prepare)')

    # Scene detection parameters
    parser.add_argument('--threshold', type=float, default=30.0,
                       help='Scene detection threshold (10-50 range, default: 30.0)')
    parser.add_argument('--min-scene-len', type=float, default=1.0,
                       help='Minimum scene duration in seconds (default: 1.0)')
    parser.add_argument('--force-regenerate-clips', action='store_true',
                       help='Force regeneration of clips even if cache exists')

    # Music video generation parameters
    parser.add_argument('--strategy', type=str, default='progressive',
                       choices=['progressive', 'random', 'forward_only', 'no_repeat'],
                       help='Scene selection strategy (default: progressive)')
    parser.add_argument('--beat-skip', type=int, default=1,
                       help='Use every Nth beat (1=all beats, 2=every other, etc. Default: 1)')

    # Output directories
    parser.add_argument('--clips-library-dir', type=str, default='clips_library',
                       help='Directory for film clip library (default: clips_library)')
    parser.add_argument('--output-dir', type=str, default='music_videos',
                       help='Directory for music video outputs (default: music_videos)')

    args = parser.parse_args()

    # Validate arguments
    if not args.prepare and not args.song:
        parser.error("--song is required unless --prepare is specified")

    # Print header
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         MUSIC VIDEO GENERATOR v2.0                          ║
    ╠══════════════════════════════════════════════════════════════╣
    """)

    try:
        # Step 1: Prepare FilmLibrary
        print(f"║  Film: {Path(args.film).name:<53} ║")
        print(f"║  Threshold: {args.threshold:<48} ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")

        library = FilmLibrary(
            args.film,
            threshold=args.threshold,
            min_scene_len=args.min_scene_len,
            force_regenerate=args.force_regenerate_clips,
            clips_library_dir=args.clips_library_dir
        )

        # Check cache or generate
        if library._check_cache() and not args.force_regenerate_clips:
            print("📦 Using cached clips")
            library._load_from_cache()
        else:
            print("🎬 Generating film library...")

            # Detect scenes
            scenes = library.detect_scenes()
            if not scenes:
                print("✗ Scene detection failed")
                return 1

            # Extract clips
            clip_count = library.extract_clips(scenes)
            if clip_count == 0:
                print("✗ Clip extraction failed")
                return 1

            # Generate thumbnails
            library.generate_thumbnails(scenes)

            # Analyze scenes
            library.analyze_scenes(scenes)

            # Save metadata
            library.save_metadata()

        # If --prepare only, stop here
        if args.prepare:
            print("\n✓ Film library preparation complete")
            print(f"   Location: {library.library_dir}")
            print(f"   Scenes: {len(library.get_scenes())}")
            return 0

        # Step 2: Generate Music Video
        print(f"\n🎵 Generating music video...")
        print(f"   Song: {Path(args.song).name}")
        print(f"   Strategy: {args.strategy}")
        print(f"   Beat skip: {args.beat_skip}")

        generator = MusicVideoGenerator(
            library,
            args.song,
            strategy=args.strategy,
            beat_skip=args.beat_skip,
            output_dir=args.output_dir
        )

        # Analyze audio
        music_analysis = generator.analyze_audio()
        if not music_analysis['beats']:
            print("✗ Audio analysis failed")
            return 1

        # Validate scene-beat ratio
        generator.validate_scene_beat_ratio()

        # Select scenes
        selected = generator.select_scenes()
        if not selected:
            print("✗ Scene selection failed")
            return 1

        print(f"\n✓ Music video generation complete!")
        print(f"   Output: {generator.output_dir}")

        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        return 1
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        return 1
    except KeyboardInterrupt:
        print(f"\n\n✗ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
