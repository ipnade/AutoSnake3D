config = {
    # Display
    'display': {
        'width': 1600,
        'height': 900,
        'fps': 144,
        'vsync': True,
    },
    
    # Camera
    'camera': {
        'fov': 45,
        'near_plane': 0.1,
        'far_plane': 500.0,
        'distance': 100,
        'auto_rotate': True,
        'rotation_speed': {
            'x': 0.001,
            'y': 0.0005,
            'multiplier': 1.0
        },
        'y_amplitude': 0.5,
    },
    
    # Snake
    'snake': {
        'initial_length': 1,
        'speed': 25,
        'colors': {
            'custom_color': False,
            'primary_color': (0.0, 1.0, 0.0),
            'gradient_intensity': 0.5,
            'gamer_mode': False,
            'default_colors': {
                'head': (1.0, 0.843, 0.0),
                'body_pattern': [
                    (0.0, 0.5, 0.0),
                    (0.2, 0.8, 0.2),
                    (0.4, 0.7, 0.0)
                ]
            },
            'head': (1.0, 0.843, 0.0),
            'body_pattern': [
                (0.0, 0.5, 0.0),
                (0.2, 0.8, 0.2),
                (0.4, 0.7, 0.0)
            ]
        },
        'size': {
            'head': 1.0,
            'body': 0.95
        },
        'z_fighting_offset': 0.02
    },
    
    # Food
    'food': {
        'color': (1.0, 0.0, 0.0),
        'size': 0.8,
        'bob_speed': 0.05,
        'bob_amplitude': 0.2
    },
    
    # Particles
    'particles': {
        'enabled': True,
        'count': 30,
        'min_count': 10,
        'max_count': 100,
        'lifetime': {
            'min': 0.5,
            'max': 2.0
        },
        'speed': {
            'min': 5,
            'max': 15
        },
        'color_variation': 0.2,
        'size': 2.0
    },
    
    # Grid
    'grid': {
        'size': 25,
        'color': (0.2, 0.2, 0.2),
        'enabled': True
    },
    
    # Gameplay
    'gameplay': {
        'boundary': 24,
        'reset_on_collision': True
    },
    
    # Effects
    'effects': {
        'gradient_fade': True,
        'smooth_camera': True,
    }
}