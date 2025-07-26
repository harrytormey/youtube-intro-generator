# YouTube Intro Generator - Complete Implementation Specification

## Overview
A CLI tool that generates cinematic noir-style YouTube intro videos using fal.ai's Veo3 API with local text overlay and face integration. The tool supports caching for expensive API calls and video combination for complete YouTube workflows.

## Core Architecture

### Command Structure
The CLI has three main commands:
1. `generate-background` - One-time background video generation
2. `main` - Create intro with text and face using cached background
3. `combine` - Combine intro with main content video

### Dependencies
```
typer - CLI framework
requests - HTTP requests for fal.ai API
python-dotenv - Environment variable management
pillow - Image processing (NOT used for text rendering)
numpy - Array operations for background removal
scipy - Image processing operations
```

## Implementation Details

### 1. Background Generation (`generate-background` command)

**Purpose**: Generate and cache a clean noir-style spacetime background using fal.ai's Veo3 API.

**Key Requirements**:
- Uses fal.ai Veo3 endpoint: `https://fal.run/fal-ai/veo3`
- 8-second duration, 16:9 aspect ratio, 1080p resolution
- CRITICAL: Prompt must specify "NO TEXT, NO FACES, NO PEOPLE" for clean compositing
- Saves to `cache/background.mp4`
- Includes ambient audio generation

**Prompt Template**:
```
Create a cinematic noir-style spacetime animation in black and white, Twilight Zone aesthetic:

0-2s: Fade in from black. A warped 3D spacetime grid oscillates over a starfield.
2-4s: The grid begins warping and collapsing inward, creating spacetime distortion.
4-6s: A stylized black hole forms at the center, warping the grid dramatically.
6-8s: The black hole stabilizes with swirling cosmic matter, grid continues warping.

Style: black and white, Twilight Zone, noir, cinematic, minimal, eerie ambient atmosphere.

IMPORTANT: NO TEXT, NO FACES, NO PEOPLE - just pure abstract spacetime geometry.
Clean background suitable for compositing text and images later.
```

### 2. Intro Generation (`main` command) 

**Purpose**: Composite text and face onto cached background using local processing.

**Critical Implementation Details**:

#### Text Rendering
- **MUST use FFmpeg's native `drawtext` filter** - PIL text rendering fails completely
- Font sizes: Title = 5% of screen height, Footer = 3% of screen height  
- Font: `/System/Library/Fonts/Arial.ttc`
- Colors: White text with black border for maximum contrast
- Border width: 2.5% of screen height for title, 1.5% for footer
- Positioning: Title centered, footer bottom-left (40px margin)
- Timing: Title appears at 6s, footer at 6.5s

#### Face Processing
- **Simple background removal only** - complex morphological operations cause artifacts
- Conservative white pixel removal: RGB values > 250
- Convert to grayscale while preserving alpha channel
- Resize to 30% of video width
- Center positioning with fade-in at 4s, fade-out at 5.5s

#### FFmpeg Command Structure
```bash
ffmpeg -y \
  -i background_video \
  -loop 1 -i face_overlay \
  -filter_complex "
    [1:v]fade=t=in:st=4:d=0.5:alpha=1,fade=t=out:st=5.5:d=0.5:alpha=1[face];
    [0:v][face]overlay=0:0[bg_face];
    [bg_face]drawtext=text='$title':fontfile=/System/Library/Fonts/Arial.ttc:fontsize=$title_size:fontcolor=white:borderw=$border_width:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,6,8)'[with_title];
    [with_title]drawtext=text='$footer':fontfile=/System/Library/Fonts/Arial.ttc:fontsize=$footer_size:fontcolor=white:borderw=$border_width:bordercolor=black:x=40:y=h-text_h-40:enable='between(t,6.5,8)'[final]
  " \
  -map '[final]' -map '0:a' -c:a copy -c:v libx264 -t 8
```

### 3. Video Combination (`combine` command)

**Purpose**: Combine intro video with main content video for complete YouTube workflow.

**Critical Audio Handling**:
- **MUST use single FFmpeg command with separate video/audio concatenation**
- Multi-step approaches cause audio sync issues
- Preserve original audio characteristics from main video

**Implementation**:
```bash
ffmpeg -y \
  -i intro_video \
  -i main_video \
  -filter_complex "
    [0:v]scale=WIDTH:HEIGHT[intro_v];
    [1:v]scale=WIDTH:HEIGHT[main_v];
    [intro_v][main_v]concat=n=2:v=1:a=0[final_v];
    [0:a]atrim=end=8[intro_a];
    [intro_a][1:a]concat=n=2:v=0:a=1[final_a]
  " \
  -map '[final_v]' -map '[final_a]' \
  -c:v libx264 -c:a aac -b:a 192k \
  -ar ORIGINAL_SAMPLE_RATE -ac ORIGINAL_CHANNELS \
  -shortest -movflags +faststart -pix_fmt yuv420p
```

**Key Requirements**:
- Analyze main video properties using `ffprobe` 
- Match resolution, preserve original sample rate and channels
- Use `atrim=end=8` to cleanly cut intro audio
- Separate video and audio concatenation prevents timing issues
- QuickTime compatibility with `yuv420p` and `faststart`

## File Structure
```
youtube-intro-generator/
├── cli.py                    # Main CLI with all three commands
├── requirements.txt          # Dependencies listed above
├── .env                      # FAL_API_KEY configuration
├── .env.example              # Template
├── cache/                    # Cached background videos
│   └── background.mp4
├── assets/                   # Reference images
│   └── *.png, *.jpg
└── output/                   # Generated videos
    └── *.mp4
```

## Error Handling

### FFmpeg Compatibility
- Clean up temporary files in `finally` blocks
- Use `capture_output=True` and display stderr on failures
- Validate file existence before processing

### API Integration
- Handle fal.ai authentication with Authorization header: `Key {api_key}`
- Parse JSON responses safely with fallback for missing fields
- Download binary content properly for video files

### Image Processing
- Conservative background removal to prevent face artifacts
- Graceful fallback for font loading failures
- Proper alpha channel handling throughout pipeline

## Performance Optimizations

### Caching Strategy
- One-time expensive API call for background generation
- Reuse cached background for multiple intros
- Local processing for text and face (fast)

### Video Processing
- Minimal re-encoding where possible
- Use `copy` codec when appropriate
- Single-pass processing for combination

## Platform Compatibility

### macOS Specific
- Font path: `/System/Library/Fonts/Arial.ttc`
- Virtual environment setup for externally-managed Python
- Homebrew FFmpeg installation

### Cross-Platform Considerations
- Use `pathlib.Path` for file handling
- Subprocess calls with proper shell escaping
- Environment variable loading with python-dotenv

## Quality Settings

### Video Output
- Codec: libx264 with medium preset
- CRF: 23 (high quality)
- Pixel format: yuv420p (compatibility)
- Resolution: Match main video or 1920x1080 default

### Audio Output  
- Codec: AAC
- Bitrate: 192k for combination, copy for intro generation
- Preserve original sample rate and channel configuration
- FastStart flag for streaming compatibility

## Command Examples

### Complete Workflow
```bash
# Step 1: Generate background (one-time, ~2 minutes, costs API credits)
python cli.py generate-background

# Step 2: Create intro (fast, local processing)
python cli.py main \
  --title "Building a Cinematic YouTube Intro" \
  --footer "@username / website.com" \
  --reference-image assets/face.png \
  --output-path intro.mp4

# Step 3: Combine with main content (fast, perfect audio sync)
python cli.py combine \
  --intro-video intro.mp4 \
  --main-video main_content.mp4 \
  --output-path final_youtube.mp4
```

## Known Issues & Solutions

### Text Rendering
- **Problem**: PIL text rendering produces corrupted output
- **Solution**: Use FFmpeg drawtext filter exclusively

### Face Artifacts  
- **Problem**: Complex background removal creates black spots
- **Solution**: Simple white pixel removal only (RGB > 250)

### Audio Sync
- **Problem**: Multi-step processing causes timing drift
- **Solution**: Single FFmpeg command with separate A/V concatenation

### Frame Rate Mismatches
- **Problem**: Converting frame rates affects audio pitch
- **Solution**: Preserve original frame rates, only scale resolution

This specification provides everything needed to recreate the exact functionality that was developed through the iterative debugging process.