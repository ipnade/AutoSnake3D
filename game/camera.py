import math
from OpenGL.GLU import gluLookAt

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

class Camera:
    def __init__(self, config):
        self.config = config
        # Camera angles
        self.yaw = 0.0     # Horizontal rotation (0-360°)
        self.pitch = 0.0   # Vertical rotation (±90°)
        self.radius = config['camera'].get('distance', 100)
        
        # Movement physics
        self.rotation_velocity_yaw = 0.0
        self.rotation_velocity_pitch = 0.0
        self.friction = 0.95
        
        # Auto rotation
        self.time = 0.0
        self.pitch_speed = 0.001
        self.disable_auto_spin = False

    def update(self):
        if self._has_momentum():
            self._apply_momentum()
        elif not self.disable_auto_spin:
            self.auto_spin()

    def _has_momentum(self):
        return (abs(self.rotation_velocity_yaw) > 0.001 or 
                abs(self.rotation_velocity_pitch) > 0.001)

    def _apply_momentum(self):
        self.yaw = (self.yaw + self.rotation_velocity_yaw) % (2 * math.pi)
        self.pitch = clamp(self.pitch + self.rotation_velocity_pitch, -math.pi/2, math.pi/2)
        self.rotation_velocity_yaw *= self.friction
        self.rotation_velocity_pitch *= self.friction

    def get_position(self):
        camX = self.radius * math.cos(self.pitch) * math.sin(self.yaw)
        camY = self.radius * math.sin(self.pitch)
        camZ = self.radius * math.cos(self.pitch) * math.cos(self.yaw)
        return (camX, camY, camZ)

    def manual_rotate(self, dx, dy):
        """Rotate camera based on mouse movement"""
        sensitivity = 0.005
        delta_yaw = -dx * sensitivity
        delta_pitch = dy * sensitivity

        self.yaw = (self.yaw + delta_yaw) % (2 * math.pi)
        self.pitch = clamp(self.pitch + delta_pitch, -math.pi/2, math.pi/2)

        self.rotation_velocity_yaw = delta_yaw
        self.rotation_velocity_pitch = delta_pitch

    def auto_spin(self):
        if not self.config['camera']['auto_rotate']:
            return
            
        # Update horizontal rotation
        spin_speed_yaw = self.config['camera']['rotation_speed']['x']
        self.yaw = (self.yaw + spin_speed_yaw) % (2 * math.pi)
        
        # Update vertical oscillation
        self.time += self.pitch_speed
        amplitude = self.config['camera']['y_amplitude']
        target_pitch = math.sin(self.time) * amplitude
        self.pitch = self.pitch * 0.95 + target_pitch * 0.05

    def setup_view(self, display):
        camX, camY, camZ = self.get_position()
        gluLookAt(camX, camY, camZ, 0, 0, 0, 0, 1, 0)