import random
from enum import Flag

# See https://raw.githubusercontent.com/pybox2d/pybox2d/master/library/Box2D/examples/simple/simple_01.py
import pygame
import Box2D
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE, K_a, K_d, K_w, K_s, KEYUP, K_SPACE, K_RETURN)

from model import *
from settings import *

# Box2D deals with meters, but we want to display pixels, so define a
# conversion factor (pixels per meter)
PPM = 20.0

# Pygame
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS

# Create the world
world = Box2D.b2World(gravity=(0, -10), doSleep=True)


game_objects = [
    StaticLine(world, (10, 10), (SCREEN_WIDTH - 10, 10), colour=(255, 150, 100, 255)),
    StaticLine(world, (SCREEN_WIDTH - 10, 10), (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10), colour=(255, 150, 100, 255)),
    StaticLine(world, (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10), (10, SCREEN_HEIGHT - 10), colour=(255, 150, 100, 255)),
    StaticLine(world, (10, SCREEN_HEIGHT - 10), (10, 10), colour=(255, 150, 100, 255))
]
for _ in range(500):
    SnowCircles = game_objects.append(DynamicCircle(world, (random.randint(100, 500), 20), 10, CollisionInfo(1,1,1), (255,255,255,255)))

# region Collision Groups

class CollisionGroup(Flag):
    NoCollision = 0
    Default = auto()
    SecondGroup = auto()
    ThirdGroup = auto()

    @classmethod
    def ALL(cls):
        # From https://stackoverflow.com/a/78229655
        return ~CollisionGroup(0)

for game_obj in game_objects:
    game_obj.set_collision_group(CollisionGroup.Default, CollisionGroup.ALL())



# endregion


def main():
    timer = TARGET_FPS * 5

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pygame.display.set_caption("Simple pygame example")
    clock = pygame.time.Clock()
    
    
    io = KeyQuery()
    shape_registry = ShapeRegistry(world)
    shape_registry.add(game_objects)
    
    running = True
    print("To Play: \n Controls: D = Pop Snowball, Enter = Start Game")
    start_game = False
    while running:
        io.clear_pressed()
        io.mark_mouse_relative(pygame.mouse.get_rel())
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
                break
        
            if event.type == KEYDOWN:
                io.mark_pressed(event.key)
            elif event.type == KEYUP:
                io.mark_released(event.key)


        left_right = int(io.is_key_down(K_d)) - int(io.is_key_down(K_a))
        up_down    = int(io.is_key_down(K_s)) - int(io.is_key_down(K_w))
        
        mouse_relo = (
            io.get_mouse_relative()[0] * TARGET_FPS,
            io.get_mouse_relative()[1] * TARGET_FPS,
        )

        if io.is_key_pressed(K_RETURN):
            start_game = True

        if start_game:
            if len(shape_registry.shapes) == 4:
                print("You Live!")
            else:
                timer -= 1
                
            if timer % 1 == 0:
                print(timer)

            if timer == 0:
                running = False
                print("You Die")
        
            if io.is_key_pressed(K_d) and len(shape_registry.shapes) > 4:
                print("Delete")
                shape_registry.delete(game_objects.pop())


        screen.fill((0, 0, 0, 0))
        shape_registry.draw_shapes(screen)

        # Make Box2D simulate the physics of our world for one step.
        # Instruct the world to perform a single step of simulation. It is
        # generally best to keep the time step and iterations fixed.
        # See the manual (Section "Simulating the World") for further discussion
        # on these parameters and their implications.
        world.Step(TIME_STEP, 10, 10)

        for contact in world.contacts:
            contact: Box2D.b2Contact
            if not contact.touching:
                continue

            shape_a: Shape = contact.fixtureA.userData
            shape_b: Shape = contact.fixtureB.userData

        # Flip the screen and try to keep at the target FPS
        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()
    print('Done!')


if __name__ == "__main__":
    main()
