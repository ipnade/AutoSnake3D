class Snake:
    def __init__(self):
        self.body = [(0, 0, 0)]  # Start at center
        self.direction = (1, 0, 0)  # Start moving in +x direction
        self.grow = False

    def move(self, new_direction=None):
        if new_direction:
            self.direction = new_direction
        
        new_head = (
            self.body[0][0] + self.direction[0],
            self.body[0][1] + self.direction[1],
            self.body[0][2] + self.direction[2]
        )
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        self.grow = False

    def check_collision(self):
        # Check wall collision
        x, y, z = self.body[0]
        if abs(x) > 25 or abs(y) > 25 or abs(z) > 25:
            return True
        # Check self collision
        return self.body[0] in self.body[1:]