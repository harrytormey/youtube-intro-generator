from manim import *
from pathlib import Path

class CompositeIntro(Scene):
    def construct(self):
        """Show how to composite the generated elements."""
        
        # Instructions for user
        title = Text("YouTube Intro Composition", font_size=36, color=WHITE)
        title.to_edge(UP)
        
        instructions = VGroup(
            Text("Your generated components:", font_size=24, color=YELLOW),
            Text("1. output/background.mp4 - Clean spacetime animation", font_size=18, color=WHITE),
            Text("2. output/text_overlay.png - Title and code text", font_size=18, color=WHITE), 
            Text("3. output/face_overlay.png - Space scene template", font_size=18, color=WHITE),
            Text("4. Your face-swapped version (manual step)", font_size=18, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        
        instructions.move_to(ORIGIN + UP)
        
        composition_steps = VGroup(
            Text("Composition steps:", font_size=24, color=YELLOW),
            Text("1. Layer background.mp4 as base", font_size=18, color=WHITE),
            Text("2. Add face overlay at 3-7 seconds", font_size=18, color=WHITE),
            Text("3. Add text overlay with timing:", font_size=18, color=WHITE),
            Text("   • Code text: 2-3s", font_size=16, color=GRAY),
            Text("   • Title + footer: 7-8s", font_size=16, color=GRAY),
            Text("4. Export as final intro video", font_size=18, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        
        composition_steps.move_to(ORIGIN + DOWN*1.5)
        
        # Animation
        self.play(Write(title))
        self.wait(1)
        self.play(FadeIn(instructions), run_time=2)
        self.wait(2)
        self.play(FadeIn(composition_steps), run_time=2)
        self.wait(3)
        
        # Show a simple timeline
        timeline = Rectangle(width=10, height=0.5, color=WHITE)
        timeline.move_to(ORIGIN + DOWN*3)
        
        markers = VGroup()
        labels = VGroup()
        
        # Timeline markers
        for i, (time, label, color) in enumerate([
            (0, "0s", WHITE),
            (2.5, "2s: Code", YELLOW), 
            (4, "4s: Face", GREEN),
            (7.5, "7s: Title", BLUE),
            (10, "8s", WHITE)
        ]):
            x_pos = timeline.get_left()[0] + (time/8) * timeline.width
            marker = Line(
                start=[x_pos, timeline.get_top()[1], 0],
                end=[x_pos, timeline.get_bottom()[1] - 0.2, 0],
                color=color
            )
            text = Text(label, font_size=12, color=color)
            text.next_to(marker, DOWN, buff=0.1)
            
            markers.add(marker)
            labels.add(text)
        
        self.play(Create(timeline))
        self.play(Create(markers), Write(labels))
        
        self.wait(3)