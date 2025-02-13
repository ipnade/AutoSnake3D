import imgui
from imgui.integrations.pygame import PygameRenderer


class UISystem:
    def __init__(self, config, display):
        self.config = config
        self.display = display
        
        # Initialize ImGui
        imgui.create_context()
        self.io = imgui.get_io()
        self.io.display_size = display
        
        # Initialize ImGui Pygame renderer
        self.renderer = PygameRenderer()
        
        # Style configuration
        style = imgui.get_style()
        style.window_rounding = 6.0
        style.frame_rounding = 4.0
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.15, 0.15, 0.15, 0.95)
        style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.2, 0.2, 0.2, 1.0)
    
    def get_display_speed(self):
        """Convert internal speed (50-10) to display speed (1-10)"""
        return int(((50 - self.config['snake']['speed']) / 4.4) + 1)
        
    def handle_event(self, event):
        self.renderer.process_event(event)
        
    def update(self):
        imgui.new_frame()
        
        # Create settings window with fixed position
        window_flags = (
            imgui.WINDOW_NO_MOVE |          # Prevent window movement
            imgui.WINDOW_NO_RESIZE          # Prevent window resizing
        )
        
        # Position at top right
        imgui.set_next_window_position(
            self.display[0] - 280,  # 280px width
            0,                      # 0px from top
            condition=imgui.ALWAYS  # Force position every frame
        )
        imgui.set_next_window_size(280, 400, condition=imgui.ONCE)  # ONCE allows collapse
        imgui.set_next_window_collapsed(True, condition=imgui.ONCE)  # Start collapsed
        
        imgui.begin("Settings", flags=window_flags)
        
        # Particles Settings
        expanded, visible = imgui.collapsing_header("Particles")
        if expanded:
            changed, self.config['particles']['enabled'] = imgui.checkbox(
                "Enabled", 
                self.config['particles']['enabled']
            )
            
            if self.config['particles']['enabled']:
                changed, value = imgui.slider_int(
                    "Particle Count",
                    self.config['particles']['count'],
                    self.config['particles']['min_count'],
                    self.config['particles']['max_count']
                )
                if changed:
                    self.config['particles']['count'] = value
                    
        # Snake Settings
        expanded, visible = imgui.collapsing_header("Snake")
        if expanded:
            changed, self.config['snake']['colors']['grayscale'] = imgui.checkbox(
                "Grayscale Mode", 
                self.config['snake']['colors']['grayscale']
            )
            
            # Use converted display speed for the slider
            changed, value = imgui.slider_int(
                "Snake Speed",
                self.get_display_speed(),
                1, 10  # 1 = slowest, 10 = fastest
            )
            if changed:
                # Convert back to internal speed
                self.config['snake']['speed'] = int(50 - (value - 1) * 4.4)
            
        imgui.end()
        
    def render(self):
        # Render ImGui
        imgui.render()
        self.renderer.render(imgui.get_draw_data())
        
    def shutdown(self):
        self.renderer.shutdown()