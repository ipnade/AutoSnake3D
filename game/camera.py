import math
from OpenGL.GLU import gluLookAt

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

class Camera:
    def __init__(self, config):
        self.config = config
        # Use yaw for horizontal rotation and pitch for vertical, so that
        # vertical dragging doesn't invert direction unexpectedly.
        self.yaw = 0.0   # full 360° rotation allowed
        self.pitch = 0.0 # clamped to avoid flipping
        # Distance from the origin (center of rotation)
        self.radius = config['camera'].get('distance', 100)
        self.rotation_velocity_yaw = 0.0
        self.rotation_velocity_pitch = 0.0
        self.friction = 0.95
        # Add time tracking for smooth pitch oscillation
        self.time = 0.0
        # Add a pitch oscillation speed parameter
        self.pitch_speed = 0.001  # Reduced from 0.01 for slower oscillation

    def update(self):
        # Apply momentum if available; otherwise, auto-spin.
        if abs(self.rotation_velocity_yaw) > 0.001 or abs(self.rotation_velocity_pitch) > 0.001:
            self.yaw = (self.yaw + self.rotation_velocity_yaw) % (2 * math.pi)
            # Clamp pitch between -90° and +90° to maintain consistent vertical dragging.
            self.pitch = clamp(self.pitch + self.rotation_velocity_pitch, -math.pi/2, math.pi/2)
            self.rotation_velocity_yaw *= self.friction
            self.rotation_velocity_pitch *= self.friction
        else:
            self.auto_spin()

    def get_position(self):
        # Calculate the camera position using yaw and pitch.
        camX = self.radius * math.cos(self.pitch) * math.sin(self.yaw)
        camY = self.radius * math.sin(self.pitch)
        camZ = self.radius * math.cos(self.pitch) * math.cos(self.yaw)
        return (camX, camY, camZ)

    def manual_rotate(self, dx, dy):
        """Rotate camera based on mouse movement.
           Horizontal drag rotates the camera around the y axis (yaw),
           while vertical drag adjusts the pitch and is clamped.
        """
        sensitivity = 0.005
        delta_yaw = -dx * sensitivity
        delta_pitch = dy * sensitivity

        self.yaw = (self.yaw + delta_yaw) % (2 * math.pi)
        self.pitch = clamp(self.pitch + delta_pitch, -math.pi/2, math.pi/2)

        # Store momentum.
        self.rotation_velocity_yaw = delta_yaw
        self.rotation_velocity_pitch = delta_pitch

    def auto_spin(self):
        if not self.config['camera']['auto_rotate']:
            return
            
        # Update yaw rotation as before
        spin_speed_yaw = self.config['camera']['rotation_speed']['x']
        self.yaw = (self.yaw + spin_speed_yaw) % (2 * math.pi)
        
        # Use slower time increment for pitch oscillation
        self.time += self.pitch_speed
        amplitude = self.config['camera']['y_amplitude']
        target_pitch = math.sin(self.time) * amplitude
        
        # Smoothly interpolate current pitch to target pitch
        self.pitch = self.pitch * 0.95 + target_pitch * 0.05

    def setup_view(self, display):
        camX, camY, camZ = self.get_position()
        gluLookAt(camX, camY, camZ, 0, 0, 0, 0, 1, 0)