import random
import math
from snake import Snake
from particle_system import ParticleSystem

class GameState:
    def __init__(self, config):
        self.config = config
        self.reset()
        
    def reset(self):
        self.snake = Snake()
        self.food = self.spawn_food(self.snake.body)
        self.game_speed = self.config['snake']['speed']
        self.last_move_time = 0
        self.food_bob_time = 0
        self.particle_system = ParticleSystem()
        self.dying = False
        self.death_animation_segment = 0
        self.last_death_effect = 0
        self.death_complete = False
        self.death_complete_time = 0
        self.death_speed = 250
        self.food_collected = False
        self.last_food_pos = None
        
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
        # Update game speed from config in case it changed
        self.game_speed = self.config['snake']['speed']
        
        # Update particles regardless of game state
        if self.config['particles']['enabled']:
            self.particle_system.update(1.0/self.config['display']['fps'])

        if self.dying:
            if current_time - self.last_death_effect >= self.death_speed:
                if self.death_animation_segment < len(self.snake.body):
                    if self.config['particles']['enabled']:
                        segment_index = len(self.snake.body) - 1 - self.death_animation_segment
                        
                        # Get the same color as the snake segment
                        if self.config['snake']['colors']['custom_color']:
                            r, g, b = self.config['snake']['colors']['primary_color']
                            intensity = self.config['snake']['colors']['gradient_intensity']
                            fade = 1.0 - (segment_index/len(self.snake.body)) * intensity
                            color = [max(0.0, min(1.0, c * fade)) for c in (r, g, b)]
                        else:
                            if segment_index == 0:
                                color = self.config['snake']['colors']['default_colors']['head']
                            else:
                                pattern = self.config['snake']['colors']['default_colors']['body_pattern']
                                color = pattern[segment_index % len(pattern)]

                        for _ in range(self.config['particles']['count']):
                            velocity = [
                                random.uniform(-15, 15),
                                random.uniform(5, 20),
                                random.uniform(-15, 15)
                            ]
                            self.particle_system.emit_particle(
                                position=self.snake.body[segment_index],
                                velocity=velocity,
                                color=color,
                                lifetime=random.uniform(0.5, 1.5)
                            )
                    
                    # Progress death animation regardless of particles
                    self.death_speed = max(50, 500 - (self.death_animation_segment * 25))
                    self.death_animation_segment += 1
                    self.last_death_effect = current_time
                elif not self.death_complete:
                    self.death_complete = True
                    self.death_complete_time = current_time
                elif current_time - self.death_complete_time >= 3000:  # 3 second wait
                    self.reset()
                    return True
            return True

        # Original update logic for live snake
        if current_time - self.last_move_time >= self.game_speed:
            next_move = self.get_next_move()
            self.snake.move(next_move)
            
            if self.snake.body[0] == self.food:
                # Store food position before spawning new food
                if self.config['particles']['enabled']:
                    self.last_food_pos = self.food
                    self.food_collected = True
                self.snake.grow = True
                self.food = self.spawn_food(self.snake.body)
            
            if self.snake.check_collision():
                self.dying = True
                return True
                
            self.last_move_time = current_time
            
        # Update food bobbing using config speed
        self.food_bob_time += self.config['food']['bob_speed']
        
        return True

    def get_food_position(self):
        bob_speed = self.config['food']['bob_speed']
        bob_amplitude = self.config['food']['bob_amplitude']
        bob_offset = math.sin(self.food_bob_time) * bob_amplitude
        return (self.food[0], self.food[1] + bob_offset, self.food[2])

    def get_visible_segments(self):
        if not self.dying:
            return self.snake.body
        # Return all segments except the ones that have been destroyed
        return self.snake.body[:(len(self.snake.body) - self.death_animation_segment)]

def draw(self):
    if self.config['particles']['enabled']:
        self.particle_system.draw()
        if self.food_collected:
            self.particle_system.emit_particles(
                position=self.last_food_pos, 
                color=[1.0, 0.0, 0.0],
                count=self.config['particles']['count']
            )
            self.food_collected = False