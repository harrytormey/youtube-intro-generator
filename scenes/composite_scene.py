from manim import *
import cv2
import numpy as np

class CompositeIntro(Scene):
    def construct(self):
        """Composite the generated elements into a final intro."""
        
        # Load the generated components (you'll need to update paths)
        background_video_path = "output/background.mp4"
        face_overlay_path = "output/face_overlay.png"
        text_overlay_path = "output/text_overlay.png"
        
        # Create placeholders if files don't exist
        try:
            # Background
            background = Rectangle(width=16, height=9, color=BLACK, fill_opacity=1)
            background.set_stroke(WHITE, width=1)
            
            # Face overlay (load from generated image)
            face_overlay = ImageMobject(face_overlay_path) if Path(face_overlay_path).exists() else Circle(color=WHITE)
            face_overlay.scale(0.5)
            face_overlay.move_to(ORIGIN)
            
            # Text overlay (load from generated image) 
            text_overlay = ImageMobject(text_overlay_path) if Path(text_overlay_path).exists() else Text("Generated Text", color=WHITE)
            text_overlay.scale(0.8)
            
            # Animation sequence
            self.add(background)
            
            # Fade in background
            self.play(FadeIn(background), run_time=1)
            self.wait(1)
            
            # Add spacetime grid effect
            grid = NumberPlane(
                x_range=(-8, 8, 1),
                y_range=(-4.5, 4.5, 1),
                background_line_style={
                    "stroke_color": BLUE,
                    "stroke_width": 1,
                    "stroke_opacity": 0.3
                }
            )
            
            self.play(Create(grid), run_time=2)
            
            # Warp the grid (black hole effect)
            def warp_function(point):
                x, y, z = point
                distance = np.sqrt(x**2 + y**2)
                if distance > 0:
                    warp_factor = 1 / (1 + distance/2)
                    return np.array([x * warp_factor, y * warp_factor, z])
                return point
            
            self.play(
                grid.animate.apply_function(warp_function),
                run_time=3,
                rate_func=smooth
            )
            
            # Add face emerging from center
            self.play(FadeIn(face_overlay), run_time=1.5)
            
            # Add text overlay
            self.play(Write(text_overlay), run_time=1.5)
            
            # Final hold
            self.wait(1)
            
        except Exception as e:
            # Fallback animation if files not found
            title = Text("YouTube Intro", font_size=48, color=WHITE)
            subtitle = Text("Generated with fal.ai", font_size=24, color=GRAY)
            subtitle.next_to(title, DOWN)
            
            self.play(Write(title), run_time=2)
            self.play(Write(subtitle), run_time=1)
            self.wait(2)