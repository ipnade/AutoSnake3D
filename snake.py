class Snake:
    """Represents the snake entity and handles its movement and collision detection"""
    
    def __init__(self):
        self.body = [(0, 0, 0)]  # Start at origin
        self.direction = (1, 0, 0)  # Initial direction: +x axis
        self.grow = False
        
    def move(self, new_direction=None):
        """Move the snake in the current or new direction
        
        Args:
            new_direction (tuple, optional): New direction as (x, y, z)
        """
        if new_direction:
            self.direction = new_direction
        
        # Calculate new head position
        new_head = tuple(
            current + direction 
            for current, direction in zip(self.body[0], self.direction)
        )
        
        # Update body
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        self.grow = False

    def check_collision(self):
        """Check for collisions with walls and self
        
        Returns:
            bool: True if collision detected, False otherwise
        """
        head_x, head_y, head_z = self.body[0]
        
        # Check wall boundaries
        if any(abs(coord) > 25 for coord in (head_x, head_y, head_z)):
            return True
            
        # Check self-collision
        return self.body[0] in self.body[1:]