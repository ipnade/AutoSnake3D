import imgui
from imgui.integrations.pygame import PygameRenderer


class UISystem:
    def __init__(self, config, display):
        self.config = config
        self.display = display
        self.window_visible = False
        
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
        
        self.window_width = 340  # Increase from 320 to 340 for better text visibility
    
    def get_display_speed(self):
        """Convert internal speed (100=slow, 1=fast) to a display slider value (1-100)."""
        # When internal speed is 100, display value is 1; when speed is 1, display value is 100.
        return 101 - self.config['snake']['speed']
        
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
            self.display[0] - self.window_width,  # Use window_width instead of 280
            0,                      # 0px from top
            condition=imgui.ALWAYS  # Force position every frame
        )
        imgui.set_next_window_size(self.window_width, 400, condition=imgui.ONCE)  # ONCE allows collapse
        
        # Begin the window and store its visibility state
        expanded, visible = imgui.begin("Settings", flags=window_flags)
        self.window_visible = visible and not imgui.is_window_collapsed()
        
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
            changed, display_value = imgui.slider_int(
                "Snake Speed",
                self.get_display_speed(),
                1, 100  # 1 = slowest, 100 = fastest
            )
            if changed:
                # Convert display value back into internal speed:
                self.config['snake']['speed'] = 101 - display_value

        # Camera Settings
        expanded, visible = imgui.collapsing_header("Camera")
        if expanded:
            changed, self.config['camera']['auto_rotate'] = imgui.checkbox(
                "Auto Rotation", 
                self.config['camera']['auto_rotate']
            )
            
            changed, value = imgui.slider_float(
                "Rotation Speed",
                self.config['camera']['rotation_speed']['multiplier'],
                0.1, 2.0,
                format="%.1fx"
            )
            if changed:
                self.config['camera']['rotation_speed']['multiplier'] = value
                # Update actual rotation speeds
                base_x = 0.002
                base_y = 0.001
                self.config['camera']['rotation_speed']['x'] = base_x * value
                self.config['camera']['rotation_speed']['y'] = base_y * value
            
        imgui.end()
        
    def render(self):
        # Render ImGui
        imgui.render()
        self.renderer.render(imgui.get_draw_data())
        
    def shutdown(self):
        self.renderer.shutdown()
        
    def get_settings_bounds(self):
        """Return the current bounds of the settings window."""
        if not self.window_visible:
            # Return empty bounds when window is collapsed
            return {
                'x': 0,
                'y': 0,
                'width': 0,
                'height': 0
            }
        return {
            'x': self.display[0] - self.window_width,  # Use window_width 
            'y': 0,
            'width': self.window_width,  # Use window_width
            'height': 400
        }