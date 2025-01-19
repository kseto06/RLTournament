import pymunk
import pygame
import gymnasium as gym
import random
import sys
from pymunk.pygame_util import DrawOptions

width = 600
height = 600

class GameObject:
    # ACTUAL IMAGE RENDERING: 
    def __init__(self, x: int, y: int, dir_name: str, screen: pygame.display):
        self.x = x
        self.y = y
        self.hitboxes = []
        self.image = pygame.image.load(dir_name)
        self.image_width, self.image_height = self.image.get_size()
        self.image_x = (x + self.image_width//1.5)
        self.image_y = (y + self.image_height//1.5) #Centered
        self.screen = screen

    def update_pos(self, x: int, y: int):
        self.x = x
        self.y = y
        self.image_x = (x + self.image_width//2) - 10
        self.image_y = (y + self.image_height//2) - 10#Centered

    # GAME OBJECT HITBOXES

    def add_hitbox(self, x: int, y: int, width: int, height: int):
        '''
        Append a new hitbox to the GameObject's collection of hitboxes
        '''
        self.hitboxes.append(Hitbox(x, y, width, height, self.screen))

    def draw_object(self):
        self.screen.blit(self.image, (self.image_x, self.image_y))

class Sword(GameObject):
    '''
    Sword (png) object. Extends game object
    '''
    def __init__(self, x: int, y: int, dir_name: str, screen):
        super().__init__(x, y, dir_name, screen)
        self.x = x
        self.y = y

    def construct_hitboxes(self):
        # Construct multiple hitboxes based on their (x, y) coordinates
        # NOTE: Change this for different types of game objects
        hitbox_points = [
            ((self.x + self.image_width//2) - 10, self.y), #initial (x, y)
            ((self.x+self.image_width) - 10, self.y),
            ((self.x+3*self.image_width//2) - 10, self.y)
        ]

        # Add hitboxes to the space using the hitbox_points
        L = len(hitbox_points)
        for i in range(L - 1):
            x1, y1 = hitbox_points[i][0], hitbox_points[i][1]
            x2, y2 = hitbox_points[i+1][0], hitbox_points[i+1][1]
            width = self.image_width // (L-1)
            height = self.image_height
            x = min(x1, x2)  # Determine the x-coordinate of the hitbox
            y = min(y1, y2)  # Determine the y-coordinate of the hitbox
            self.add_hitbox(x, y, width, height) 

    def update_hitbox_pos(self, x, y):
        self.x = x
        self.y = y
        self.construct_hitboxes()

    # TODO: Powercast a simple sword move, logic to make it appear/disappear
    def dash_attack():
        pass

class Throw(GameObject):
    pass

class Hammer(GameObject):
    pass

'''
TODO: Add more object/action classes here as needed
'''

@DeprecationWarning #Initial 3b1b ball. Use the new cube object
class Ball:
    def __init__(self, position, space, mass, collision_type, width=50, height=10):
        self.mass = mass
        self.width = width
        self.height = height
        self.shape = pymunk.Poly.create_box(None, size=(width, height))
        self.moment = pymunk.moment_for_poly(self.mass, self.shape.get_vertices())
        self.body = pymunk.Body(self.mass, self.moment)
        self.shape.body = self.body
        leg1 = pymunk.Segment(self.body, (-20, 30), (-10, 0), 3)  # 2
        leg2 = pymunk.Segment(self.body, (20, 30), (10, 0), 3)
        self.shape.collision_type = collision_type
        self.shape.body.position = position
        space.add(self.shape, self.body, leg1, leg2)

class Ground:
    def __init__(self, space, x, y, width_ground):
        self.body = pymunk.Body(x, y, body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Poly.create_box(self.body, (width_ground, 10))
        self.shape.body.position = (x + width_ground // 2, y)
        self.shape.friction = 0.7
        space.add(self.shape, self.body)

class Cube:
    def __init__(self, position, space, mass, collision_type, width=50, height=10):
        self.mass = mass
        self.width = width
        self.height = height

        self.shape = pymunk.Poly.create_box(None, size=(width, height))
        self.moment = pymunk.moment_for_poly(self.mass, self.shape.get_vertices())
        self.body = pymunk.Body(self.mass, self.moment)
        self.shape.body = self.body
        
        self.shape.collision_type = collision_type
        self.shape.body.position = position
        space.add(self.shape, self.body)

    def get_bounding_box(self) -> pymunk.Shape.cache_bb:
        return self.shape.cache_bb()
    
class Hitbox: 
    '''
    This class adds and renders a Hitbox to the game space.
    '''
    def __init__(self, x: int, y: int, width: int, height: int, screen: pygame.display):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen = screen
        self.hitbox_rect = pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, self.width, self.height), 1)
    
    def draw(self):
        # pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, self.width, self.height), 1)
        self.hitbox_rect.topleft = (self.x, self.y)

class HitboxHandler:
    '''
    This class handles the hitbox interactions between Pygame (GameObject) and Pymunk (agent) objects.
    '''
    def __init__(self, screen: pygame.display):
        self.screen = screen

    def object_hits_agent(self, game_obj: GameObject, agent: Cube) -> bool:
        game_obj_hitboxes = game_obj.hitboxes
        agent_bb = agent.get_bounding_box()

        # Bounding box rectangle for agent
        pygame.draw.rect(self.screen, (0, 255, 0), (int(agent_bb.left), int(agent_bb.bottom), int(agent_bb.right - agent_bb.left), int(agent_bb.top - agent_bb.bottom)), 1)
        
        for hitbox in game_obj_hitboxes:
            # Draw a rect for the game object
            game_obj_hitbox = pygame.draw.rect(self.screen, (255, 0, 0), (game_obj.x, game_obj.y, game_obj.image_width, game_obj.image_height), 1)

            # Check for overlap between a pygame.rect and pymunk bb
            if game_obj_hitbox.colliderect(agent_bb.left, agent_bb.bottom, agent_bb.right - agent_bb.left, agent_bb.top - agent_bb.bottom):
                print('hit')
                return True 

            return False

class Hurtbox:
    def hurtbox(self, body1: Cube, body2: Cube) -> bool:
        '''
        This function takes in two bodies and checks if their bounding boxes overlap 

        Inputs:
        body1 (Cube): first object
        body2 (Cube): second object
        '''

        # Get the bounding boxes of the bodies
        bb1 = body1.shape.cache_bb() 
        bb2 = body2.shape.cache_bb() 

        # Check for overlap
        return bb1.intersects(bb2)

def collide(arbiter, space, data):
    # print("Collision detected!")
    return True

# def hitbox(entity1: Ball, entity2: Ball):
#     if entity1.shape.body.position.x <= entity2.shape.body.position.x and entity1.shape.body.position.y <= entity2.shape.body.position.y <= entity1.shape.body.position.y + entity1.height:
#         if entity1.shape.body.position.x < entity2.shape.body.position.x and \
#             entity1.shape.body.position.x + entity1.width > entity2.shape.body.position.x:
#             print("Entity1 hit by Entity2 on the LEFT")
#             return True
#         elif entity2.shape.body.position.x < entity1.shape.body.position.x and \
#               entity2.shape.body.position.x + entity2.width > entity1.shape.body.position.x:
#             print("Entity1 hit by Entity2 on the RIGHT")
#             return True
#     return False

def display_video(width: int, height: int):
    import cv2
    import os
    import numpy as np
    import skvideo.io
    from IPython.display import Video

    frame_folder = "frames"
    frames = [os.path.join(frame_folder, f) for f in sorted(os.listdir(frame_folder)) if f.endswith(".png")]

    frame_array = []
    for frame_path in frames:
        img = cv2.imread(frame_path)
        if img is None:
            raise ValueError(f"Could not read frame: {frame_path}")
        frame_array.append(img)

    video_data = np.stack(frame_array, axis=0)
    skvideo.io.vwrite('output.mp4', video_data)
    Video('output.mp4', embed=True, width=width, height=height)

def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Env")
    clock = pygame.time.Clock()

    draw_options = DrawOptions(screen)

    space = pymunk.Space()
    space.gravity = 0, 200.0
    ground = Ground(space, 50, 500, 500)

    # Modify the placement of the platforms
    platform1 = Ground(space, 125, 400, 125)  # First platform
    platform2 = Ground(space, 350, 400, 125)  # Second platform with a gap

    # ball = Ball((150, 200), space, 200, 1)
    # ball2 = Ball((450, 100), space, 200, 1)

    ball = Cube((150, 100), space, 4, 1, width=50, height=50)
    sword = Sword(150, 100, "./assets/sword.png", screen)

    ball2 = Cube((450, 100), space, 3, 2, width=50, height=50)
    hurtbox = Hurtbox()

    hitbox_handler = HitboxHandler(screen)
    collision_handler = space.add_collision_handler(1, 2)
    collision_handler.begin = collide
    frame_count = 0

    # Define the y-coordinate threshold for quitting
    quit_y_threshold = 575

    def apply_force_toward_each_other(ball1, ball2, force_magnitude):
        # Calculate force directions
        direction1 = (1 if ball2.shape.body.position.x > ball1.shape.body.position.x else -1, 0)
        direction2 = (1 if ball1.shape.body.position.x > ball2.shape.body.position.x else -1, 0)

        # Apply forces
        ball1.shape.body.apply_force_at_local_point((force_magnitude * direction1[0], force_magnitude * direction1[1]), (0, 0))
        ball2.shape.body.apply_force_at_local_point((force_magnitude * direction2[0], force_magnitude * direction2[1]), (0, 0))

    for _ in range(1000):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit(0)

        hurtbox.hurtbox(ball, ball2)

        # Continuously move the balls toward each other
        apply_force_toward_each_other(ball, ball2, 50)

        # Quit if any ball goes below the threshold
        if ball.shape.body.position.y > quit_y_threshold or ball2.shape.body.position.y > quit_y_threshold:
            print("A ball has fallen below the threshold. Exiting...")
            sys.exit()

        screen.fill((0, 0, 0))

        # Draw GameObject & sword hitboxes:
        sword.update_pos(ball.shape.body.position.x, ball.shape.body.position.y)
        sword.update_hitbox_pos(ball.shape.body.position.x, ball.shape.body.position.y)
        for hitbox in sword.hitboxes:
            hitbox.draw()
        sword.draw_object()

        # Check if the GameObject hits Agent
        hitbox_handler.object_hits_agent(game_obj=sword, agent=ball2)

        # Draw the red line
        pygame.draw.line(screen, (255, 0, 0), (0, quit_y_threshold), (width, quit_y_threshold), 2)

        space.debug_draw(draw_options)
        space.step(1/50.0)
        pygame.display.update()
        clock.tick(50)
        # pygame.image.save(screen, f"frames/frame_{frame_count:04d}.png")
        frame_count += 1

if __name__ == '__main__':
    main()