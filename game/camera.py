import math
from OpenGL.GLU import gluLookAt

class Camera:
    def __init__(self, config):
        self.config = config
        self.angleX = 0
        self.angleY = 0
        self.radius = 100
        
    def update(self):
        if self.config['effects']['smooth_camera']:
            self.angleX += self.config['camera']['rotation_speed']['x']
            self.angleY += self.config['camera']['rotation_speed']['y']
    
    def get_position(self):
        camX = self.radius * math.cos(self.angleX)
        camY = self.radius * math.sin(self.angleY) * 0.5
        camZ = self.radius * math.sin(self.angleX)
        return (camX, camY, camZ)
    
    def manual_rotate(self, dx, dy):
        """Adjust camera rotation based on mouse movement deltas."""
        # Sensitivity factor to scale the mouse delta to an appropriate rotation speed
        sensitivity = 0.005  
        self.angleX += dx * sensitivity
        self.angleY += dy * sensitivity

    def auto_spin(self):
        """Default auto-spin behavior."""
        self.angleX += self.config['camera']['rotation_speed']['x']
        self.angleY += self.config['camera']['rotation_speed']['y']
            
    def setup_view(self, display):
        camX = self.radius * math.cos(self.angleX)
        camY = self.radius * math.sin(self.angleY) * 0.5
        camZ = self.radius * math.sin(self.angleX)
        gluLookAt(camX, camY, camZ, 0, 0, 0, 0, 1, 0)