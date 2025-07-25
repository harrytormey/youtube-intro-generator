import os
import typer
import requests
import base64
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
app = typer.Typer()

def get_api_key(api_key: str = None):
    return api_key or os.getenv("FAL_API_KEY") or typer.BadParameter("Missing API key")

@app.command()
def main(
    title: str = typer.Option(..., help="Main title text"),
    footer: str = typer.Option(..., help="Footer handle or link (e.g., '@user / site.com')"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="fal.ai API key"),
    duration: int = typer.Option(8, help="Video duration in seconds (only 8s supported)"),
    output_path: Path = typer.Option("intro.mp4", help="Path to save output video"),
):
    """
    Generate a cinematic YouTube intro with custom face and text
    """
    key = get_api_key(api_key)

    # Create the video prompt description
    video_prompt = f"""
    Create a cinematic noir-style YouTube intro sequence in black and white, Twilight Zone aesthetic:
    
    0-2s: Fade in from black. A warped 3D spacetime grid oscillates over a starfield.
    2-3s: Code text appears: "simulate_spacetime_geometry(mass=1.5e30)"
    3-5s: The grid begins collapsing inward, forming a stylized black hole.
    5-7s: A grayscale face emerges from the black hole, over the flattening grid.
    7-8s: Title text appears: "{title}". Bottom-left footer: "{footer}"
    
    Style: black and white, Twilight Zone, noir, cinematic, minimal, eerie ambient atmosphere.
    """

    # Prepare the API request
    payload = {
        "prompt": video_prompt.strip(),
        "duration": "8s",
        "aspect_ratio": "16:9",
        "resolution": "720p",
        "generate_audio": True
    }

    headers = {"Authorization": f"Key {key}"}
    response = requests.post(
        "https://fal.run/fal-ai/veo3",
        json=payload,
        headers=headers
    )

    if response.status_code != 200:
        typer.echo(f"Error: {response.status_code}\n{response.text}")
        raise typer.Exit(1)

    result = response.json()
    typer.echo(f"API Response: {result}")
    
    # Extract video URL from response
    video_url = result.get("video", {}).get("url") or result.get("video_url")
    
    if not video_url:
        typer.echo(f"No video URL found in response: {result}")
        raise typer.Exit(1)
    
    typer.echo(f"Video generated: {video_url}")

    # Download the video
    typer.echo("Downloading video...")
    video_response = requests.get(video_url)
    if video_response.status_code != 200:
        typer.echo(f"Failed to download video: {video_response.status_code}")
        raise typer.Exit(1)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(video_response.content)
    typer.echo(f"Saved video to {output_path}")

if __name__ == "__main__":
    app()