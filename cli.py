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
        # Try to use a nice font - EVEN BIGGER text
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", int(height * 0.16))  # Even bigger
        footer_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", int(height * 0.08))  # Even bigger
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
    
    # Draw text with stroke (outline) - bigger stroke for larger text
    stroke_width = 5
    
    # Draw title with stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((title_x + dx, title_y + dy), title, font=title_font, fill=(0, 0, 0, 255))
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255, 255))
    
    # Draw footer with stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((footer_x + dx, footer_y + dy), footer, font=footer_font, fill=(0, 0, 0, 255))
    draw.text((footer_x, footer_y), footer, font=footer_font, fill=(255, 255, 255, 255))
    
    img.save(output_path)

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
    
    # More aggressive background removal for light backgrounds
    # Check for very light pixels (white/very light gray)
    very_light_mask = (img_array[:, :, 0] > 240) & (img_array[:, :, 1] > 240) & (img_array[:, :, 2] > 240)
    
    # Check for light gray backgrounds
    light_mask = (img_array[:, :, 0] > 200) & (img_array[:, :, 1] > 200) & (img_array[:, :, 2] > 200)
    
    # Check for medium gray backgrounds  
    medium_gray_mask = (
        (img_array[:, :, 0] > 180) & (img_array[:, :, 0] < 220) &
        (img_array[:, :, 1] > 180) & (img_array[:, :, 1] < 220) &
        (img_array[:, :, 2] > 180) & (img_array[:, :, 2] < 220)
    )
    
    # Combine all background masks
    background_mask = very_light_mask | light_mask | medium_gray_mask
    
    # Apply a small blur to the mask to smooth edges
    from scipy import ndimage
    background_mask = ndimage.binary_dilation(background_mask, iterations=1)
    
    # Make background transparent
    img_array[background_mask, 3] = 0  # Set alpha to 0 for background
    
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
    
    # Save processed images
    face_overlay_path = "temp_face_overlay.png"
    text_overlay_path = "temp_text_overlay.png"
    
    face_overlay.save(face_overlay_path)
    create_text_overlay(width, height, title, footer, text_overlay_path)
    
    # Use ffmpeg to composite everything
    cmd = [
        'ffmpeg', '-y',  # Overwrite output
        '-i', str(background_path),  # Background video
        '-loop', '1', '-i', face_overlay_path,  # Face overlay
        '-loop', '1', '-i', text_overlay_path,  # Text overlay
        '-filter_complex',
        f"""
        [1:v]fade=t=in:st=4:d=0.5:alpha=1,fade=t=out:st=5.5:d=0.5:alpha=1[face];
        [2:v]fade=t=in:st=6:d=0.3:alpha=1[text];
        [0:v][face]overlay=0:0[bg_face];
        [bg_face][text]overlay=0:0[final]
        """,
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
        for temp_file in [face_overlay_path, text_overlay_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

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

if __name__ == "__main__":
    app()