import os
import typer
import requests
import base64
from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv()
app = typer.Typer()

def get_api_key(api_key: str = None):
    return api_key or os.getenv("FAL_API_KEY") or typer.BadParameter("Missing API key")

def encode_image(image_path: Path) -> str:
    """Encode image to base64 string."""
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

def call_fal_api(endpoint: str, payload: dict, key: str) -> dict:
    """Make API call to fal.ai endpoint."""
    headers = {"Authorization": f"Key {key}"}
    response = requests.post(f"https://fal.run/{endpoint}", json=payload, headers=headers)
    
    if response.status_code != 200:
        typer.echo(f"Error calling {endpoint}: {response.status_code}\n{response.text}")
        raise typer.Exit(1)
    
    return response.json()

def download_file(url: str, output_path: Path) -> None:
    """Download file from URL to output path."""
    response = requests.get(url)
    if response.status_code != 200:
        typer.echo(f"Failed to download from {url}: {response.status_code}")
        raise typer.Exit(1)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)

@app.command()
def generate_background(
    title: str = typer.Option(..., help="Main title text"),
    footer: str = typer.Option(..., help="Footer handle or link"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="fal.ai API key"),
    output_path: Path = typer.Option("output/background.mp4", help="Path to save background video"),
):
    """Step 1: Generate background video without face."""
    key = get_api_key(api_key)
    
    video_prompt = f"""
    Create a cinematic noir-style YouTube intro sequence in black and white, Twilight Zone aesthetic:
    
    0-2s: Fade in from black. A warped 3D spacetime grid oscillates over a starfield.
    2-3s: Code text appears clearly: "simulate_spacetime_geometry(mass=1.5e30)"
    3-5s: The grid begins collapsing inward, forming a stylized black hole with swirling matter.
    5-7s: The black hole grows larger, warping space around it dramatically.
    7-8s: Clear title text appears: "{title}". Bottom-left footer: "{footer}"
    
    Style: black and white, Twilight Zone, noir, cinematic, minimal, eerie ambient atmosphere.
    No faces, no people, just abstract space and text elements.
    """
    
    payload = {
        "prompt": video_prompt.strip(),
        "duration": "8s",
        "aspect_ratio": "16:9",
        "resolution": "720p",
        "generate_audio": True
    }
    
    typer.echo("🎬 Generating background video...")
    result = call_fal_api("fal-ai/veo3", payload, key)
    
    video_url = result.get("video", {}).get("url") or result.get("video_url")
    if not video_url:
        typer.echo(f"No video URL in response: {result}")
        raise typer.Exit(1)
    
    download_file(video_url, output_path)
    typer.echo(f"✅ Background video saved to {output_path}")

@app.command()
def create_text_overlay(
    title: str = typer.Option(..., help="Main title text"),
    footer: str = typer.Option(..., help="Footer handle or link"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="fal.ai API key"),
    output_path: Path = typer.Option("output/text_overlay.png", help="Path to save text overlay"),
):
    """Step 2: Create accurate text overlay using Recraft V3."""
    key = get_api_key(api_key)
    
    text_prompt = f"""
    Create a clean text overlay for a YouTube intro on transparent background:
    
    Main title (large, bold, cinematic font): "{title}"
    Footer text (smaller, bottom-left): "{footer}"
    
    Style: Modern, readable, high contrast white text with subtle shadow.
    Background: Transparent or black.
    Layout: Title centered, footer bottom-left corner.
    Typography: Clean, professional, sci-fi inspired.
    """
    
    payload = {
        "prompt": text_prompt.strip(),
        "image_size": "landscape_16_9",
        "style": "digital_illustration"
    }
    
    typer.echo("📝 Generating text overlay with Recraft 20b...")
    result = call_fal_api("fal-ai/recraft-20b", payload, key)
    
    image_url = result.get("images")[0]["url"] if result.get("images") else None
    if not image_url:
        typer.echo(f"No image URL in response: {result}")
        raise typer.Exit(1)
    
    download_file(image_url, output_path)
    typer.echo(f"✅ Text overlay saved to {output_path}")

@app.command()
def create_face_overlay(
    reference_image: Path = typer.Option(..., help="Your reference face image"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="fal.ai API key"),
    output_path: Path = typer.Option("output/face_overlay.png", help="Path to save face overlay"),
):
    """Step 3: Create face overlay from your reference image (simplified version)."""
    key = get_api_key(api_key)
    
    # Create a space scene with face placeholder
    scene_prompt = f"""
    Create a dramatic space scene for a YouTube intro in black and white:
    
    A mysterious human face emerging from a swirling black hole with cosmic matter.
    The face should be clearly visible, well-lit, and positioned in the center.
    Background: Warped spacetime grid, swirling cosmic matter, starfield.
    Style: Black and white, noir, cinematic, dramatic lighting on the face.
    High contrast, professional lighting, clear facial features.
    """
    
    typer.echo("🌌 Creating space scene with face...")
    
    scene_payload = {
        "prompt": scene_prompt.strip(),
        "image_size": "landscape_16_9", 
        "style": "realistic_image"
    }
    
    scene_result = call_fal_api("fal-ai/recraft-20b", scene_payload, key)
    scene_url = scene_result.get("images")[0]["url"]
    
    if not scene_url:
        typer.echo(f"No scene URL in response: {scene_result}")
        raise typer.Exit(1)
    
    download_file(scene_url, output_path)
    typer.echo(f"✅ Space scene saved to {output_path}")
    typer.echo(f"📋 Manual step: Use photo editing software to replace the AI face with your reference image from {reference_image}")
    typer.echo("   Recommended tools: Photoshop, GIMP, or online face swap tools like remaker.ai")
    typer.echo("   Or run: python cli_v2.py external-face-swap to get links to working face swap tools")

@app.command()
def external_face_swap():
    """Get links to working external face swap tools."""
    typer.echo("🔗 Working Face Swap Tools (2025):")
    typer.echo("")
    typer.echo("1. 🆓 Remaker.ai Face Swap - https://remaker.ai/face-swap")
    typer.echo("   • Free online tool")
    typer.echo("   • High quality results") 
    typer.echo("   • No watermark")
    typer.echo("")
    typer.echo("2. 🆓 Vidwud - https://vidwud.com")
    typer.echo("   • Free for photos and videos")
    typer.echo("   • 1080p video support")
    typer.echo("   • No watermark")
    typer.echo("")
    typer.echo("3. 🆓 SwapAnything.io - https://swapanything.io")
    typer.echo("   • Face and outfit swapping")
    typer.echo("   • Photos, GIFs, and videos")
    typer.echo("   • Intuitive interface")
    typer.echo("")
    typer.echo("4. 💰 BasedLabs.ai - https://basedlabs.ai")
    typer.echo("   • Professional quality")
    typer.echo("   • Uncensored models")
    typer.echo("   • Image upscaling included")
    typer.echo("")
    typer.echo("📋 Instructions:")
    typer.echo("1. Upload your generated space scene: output/face_overlay.png")
    typer.echo("2. Upload your reference image: assets/harry_thumbnail.png") 
    typer.echo("3. Download the result and save as output/face_swapped.png")

@app.command()
def full_process(
    title: str = typer.Option(..., help="Main title text"),
    footer: str = typer.Option(..., help="Footer handle or link"),
    reference_image: Path = typer.Option(..., help="Your reference face image"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="fal.ai API key"),
    output_dir: Path = typer.Option("output", help="Directory for all outputs"),
):
    """Complete process: Generate all components for a professional intro."""
    typer.echo("🚀 Starting full YouTube intro generation process...")
    
    # Step 1: Background video
    background_path = output_dir / "background.mp4"
    typer.echo("\n📽️ Step 1: Generating background video...")
    generate_background(title, footer, api_key, background_path)
    
    # Step 2: Text overlay
    text_path = output_dir / "text_overlay.png"
    typer.echo("\n📝 Step 2: Creating text overlay...")
    create_text_overlay(title, footer, api_key, text_path)
    
    # Step 3: Face overlay
    face_path = output_dir / "face_overlay.png"
    typer.echo("\n🎭 Step 3: Creating face overlay...")
    create_face_overlay(reference_image, api_key, face_path)
    
    typer.echo(f"\n✅ All components generated in {output_dir}/")
    typer.echo("\n📋 Next steps:")
    typer.echo("1. Use video editing software (Final Cut, Premiere, DaVinci) to composite:")
    typer.echo(f"   - Background: {background_path}")
    typer.echo(f"   - Face overlay: {face_path}")
    typer.echo(f"   - Text overlay: {text_path}")
    typer.echo("\n2. Or use the Manim scene for programmatic composition:")
    typer.echo("   python -m manim -pql scenes/composite_scene.py CompositeIntro")

if __name__ == "__main__":
    app()