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
            
    def setup_view(self, display):
        camX = self.radius * math.cos(self.angleX)
        camY = self.radius * math.sin(self.angleY) * 0.5
        camZ = self.radius * math.sin(self.angleX)
        gluLookAt(camX, camY, camZ, 0, 0, 0, 0, 1, 0)