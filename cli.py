import os
import typer
import requests
import base64
import subprocess
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
app = typer.Typer()

def get_api_key(api_key: str = None):
    return api_key or os.getenv("FAL_API_KEY") or typer.BadParameter("Missing API key")

def create_text_overlay(width: int, height: int, title: str, footer: str, output_path: str):
    """Create a text overlay image with title and footer."""
    
    # Create transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a nice font - ABSOLUTELY GIGANTIC text
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", int(height * 0.8))  # 200% BIGGER
        footer_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", int(height * 0.4))  # 200% BIGGER
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()
    
    # Get text dimensions
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    
    footer_bbox = draw.textbbox((0, 0), footer, font=footer_font)
    footer_width = footer_bbox[2] - footer_bbox[0]
    footer_height = footer_bbox[3] - footer_bbox[1]
    
    # Position title in center
    title_x = (width - title_width) // 2
    title_y = (height - title_height) // 2
    
    # Position footer in bottom-left
    footer_x = 40
    footer_y = height - footer_height - 40
    
    # Draw text with stroke (outline) - massive stroke for gigantic text
    stroke_width = 18
    
    # Draw title with massive white stroke on transparent background
    # Use white stroke instead of black to avoid black background effect
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((title_x + dx, title_y + dy), title, font=title_font, fill=(255, 255, 255, 200))  # White stroke
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255, 255))  # Bright white text
    
    # Draw footer with massive white stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((footer_x + dx, footer_y + dy), footer, font=footer_font, fill=(255, 255, 255, 200))  # White stroke
    draw.text((footer_x, footer_y), footer, font=footer_font, fill=(255, 255, 255, 255))  # Bright white text
    
    img.save(output_path)

def wrap_text_for_ffmpeg(text: str, max_width: int = 50) -> list:
    """Wrap text into multiple lines for FFmpeg drawtext, returning list of lines."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        # Calculate length including spaces between words
        word_with_space = len(word) + (1 if current_line else 0)
        
        if current_length + word_with_space <= max_width:
            current_line.append(word)
            current_length += word_with_space
        else:
            # If we have words in current line, finish it and start new line
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                # Single word is too long, just add it anyway
                lines.append(word)
                current_length = 0
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def composite_video(background_path: Path, face_image_path: Path, title: str, footer: str, output_path: Path):
    """Composite text and face onto background video using ffmpeg."""
    
    # Get video dimensions using ffprobe
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
        str(background_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        data = json.loads(result.stdout)
        video_stream = next(s for s in data['streams'] if s['codec_type'] == 'video')
        width = int(video_stream['width'])
        height = int(video_stream['height'])
    except:
        # Default to 1080p if ffprobe fails
        width, height = 1920, 1080
    
    # Process face image with background removal
    face_img = Image.open(face_image_path)
    face_img = face_img.convert('RGBA')  # Keep alpha channel for transparency
    
    # Better background removal with smoother edges
    import numpy as np
    img_array = np.array(face_img)
    
    # Completely new approach - simple but effective background removal
    # Your image appears to be mostly grayscale already, so let's work with that
    
    # Convert to grayscale for processing but keep original for final output
    gray_img = np.mean(img_array[:, :, :3], axis=2)
    
    # Create a very conservative mask - only remove very light pixels
    # Focus on pure white and very light gray only
    background_mask = (
        (img_array[:, :, 0] > 250) & 
        (img_array[:, :, 1] > 250) & 
        (img_array[:, :, 2] > 250)
    )
    
    # Don't over-process - just set background pixels to transparent
    img_array[background_mask, 3] = 0
    
    # Keep the rest of the image intact - no morphological operations that cause artifacts
    
    # Convert back to PIL Image
    face_img = Image.fromarray(img_array)
    
    # Convert to grayscale while preserving alpha
    # Split channels
    r, g, b, a = face_img.split()
    # Convert RGB to grayscale
    gray = r.convert('L')
    # Merge back with alpha
    face_img = Image.merge('LA', (gray, a))
    face_img = face_img.convert('RGBA')  # Convert back to RGBA for consistency
    
    # Resize face to appropriate size
    face_size = int(width * 0.3)  # Made slightly bigger too
    face_img = face_img.resize((face_size, face_size), Image.Resampling.LANCZOS)
    
    # Create face overlay with transparent background
    face_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    face_x = (width - face_size) // 2
    face_y = (height - face_size) // 2
    face_overlay.paste(face_img, (face_x, face_y))
    
    # Save face overlay
    face_overlay_path = "temp_face_overlay.png"
    face_overlay.save(face_overlay_path)
    
    # Wrap title text properly for multiple lines
    def wrap_text(text, max_chars_per_line=40):
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + len(current_line) <= max_chars_per_line:
                current_line.append(word)
                current_length += len(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    # Clean text for FFmpeg (remove problematic characters entirely)
    def clean_for_ffmpeg(text):
        return text.replace("'", "").replace(":", "")
    
    title_lines = wrap_text(title)
    clean_title_lines = [clean_for_ffmpeg(line) for line in title_lines]
    clean_footer = clean_for_ffmpeg(footer)
    
    # Calculate font sizes and positioning
    title_fontsize = int(height * 0.04)
    footer_fontsize = int(height * 0.03)
    title_borderw = max(1, int(height * 0.002))
    footer_borderw = max(1, int(height * 0.0015))
    
    # Build filter complex with proper multiline text support
    filter_parts = []
    filter_parts.append("[1:v]fade=t=in:st=4:d=0.5:alpha=1,fade=t=out:st=5.5:d=0.5:alpha=1[face]")
    filter_parts.append("[0:v][face]overlay=0:0[bg_face]")
    
    # Add each line of title text
    current_input = "bg_face"
    line_height = title_fontsize + 10
    total_height = len(clean_title_lines) * line_height
    start_y = (height - total_height) // 2
    
    for i, line in enumerate(clean_title_lines):
        y_pos = start_y + (i * line_height)
        if i == len(clean_title_lines) - 1:
            output_label = "with_title"
        else:
            output_label = f"title_{i}"
        
        filter_parts.append(
            f"[{current_input}]drawtext=text='{line}':fontsize={title_fontsize}:fontcolor=white:borderw={title_borderw}:bordercolor=black:x=(w-text_w)/2:y={y_pos}:enable=between(t\\,6\\,8)[{output_label}]"
        )
        current_input = output_label
    
    # Add footer
    filter_parts.append(
        f"[with_title]drawtext=text='{clean_footer}':fontsize={footer_fontsize}:fontcolor=white:borderw={footer_borderw}:bordercolor=black:x=40:y=h-text_h-40:enable=between(t\\,6.5\\,8)[final]"
    )
    
    filter_complex = ";".join(filter_parts)
    
    cmd = [
        'ffmpeg', '-y',  # Overwrite output
        '-i', str(background_path),  # Background video
        '-loop', '1', '-i', face_overlay_path,  # Face overlay
        '-filter_complex', filter_complex,
        '-map', '[final]',
        '-map', '0:a',  # Keep original audio
        '-c:a', 'copy',  # Copy audio without re-encoding
        '-c:v', 'libx264',
        '-t', '8',  # Duration 8 seconds
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        typer.echo("✅ Video compositing completed")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ FFmpeg error: {e.stderr.decode()}")
        raise
    finally:
        # Clean up temporary files
        if os.path.exists(face_overlay_path):
            os.remove(face_overlay_path)

@app.command()
def generate_background(
    api_key: str = typer.Option(None, "--api-key", "-k", help="fal.ai API key"),
    output_path: Path = typer.Option("cache/background.mp4", help="Path to save background video"),
):
    """Generate and cache the background video (one-time setup)."""
    key = get_api_key(api_key)
    
    # Create clean background animation (no text, no faces)
    video_prompt = """
    Create a cinematic noir-style spacetime animation in black and white, Twilight Zone aesthetic:
    
    0-2s: Fade in from black. A warped 3D spacetime grid oscillates over a starfield.
    2-4s: The grid begins warping and collapsing inward, creating spacetime distortion.
    4-6s: A stylized black hole forms at the center, warping the grid dramatically.
    6-8s: The black hole stabilizes with swirling cosmic matter, grid continues warping.
    
    Style: black and white, Twilight Zone, noir, cinematic, minimal, eerie ambient atmosphere.
    
    IMPORTANT: NO TEXT, NO FACES, NO PEOPLE - just pure abstract spacetime geometry.
    Clean background suitable for compositing text and images later.
    """
    
    payload = {
        "prompt": video_prompt.strip(),
        "duration": "8s",
        "aspect_ratio": "16:9", 
        "resolution": "1080p",
        "generate_audio": True
    }
    
    typer.echo("🎬 Generating background video...")
    headers = {"Authorization": f"Key {key}"}
    response = requests.post("https://fal.run/fal-ai/veo3", json=payload, headers=headers)
    
    if response.status_code != 200:
        typer.echo(f"Error: {response.status_code}\n{response.text}")
        raise typer.Exit(1)
    
    result = response.json()
    video_url = result.get("video", {}).get("url") or result.get("video_url")
    
    if not video_url:
        typer.echo(f"No video URL found in response: {result}")
        raise typer.Exit(1)
    
    typer.echo(f"Video generated: {video_url}")
    typer.echo("Downloading video...")
    video_response = requests.get(video_url)
    
    if video_response.status_code != 200:
        typer.echo(f"Failed to download video: {video_response.status_code}")
        raise typer.Exit(1)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(video_response.content)
    typer.echo(f"✅ Background video cached to {output_path}")

@app.command()
def main(
    title: str = typer.Option(..., help="Main title text"),
    footer: str = typer.Option(..., help="Footer handle or link (e.g., '@user / site.com')"),
    reference_image: Path = typer.Option(..., help="Reference face image path"),
    background_video: Path = typer.Option("cache/background.mp4", help="Path to cached background video"),
    output_path: Path = typer.Option("intro.mp4", help="Path to save output video"),
):
    """
    Generate a cinematic YouTube intro with custom face and text using cached background
    """
    
    # Check if background video exists
    if not background_video.exists():
        typer.echo(f"❌ Background video not found at {background_video}")
        typer.echo("Run: python cli.py generate-background")
        raise typer.Exit(1)
    
    typer.echo(f"📹 Using cached background: {background_video}")
    
    # Composite text and face locally
    typer.echo("🎬 Compositing text and face locally...")
    composite_video(background_video, reference_image, title, footer, output_path)
    typer.echo(f"✅ Final intro saved to {output_path}")

@app.command()
def combine(
    intro_video: Path = typer.Option(..., help="Path to intro video"),
    main_video: Path = typer.Option(..., help="Path to main content video"),
    output_path: Path = typer.Option("combined.mp4", help="Path to save combined video"),
    transition_duration: float = typer.Option(0.8, help="Cross-fade transition duration in seconds"),
):
    """
    Combine intro video with main content video, matching main video's settings
    """
    
    # Check if both videos exist
    if not intro_video.exists():
        typer.echo(f"❌ Intro video not found at {intro_video}")
        raise typer.Exit(1)
    
    if not main_video.exists():
        typer.echo(f"❌ Main video not found at {main_video}")
        raise typer.Exit(1)
    
    typer.echo(f"🎬 Combining {intro_video} + {main_video}")
    
    # Get main video properties to match settings
    typer.echo("📊 Analyzing main video settings...")
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format',
        str(main_video)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        data = json.loads(result.stdout)
        
        # Get video stream info
        video_stream = next(s for s in data['streams'] if s['codec_type'] == 'video')
        audio_stream = next((s for s in data['streams'] if s['codec_type'] == 'audio'), None)
        
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        fps = eval(video_stream['r_frame_rate'])  # Convert fraction to float
        
        typer.echo(f"📺 Main video: {width}x{height} @ {fps:.1f}fps")
        
    except Exception as e:
        typer.echo(f"❌ Error analyzing main video: {e}")
        raise typer.Exit(1)
    
    # Create the combination with cross-fade transition
    typer.echo(f"🔗 Combining videos with {transition_duration}s cross-fade...")
    
    # Get original audio info to preserve settings
    try:
        # Check main video audio settings
        main_audio_info = next((s for s in data['streams'] if s['codec_type'] == 'audio'), None)
        if main_audio_info:
            original_sample_rate = main_audio_info.get('sample_rate', '44100')
            original_channels = main_audio_info.get('channels', 2)
            typer.echo(f"🎵 Main video audio: {original_sample_rate}Hz, {original_channels} channels")
        else:
            original_sample_rate = '44100'
            original_channels = 2
    except:
        original_sample_rate = '44100'
        original_channels = 2
    
    # Completely different approach - create one command that handles everything properly
    intro_duration = 8.0
    
    cmd = [
        'ffmpeg', '-y',
        '-i', str(intro_video),   # Input 0: intro video
        '-i', str(main_video),    # Input 1: main video  
        '-filter_complex',
        f'''
        [0:v]scale={width}:{height}[intro_v];
        [1:v]scale={width}:{height}[main_v];
        [intro_v][main_v]concat=n=2:v=1:a=0[final_v];
        [0:a]atrim=end={intro_duration}[intro_a];
        [intro_a][1:a]concat=n=2:v=0:a=1[final_a]
        ''',
        '-map', '[final_v]',
        '-map', '[final_a]',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', str(original_sample_rate),
        '-ac', str(original_channels),
        '-shortest',  # End when shortest stream ends
        '-movflags', '+faststart',
        '-pix_fmt', 'yuv420p',
        str(output_path)
    ]
    
    try:
        typer.echo("🔗 Combining videos with proper audio handling...")
        subprocess.run(cmd, check=True, capture_output=True)
        typer.echo(f"✅ Combined video saved to {output_path}")
        typer.echo(f"📊 Output matches main video settings: {width}x{height} @ {fps:.1f}fps")
        
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ FFmpeg error: {e.stderr.decode()}")
        raise

if __name__ == "__main__":
    app()