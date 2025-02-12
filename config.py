config = {
    # Display settings
    'display': {
        'width': 1600,
        'height': 900,
        'fps': 30,
        'vsync': True,
    },
    
    # Camera settings
    'camera': {
        'fov': 45,
        'near_plane': 0.1,
        'far_plane': 500.0,
        'distance': 100,
        'rotation_speed': {
            'x': 0.002,
            'y': 0.001
        },
        'y_amplitude': 0.5  # How much the camera moves up/down
    },
    
    # Snake settings
    'snake': {
        'initial_length': 1,
        'speed': 25,  # Lower = faster
        'colors': {
            'head': (1.0, 0.843, 0.0),  # Golden yellow
            'body_pattern': [
                (0.0, 0.5, 0.0),  # Dark green
                (0.2, 0.8, 0.2),  # Light green
                (0.4, 0.7, 0.0)   # Yellow-green
            ]
        },
        'size': {
            'head': 1.0,
            'body': 0.95
        },
        'z_fighting_offset': 0.02  # Offset to prevent z-fighting
    },
    
    # Food settings
    'food': {
        'color': (1.0, 0.0, 0.0),
        'size': 0.8,
        'bob_speed': 0.1,
        'bob_amplitude': 0.5
    },
    
    # Particle settings
    'particles': {
        'enabled': True,
        'count': 30,
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
    
    # Grid settings
    'grid': {
        'size': 25,
        'color': (0.2, 0.2, 0.2),
        'enabled': True
    },
    
    # Game space settings
    'gameplay': {
        'boundary': 24,  # Maximum coordinate value for snake movement
        'reset_on_collision': True
    },
    
    # Visual effects
    'effects': {
        'gradient_fade': True,  # Snake color gradient
        'smooth_camera': True,
    }
}