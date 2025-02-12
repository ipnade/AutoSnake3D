import random
import math
from snake import Snake
from particle_system import ParticleSystem

class GameState:
    def __init__(self, config):
        self.config = config
        self.snake = Snake()
        self.food = self.spawn_food(self.snake.body)
        self.game_speed = 25
        self.last_move_time = 0
        self.food_bob_time = 0
        self.particle_system = ParticleSystem()
        
    def spawn_food(self, snake_body):
        while True:
            x = random.randint(-24, 24)
            y = random.randint(-24, 24)
            z = random.randint(-24, 24)
            if (x, y, z) not in snake_body:
                return (x, y, z)
    
    def get_next_move(self):
        head = self.snake.body[0]
        current_direction = self.snake.direction
        
        food_direction = (
            self.food[0] - head[0],
            self.food[1] - head[1],
            self.food[2] - head[2]
        )
        
        new_pos = (
            head[0] + current_direction[0],
            head[1] + current_direction[1],
            head[2] + current_direction[2]
        )
        
        if (abs(new_pos[0]) <= 24 and abs(new_pos[1]) <= 24 and 
            abs(new_pos[2]) <= 24 and new_pos not in self.snake.body):
            current_distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(new_pos, self.food)))
            head_distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(head, self.food)))
            if current_distance < head_distance:
                return current_direction
        
        abs_food_dir = [abs(x) for x in food_direction]
        primary_axis = abs_food_dir.index(max(abs_food_dir))
        possible_moves = []
        
        if food_direction[primary_axis] > 0:
            possible_moves.append(tuple(1 if i == primary_axis else 0 for i in range(3)))
        else:
            possible_moves.append(tuple(-1 if i == primary_axis else 0 for i in range(3)))
        
        for axis in range(3):
            if axis != primary_axis:
                for direction in [1, -1]:
                    move = tuple(direction if i == axis else 0 for i in range(3))
                    if move not in possible_moves:
                        possible_moves.append(move)
        
        opposite_move = tuple(-x for x in current_direction)
        if opposite_move in possible_moves:
            possible_moves.remove(opposite_move)
        
        for move in possible_moves:
            new_pos = tuple(head[i] + move[i] for i in range(3))
            
            if (abs(new_pos[0]) <= 24 and abs(new_pos[1]) <= 24 and 
                abs(new_pos[2]) <= 24 and new_pos not in self.snake.body):
                return move
        
        return current_direction

    def update(self, current_time):
        if current_time - self.last_move_time >= self.game_speed:
            next_move = self.get_next_move()
            self.snake.move(next_move)
            
            if self.snake.body[0] == self.food:
                self.snake.grow = True
                self.particle_system.emit_particles(
                    position=self.food,
                    count=30,
                    color=(1.0, 0.0, 0.0)
                )
                self.food = self.spawn_food(self.snake.body)
            
            if self.snake.check_collision():
                return False
                
            self.last_move_time = current_time
            
        self.food_bob_time += 0.1
        
        if self.config['particles']['enabled']:
            self.particle_system.update(1.0/self.config['display']['fps'])
        
        return True

    def get_food_position(self):
        bob_offset = math.sin(self.food_bob_time) * 0.5
        return (self.food[0], self.food[1] + bob_offset, self.food[2])