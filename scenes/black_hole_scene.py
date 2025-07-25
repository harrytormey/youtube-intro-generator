from manim import *

class HowBlackHolesWorkScene(Scene):
    def construct(self):
        # Title
        title = Text("How Black Holes Work", font_size=48)
        title.to_edge(UP)
        
        # Create spacetime grid
        grid = NumberPlane(
            x_range=(-6, 6, 1),
            y_range=(-4, 4, 1),
            background_line_style={
                "stroke_color": BLUE,
                "stroke_width": 2,
                "stroke_opacity": 0.6
            }
        )
        
        # Black hole (circle)
        black_hole = Circle(radius=0.8, color=BLACK, fill_opacity=1.0)
        black_hole.set_stroke(WHITE, width=3)
        
        # Event horizon
        event_horizon = Circle(radius=1.2, color=YELLOW, fill_opacity=0)
        event_horizon.set_stroke(YELLOW, width=2)
        
        # Spacetime warping animation
        def warp_grid(mob, alpha):
            # Simple warping effect - compress grid lines near center
            for line in mob.background_lines:
                # Get distance from center
                center = line.get_center()
                distance = np.linalg.norm(center)
                
                # Apply warping based on distance
                if distance > 0:
                    warp_factor = 1 / (1 + alpha * 2 / (distance + 0.1))
                    line.scale(warp_factor, about_point=ORIGIN)
        
        # Animations
        self.play(Create(grid), run_time=2)
        self.play(Write(title), run_time=1)
        self.wait(0.5)
        
        # Show black hole formation
        self.play(Create(black_hole), Create(event_horizon), run_time=2)
        
        # Warp spacetime
        self.play(
            UpdateFromAlphaFunc(grid, warp_grid),
            run_time=3,
            rate_func=smooth
        )
        
        # Add some particles being pulled in
        particles = VGroup()
        for i in range(8):
            particle = Dot(radius=0.05, color=WHITE)
            angle = i * PI / 4
            particle.move_to(2.5 * np.array([np.cos(angle), np.sin(angle), 0]))
            particles.add(particle)
        
        self.play(Create(particles), run_time=1)
        
        # Animate particles spiraling into black hole
        for particle in particles:
            start_pos = particle.get_center()
            self.play(
                particle.animate.move_to(black_hole.get_center()).scale(0),
                run_time=2,
                rate_func=rush_into
            )
        
        self.wait(2)