import imgui
from imgui.integrations.pygame import PygameRenderer


class UISystem:
    def __init__(self, config, display):
        self.config = config
        self.display = display
        self.window_visible = False
        
        # ImGui setup
        imgui.create_context()
        self.io = imgui.get_io()
        self.io.display_size = display
        self.renderer = PygameRenderer()
        
        # UI styling
        style = imgui.get_style()
        style.window_rounding = 6.0
        style.frame_rounding = 4.0
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.15, 0.15, 0.15, 0.95)
        style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.2, 0.2, 0.2, 1.0)
        
        self.window_width = 360
    
    def get_display_speed(self):
        """Convert speed value for UI display (100=slow, 1=fast to 1-100 scale)"""
        return 101 - self.config['snake']['speed']
        
    def handle_event(self, event):
        self.renderer.process_event(event)
        
    def update(self, game_state):
        imgui.new_frame()
        
        # Settings window configuration
        window_flags = (
            imgui.WINDOW_NO_MOVE |
            imgui.WINDOW_ALWAYS_AUTO_RESIZE
        )
        
        # Position window at top right
        imgui.set_next_window_position(
            self.display[0] - self.window_width,
            0,
            condition=imgui.ALWAYS
        )
        
        # Window setup
        imgui.set_next_window_collapsed(True, condition=imgui.ONCE)
        imgui.set_next_window_size(self.window_width, 400, condition=imgui.ONCE)
        imgui.set_next_window_size_constraints(
            (self.window_width, 0),
            (self.window_width, 10000)
        )
        
        expanded, visible = imgui.begin("Settings", flags=window_flags)
        self.window_visible = visible and not imgui.is_window_collapsed()
        
        # Particle settings section
        expanded, visible = imgui.collapsing_header("Particles")
        if expanded:
            changed, enabled = imgui.checkbox(
                "Enabled [P]", 
                self.config['particles']['enabled']
            )
            if changed:
                self.config['particles']['enabled'] = enabled
                if not enabled:
                    game_state.particle_system.clear_particles()
            
            if self.config['particles']['enabled']:
                changed, value = imgui.slider_int(
                    "Particle Count",
                    self.config['particles']['count'],
                    self.config['particles']['min_count'],
                    self.config['particles']['max_count']
                )
                if changed:
                    self.config['particles']['count'] = value
                    
        # Snake settings section
        expanded, visible = imgui.collapsing_header("Snake")
        if expanded:
            changed, self.config['snake']['colors']['gamer_mode'] = imgui.checkbox(
                "Gamer Mode", 
                self.config['snake']['colors']['gamer_mode']
            )
            
            # Only show custom color options if gamer mode is off
            if not self.config['snake']['colors']['gamer_mode']:
                changed, self.config['snake']['colors']['custom_color'] = imgui.checkbox(
                    "Custom Color", 
                    self.config['snake']['colors']['custom_color']
                )
                
                if self.config['snake']['colors']['custom_color']:
                    r, g, b = self.config['snake']['colors']['primary_color']
                    changed, color = imgui.color_edit3(
                        "Snake Color",
                        r, g, b,
                        flags=imgui.COLOR_EDIT_PICKER_HUE_WHEEL
                    )
                    
                    if changed:
                        self.config['snake']['colors']['primary_color'] = tuple(
                            max(0.0, min(1.0, c)) for c in color
                        )
                        
                    changed, value = imgui.slider_float(
                        "Gradient Intensity",
                        self.config['snake']['colors']['gradient_intensity'],
                        0.0, 1.0,
                        format="%.2f"
                    )
                    if changed:
                        self.config['snake']['colors']['gradient_intensity'] = value
            
            changed, display_value = imgui.slider_int(
                "Snake Speed",
                self.get_display_speed(),
                1, 100
            )
            if changed:
                self.config['snake']['speed'] = 101 - display_value

        # Camera settings section
        expanded, visible = imgui.collapsing_header("Camera")
        if expanded:
            changed, self.config['camera']['auto_rotate'] = imgui.checkbox(
                "Auto Rotation [C]", 
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
                base_x, base_y = 0.002, 0.001
                self.config['camera']['rotation_speed']['x'] = base_x * value
                self.config['camera']['rotation_speed']['y'] = base_y * value
            
        imgui.end()
        
    def render(self):
        imgui.render()
        self.renderer.render(imgui.get_draw_data())
        
    def shutdown(self):
        self.renderer.shutdown()
        
    def get_settings_bounds(self):
        """Return the current bounds of the settings window"""
        if not self.window_visible:
            return {
                'x': self.display[0] - self.window_width,
                'y': 0,
                'width': self.window_width,
                'height': 20  # Collapsed header height
            }
        return {
            'x': self.display[0] - self.window_width,
            'y': 0,
            'width': self.window_width,
            'height': 400
        }