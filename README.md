# YouTube Intro Generator 🎬

Generate cinematic noir-style YouTube intro videos using fal.ai's video generation API and create complementary animations with Manim.

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

### 2. Get fal.ai API Key

1. Go to [fal.ai](https://fal.ai)
2. Sign up for an account
3. Navigate to your API settings/dashboard
4. Generate an API key
5. Copy the key

### 3. Configure API Key

Copy the example environment file and add your API key:

```bash
# Copy the example file
cp .env.example .env

# Edit .env file with your API key
nano .env

# Or use any text editor
open .env
```

Replace `your_fal_api_key_here` with your actual API key:
```
FAL_API_KEY=fal_key_xxxxxxxxxxxxxxxxxx
```

**Important:** The `.env` file is already in `.gitignore` so your API key won't be committed to version control.

### 4. Add Reference Image

Place your reference image (face photo) in the `assets/` folder:
```bash
# Example: copy your image
cp ~/path/to/your/photo.jpg assets/harry_thumbnail.png
```

## 📖 Usage

### Generate YouTube Intro Video

**Remember to activate your virtual environment first:**
```bash
source venv/bin/activate
```

Then generate videos:
```bash
# Basic usage
python cli.py generate \
  --title "My Amazing Video Title" \
  --footer "@yourusername / yoursite.com" \
  --reference-image assets/your_photo.png

# Custom output path
python cli.py generate \
  --title "Inside Claude Code: Animating AI" \
  --footer "@htormey / htormey.org" \
  --reference-image assets/harry_thumbnail.png \
  --output-path output/my_custom_intro.mp4

# With custom duration
python cli.py generate \
  --title "Physics Explained" \
  --footer "@physics / science.com" \
  --reference-image assets/face.jpg \
  --duration 7
```

### Render Manim Animations

```bash
# Make sure virtual environment is active first
source venv/bin/activate

# Low quality preview (fast)
python -m manim -pql scenes/black_hole_scene.py HowBlackHolesWorkScene

# High quality render
python -m manim -pqh scenes/black_hole_scene.py HowBlackHolesWorkScene

# 4K quality
python -m manim -pqk scenes/black_hole_scene.py HowBlackHolesWorkScene
```

## 🎨 Video Style

The generated intros feature a **noir/Twilight Zone aesthetic**:

- **Black & white** cinematic style
- **3D spacetime grid** that warps and collapses
- **Code snippets** appear over the animation
- **Face emergence** from a stylized black hole
- **Custom title and footer** text overlay
- **Eerie ambient** soundtrack

### Scene Timeline
- `0s`: Fade in from black with warped spacetime grid
- `0.5s`: Code appears: `simulate_spacetime_geometry(mass=1.5e30)`
- `2.0s`: Grid collapses into black hole formation
- `3.5s`: Your face emerges from the black hole
- `4.5s`: Title and footer text appear

## 📁 Project Structure

```
youtube-intro-generator/
├── cli.py                    # Main CLI application
├── .env                      # API key configuration (not in git)
├── .env.example              # Template for environment variables
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── venv/                     # Virtual environment (not in git)
├── assets/                   # Reference images
│   └── (your photos here)
├── output/                   # Generated videos (not in git)
│   └── (generated intros)
└── scenes/                   # Manim animation scenes
    └── black_hole_scene.py   # Black hole physics animation
```

## 🛠 Troubleshooting

### Python/pip Issues
```bash
# If pip command not found, use:
python3 -m pip install -r requirements.txt

# Or install uv for faster package management:
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -r requirements.txt
```

### API Key Issues
- Make sure your `.env` file contains the correct fal.ai API key
- Verify the key starts with `fal_key_`
- Check that you have credits remaining on your fal.ai account

### Image Issues
- Supported formats: PNG, JPG, JPEG
- Recommended: Clear face photo, good lighting
- Size: Any reasonable size (will be processed by API)

### Manim Issues
```bash
# If manim installation fails, try:
python3 -m pip install manim[jupyter]

# Or for M1/M2 Macs:
brew install py3cairo ffmpeg
python3 -m pip install manim
```

## 🎯 Examples

### Example 1: Tech Tutorial Intro
```bash
python3 cli.py generate \
  --title "Building AI with Python" \
  --footer "@codewithme / github.com/codewithme" \
  --reference-image assets/profile.jpg \
  --output-path output/ai_tutorial_intro.mp4
```

### Example 2: Science Explainer
```bash
python3 cli.py generate \
  --title "Quantum Physics Made Simple" \
  --footer "@scienceexplained / physics.edu" \
  --reference-image assets/scientist.png \
  --duration 6
```

## 🔧 Customization

You can modify the video generation by editing the prompt in `cli.py`:

- Change the `style` parameter for different aesthetics
- Modify the `scene` timeline for different animations
- Adjust `music` description for different soundtracks
- Update `duration` for longer/shorter videos

## 📊 Costs

fal.ai video generation costs vary by:
- Video duration (longer = more expensive)
- Video quality/resolution
- Usage frequency

Check [fal.ai pricing](https://fal.ai/pricing) for current rates.

## 🤝 Contributing

Feel free to:
- Add new Manim scenes in `scenes/`
- Modify video generation prompts
- Improve the CLI interface
- Add new export formats

## 📝 License

This project is open source. Use responsibly and respect fal.ai's terms of service.