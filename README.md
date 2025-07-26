# YouTube Intro Generator 🎬

Generate cinematic noir-style YouTube intro videos using fal.ai's video generation API with local text and face compositing. Features a caching system to minimize expensive API calls and video combination for complete YouTube workflows.

## 🚀 Quick Setup

### 1. Install Python Dependencies

On macOS with externally-managed Python, you need to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Important:** Always activate the virtual environment before running the CLI:
```bash
# Every time you use this project:
source venv/bin/activate
```

### 2. Install FFmpeg

FFmpeg is required for video processing:

```bash
# macOS (using Homebrew)
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### 3. Get fal.ai API Key

1. Go to [fal.ai](https://fal.ai)
2. Sign up for an account
3. Navigate to your API settings/dashboard
4. Generate an API key
5. Copy the key

### 4. Configure API Key

Copy the example environment file and add your API key:

```bash
# Copy the example file
cp .env.example .env

# Edit .env file with your API key
nano .env
```

Replace `your_fal_api_key_here` with your actual API key:
```
FAL_API_KEY=fal_key_xxxxxxxxxxxxxxxxxx
```

**Important:** The `.env` file is already in `.gitignore` so your API key won't be committed to version control.

### 5. Add Reference Image

Place your reference image (face photo) in the `assets/` folder:
```bash
# Example: copy your image
cp ~/path/to/your/photo.jpg assets/harry_thumbnail.png
```

## 📖 Usage

The workflow consists of three commands that work together:

### Step 1: Generate Background (One-time Setup)

Generate and cache the noir-style spacetime background:

```bash
source venv/bin/activate
python cli.py generate-background
```

- **Duration**: ~2 minutes
- **Cost**: Uses fal.ai API credits
- **Output**: `cache/background.mp4`
- **Frequency**: Only needed once (or when you want a new background)

### Step 2: Create Your Intro (Fast & Local)

Generate your intro video with custom text and face:

```bash
python cli.py main \
  --title "Your Video Title Here" \
  --footer "@yourusername / yoursite.com" \
  --reference-image assets/your_photo.png \
  --output-path output/my_intro.mp4
```

**Options:**
- `--title`: Main title text (appears at 6 seconds)
- `--footer`: Footer text like handle/website (appears at 6.5 seconds)  
- `--reference-image`: Path to your face photo
- `--background-video`: Custom background (default: `cache/background.mp4`)
- `--output-path`: Where to save the intro (default: `intro.mp4`)

### Step 3: Combine with Main Content (Optional)

Combine your intro with your main video content:

```bash
python cli.py combine \
  --intro-video output/my_intro.mp4 \
  --main-video path/to/your_main_video.mp4 \
  --output-path output/final_youtube.mp4
```

**Options:**
- `--intro-video`: Path to your intro video
- `--main-video`: Path to your main content video
- `--output-path`: Final combined video (default: `combined.mp4`)
- `--transition-duration`: Cross-fade duration in seconds (default: 0.8)

## 🎯 Complete Examples

### Example 1: Tech Tutorial
```bash
# Step 1: Generate background (one-time)
python cli.py generate-background

# Step 2: Create intro
python cli.py main \
  --title "Building AI with Python" \
  --footer "@codewithme / github.com/codewithme" \
  --reference-image assets/profile.jpg \
  --output-path output/ai_tutorial_intro.mp4

# Step 3: Combine with main content
python cli.py combine \
  --intro-video output/ai_tutorial_intro.mp4 \
  --main-video recordings/my_tutorial.mp4 \
  --output-path output/final_ai_tutorial.mp4
```

### Example 2: Science Explainer
```bash
# Use cached background from before
python cli.py main \
  --title "Quantum Physics Made Simple" \
  --footer "@scienceexplained / physics.edu" \
  --reference-image assets/scientist.png \
  --output-path output/quantum_intro.mp4

# Combine with main video
python cli.py combine \
  --intro-video output/quantum_intro.mp4 \
  --main-video recordings/quantum_explanation.mp4 \
  --output-path output/final_quantum_video.mp4
```

## 🎨 Video Style & Features

### Visual Style
- **Noir/Twilight Zone aesthetic**: Black & white cinematic style
- **3D spacetime grid**: Warps and collapses into a black hole
- **Face integration**: Your face emerges from the cosmic scene
- **Professional text**: Clean, readable white text with black borders
- **Perfect timing**: 8-second intro with precise element timing

### Technical Features
- **Caching system**: Generate background once, reuse for multiple intros
- **Local processing**: Text and face compositing happens locally (fast & free)
- **Audio sync**: Perfect audio synchronization when combining videos
- **Format compatibility**: Works with ScreenStudio and other recording software
- **QuickTime compatible**: Plays in QuickTime Player and video editors

### Timeline
- `0-2s`: Fade in from black with warped spacetime grid over starfield
- `2-4s`: Grid begins warping and collapsing inward  
- `4-6s`: Black hole forms, your face fades in from the center
- `6s`: Title text appears (centered)
- `6.5s`: Footer text appears (bottom-left)
- `4-5.5s`: Face fade-out with transition timing

## 📁 Project Structure

```
youtube-intro-generator/
├── cli.py                    # Main CLI application (3 commands)
├── spec.md                   # Complete implementation specification
├── .env                      # API key configuration (not in git)
├── .env.example              # Template for environment variables
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── venv/                     # Virtual environment (not in git)
├── cache/                    # Cached background videos
│   └── background.mp4        # Generated by generate-background
├── assets/                   # Reference images
│   └── *.png, *.jpg          # Your face photos
├── output/                   # Generated videos (not in git)
│   ├── *_intro.mp4          # Generated intros
│   └── final_*.mp4          # Combined final videos
└── scenes/                   # Manim animation scenes (optional)
    └── *.py                 # Educational animations
```

## 🛠 Troubleshooting

### Command Issues
```bash
# If you get "No such option" errors, make sure to use the right command:
python cli.py main --title "..." --footer "..." --reference-image "..."

# Not this:
python cli.py --title "..."  # ❌ Wrong
```

### Python/pip Issues
```bash
# If pip command not found:
python3 -m pip install -r requirements.txt

# If virtual environment issues:
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### FFmpeg Issues
```bash
# If FFmpeg not found:
brew install ffmpeg

# Verify installation:
ffmpeg -version
which ffmpeg
```

### API Key Issues
- Make sure your `.env` file contains the correct fal.ai API key
- Verify the key starts with `fal_key_`
- Check that you have credits remaining on your fal.ai account
- Test with: `python cli.py generate-background`

### Audio Sync Issues
- If main video audio sounds slow/deep, the combine command automatically handles this
- Make sure you're using the latest version of the combine command
- The tool preserves original audio characteristics from your main video

### Image Issues
- **Supported formats**: PNG, JPG, JPEG
- **Recommended**: Clear face photo with good lighting
- **Background removal**: Works best with light/white backgrounds
- **Size**: Any reasonable size (will be automatically processed)

## 💡 Pro Tips

### Workflow Optimization
1. **Generate background once**: Use `generate-background` only when you want a new style
2. **Batch intro creation**: Create multiple intros using the same cached background
3. **Test before combining**: Preview your intro before combining with main content
4. **Resolution matching**: The combine command automatically matches your main video's resolution

### Content Creation
- **Title length**: Keep titles concise for better readability
- **Footer format**: Use format like "@username / website.com"
- **Face photos**: Use well-lit, clear photos for best results
- **Main video**: Any format/resolution works (ScreenStudio, OBS, etc.)

### Cost Management
- **Background caching**: Saves money by reusing expensive API-generated backgrounds
- **Local processing**: Text and face compositing is free and fast
- **Batch creation**: Create multiple intros from one background generation

## 📊 Costs

### fal.ai API Costs
- **Background generation**: ~$0.10-0.50 per 8-second video (varies by current pricing)
- **Intro creation**: $0 (uses cached background + local processing)
- **Video combination**: $0 (local FFmpeg processing)

Check [fal.ai pricing](https://fal.ai/pricing) for current rates.

## 🤝 Contributing

Feel free to:
- Add new background styles by modifying the prompt in `generate-background`
- Improve text positioning and styling
- Add new video effects or transitions
- Enhance the face processing algorithm
- Add support for different video formats

## 📝 License

This project is open source. Use responsibly and respect fal.ai's terms of service.

---

**Need help?** Check `spec.md` for complete technical implementation details.