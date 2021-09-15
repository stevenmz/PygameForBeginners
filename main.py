import pygame
import os

import RgbColors
from game_objs import (
    Canvas,
    DrawableObject,
    RedSpaceship,
    YellowSpaceship,
    Line,
    RedHealth,
    YellowHealth,
)
from collision_manager import find_collisions
import events

pygame.init()


class SpaceshipGame:
    def __init__(self, fps=60, width=900, height=500, caption="First Game"):
        super().__init__()

        # How many frames per second to update the window (Frames per second)
        self.fps = fps
        self.width = width
        self.height = height
        self.caption = caption

        self.background_color = RgbColors.WHITE

        self.CLOCK = pygame.time.Clock()

        self.game_objects = []

        rs = RedSpaceship(
            300,
            100,
            55,
            40,
            os.path.join("Assets", "spaceship_red.png"),
            [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s],
        )
        ys = YellowSpaceship(
            700,
            100,
            55,
            40,
            os.path.join("Assets", "spaceship_yellow.png"),
            [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN],
        )
        border = Line(width / 2 - 5, 0, 10, height, RgbColors.BLACK)

        self.game_objects.append(
            Canvas(0, 0, width, height, os.path.join("Assets", "space.png"))
        )
        self.game_objects.append(border)
        self.game_objects.append(rs)
        self.game_objects.append(ys)
        self.game_objects.append(
            RedHealth(0, 0, 0, 30, os.path.join("Assets", "QuirkyRobot.ttf"))
        )
        self.game_objects.append(
            YellowHealth(width, 0, 0, 30, os.path.join("Assets", "QuirkyRobot.ttf"))
        )

    def run(self):
        self.WIN = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.caption)

        run = True

        while run:
            # Make sure our event loop runs at FPS
            self.CLOCK.tick(self.fps)

            for event in pygame.event.get():
                print(event)
                if event.type == pygame.QUIT:
                    run = False
                elif (
                    event.type == events.EVENT_BULLET_OFFSCREEN
                    or event.type == events.EVENT_SPACESHIP_HIT
                ):
                    if event.obj in self.game_objects:
                        self.game_objects.remove(event.obj)

                for obj in self.game_objects:
                    vals = obj.process_event(event)

                    # Any new trackable objects the result of a key press should now be tracked.
                    for val in vals:
                        if isinstance(val, DrawableObject):
                            self.game_objects.append(val)

            for obj in self.game_objects:
                obj.process_keys_pressed(pygame.key.get_pressed())

            find_collisions(self.game_objects)

            self.draw_window()

        pygame.display.quit()
        pygame.quit()
        exit()

    def draw_window(self):
        for obj in self.game_objects:
            obj.draw(self.WIN)

        pygame.display.update()


if __name__ == "__main__":
    SpaceshipGame().run()
