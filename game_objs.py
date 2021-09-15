import pygame
from pygame import font
import RgbColors
from typing import List, Tuple
import os
import events


class DrawableObject:
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__()

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, window):
        pass

    def process_event(self, event):
        """Not all drawable objects care about events so provide a default implementation"""
        return False, []

    def process_keys_pressed(self, keys):
        """Not all drawable objects care about key presses so provide a default implementation"""
        pass

    def get_bounding_rectangle(self):
        """Used for collision detection"""
        return self.rect

    def handle_collision(self, colliding_object):
        """Each object will handle this differently. Subclasses implement"""
        pass


class Canvas(DrawableObject):
    """
    First object to be drawn
    Serves as collision detection
    """

    def __init__(self, x, y, width, height, background_path):
        super().__init__(x, y, width, height)
        self.background = pygame.image.load(background_path)

    def draw(self, window):
        window.blit(self.background, (0, 0))

    def handle_collision(self, colliding_object):
        colliding_object_rect = colliding_object.get_bounding_rectangle()
        if isinstance(colliding_object, Bullet):
            exit_screen_left = colliding_object.get_bounding_rectangle().x <= 0
            exit_screen_right = (
                colliding_object_rect.x + colliding_object_rect.width >= self.rect.width
            )

            if exit_screen_left or exit_screen_right:
                ev = pygame.event.Event(
                    events.EVENT_BULLET_OFFSCREEN, obj=colliding_object
                )
                pygame.event.post(ev)


class Spaceship(DrawableObject):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        icon_path: str,
        movement_keys: List[int],
        max_bullets=3,
    ):
        super().__init__(x, y, width, height)

        self.icon_width, self.icon_height = width, height
        self.VEL = 5
        self.health_remaining = 10

        self.image: pygame.Surface = pygame.image.load(icon_path)
        self.image: pygame.Surface = pygame.transform.scale(
            self.image, (self.icon_width, self.icon_height)
        )

        self.left_key = movement_keys[0]
        self.right_key = movement_keys[1]
        self.up_key = movement_keys[2]
        self.down_key = movement_keys[3]

        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.max_bullets = max_bullets
        self.bullets_remaining = self.max_bullets
        self.my_fired_bullets = []

        # Sounds
        self.bullet_sound = pygame.mixer.Sound(
            os.path.join("Assets", "spaceship_fired.mp3")
        )
        self.spaceshit_hit_sound = pygame.mixer.Sound(
            os.path.join("Assets", "spaceship_hit.mp3")
        )

    def draw(self, window: pygame.Surface):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def process_event(self, event) -> Tuple[bool, List[DrawableObject]]:
        new_game_objs = []

        if (
            event.type == events.EVENT_BULLET_OFFSCREEN
            or event.type == events.EVENT_SPACESHIP_HIT
        ):
            bullet = event.obj
            if bullet in self.my_fired_bullets:
                self.my_fired_bullets.remove(event.obj)
                self.bullets_remaining += 1

        return new_game_objs

    def process_keys_pressed(self, keys):
        if keys[self.left_key]:  # Left
            self.rect.x -= self.VEL
        if keys[self.right_key]:  # Right
            self.rect.x += self.VEL
        if keys[self.up_key]:  # Up
            self.rect.y -= self.VEL
        if keys[self.down_key]:  # Down
            self.rect.y += self.VEL

    def handle_collision(self, colliding_object):
        if isinstance(colliding_object, Line):
            print("Spaceship collided with Line")
            # We hit the middle border, move back from where we were
            if self.rect.x <= colliding_object.get_bounding_rectangle().x:
                print("left to right")
                # We are overlapping from left to right
                self.rect.x = self.rect.x - self.VEL
            else:
                # We are overlapping from right to left
                print("Right to left")
                self.rect.x = self.rect.x + self.VEL
        elif isinstance(colliding_object, Canvas):
            # Did we go off the left right top or bottom?
            canvas_rect = colliding_object.get_bounding_rectangle()
            if self.rect.x <= canvas_rect.x:
                # Went off the left
                self.rect.x += self.VEL
            elif self.rect.x + self.rect.width >= canvas_rect.width:
                # Went off the right boundary
                self.rect.x -= self.VEL
            elif self.rect.y <= canvas_rect.y:
                # Went off the top of the booundary
                self.rect.y += self.VEL
            elif self.rect.y + self.rect.height + 15 >= canvas_rect.height:
                # Went off the bottom of the canvas
                self.rect.y -= self.VEL
        elif isinstance(colliding_object, Bullet):
            pygame.mixer.Sound.play(self.spaceshit_hit_sound)
            self.health_remaining -= 1
            if self.health_remaining <= 0:
                dead_event = pygame.event.Event(
                    events.EVENT_SPACESHIP_DESTROYED, obj=self
                )
                pygame.event.post(dead_event)
            spaceship_hit_event = pygame.event.Event(
                events.EVENT_SPACESHIP_HIT, obj=colliding_object, ship=self
            )
            pygame.event.post(spaceship_hit_event)


class RedSpaceship(Spaceship):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        icon_path: str,
        movement_keys: List[int],
        max_bullets=3,
    ):
        super().__init__(
            x, y, width, height, icon_path, movement_keys, max_bullets=max_bullets
        )
        self.rotation_angle = 90
        self.image = pygame.transform.rotate(self.image, self.rotation_angle)

    def process_event(self, event) -> Tuple[bool, List[DrawableObject]]:
        new_objs = super().process_event(event)
        new_game_objs = []
        new_game_objs.extend(new_objs)

        if event.type == pygame.KEYDOWN:
            print("process_event", event)
            if event.key == pygame.K_LCTRL and self.bullets_remaining > 0:
                bullet = Bullet(
                    self.rect.x + self.rect.width + 2,
                    self.rect.y + self.rect.height // 2,
                    10,
                    5,
                    5,
                    RgbColors.RED,
                )
                self.bullets_remaining -= 1
                new_game_objs.append(bullet)
                self.my_fired_bullets.append(bullet)

                pygame.mixer.Sound.play(self.bullet_sound)

        return new_game_objs


class YellowSpaceship(Spaceship):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        icon_path: str,
        movement_keys: List[int],
        max_bullets=3,
    ):
        super().__init__(x, y, width, height, icon_path, movement_keys, max_bullets)
        self.rotation_angle = 270
        self.image = pygame.transform.rotate(self.image, self.rotation_angle)

    def process_event(self, event) -> Tuple[bool, List[DrawableObject]]:
        new_objs = super().process_event(event)
        new_game_objs = []
        new_game_objs.extend(new_objs)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RCTRL and self.bullets_remaining > 0:
                bullet = Bullet(
                    self.rect.x - self.rect.width - 2,
                    self.rect.y + self.rect.height // 2,
                    10,
                    5,
                    -5,
                    RgbColors.YELLOW,
                )
                self.bullets_remaining -= 1
                new_game_objs.append(bullet)
                self.my_fired_bullets.append(bullet)

                pygame.mixer.Sound.play(self.bullet_sound)

        return new_game_objs


class Bullet(DrawableObject):
    def __init__(self, x: int, y: int, width: int, height: int, velocity: int, color):
        super().__init__(x, y, width, height)
        self.velocity = velocity
        self.color = color
        print(self)

    def draw(self, window):
        self.rect.x += self.velocity
        pygame.draw.rect(window, self.color, self.rect)


class Line(DrawableObject):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height)

        self.color = color
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, window: pygame.Surface):
        pygame.draw.rect(window, self.color, self.rect)


class RedHealth(DrawableObject):
    def __init__(self, x: int, y: int, width: int, height: int, font_path):
        super().__init__(x, y, width, height)
        self.font = pygame.font.Font(font_path, self.height)
        self.health_remaining = "Full"

    def process_event(self, event) -> Tuple[bool, List[DrawableObject]]:
        if event.type == events.EVENT_SPACESHIP_HIT:
            ship = event.ship
            if isinstance(ship, RedSpaceship):
                self.health_remaining = ship.health_remaining

        return []

    def draw(self, window):
        super().draw(window)
        health_indicator = self.font.render(
            f"Health: {self.health_remaining}", True, RgbColors.RED
        )
        window.blit(health_indicator, (self.x, self.y))


class YellowHealth(DrawableObject):
    def __init__(self, x: int, y: int, width: int, height: int, font_path):
        super().__init__(x, y, width, height)
        self.font = pygame.font.Font(font_path, self.height)
        self.health_remaining = "Full"
        self.x -= self.font.size("Health: XX")[0] + 5

    def process_event(self, event) -> Tuple[bool, List[DrawableObject]]:
        if event.type == events.EVENT_SPACESHIP_HIT:
            ship = event.ship
            if isinstance(ship, YellowSpaceship):
                self.health_remaining = ship.health_remaining

        return []

    def draw(self, window):
        super().draw(window)
        health_indicator = self.font.render(
            f"Health: {self.health_remaining}", True, RgbColors.YELLOW
        )
        window.blit(health_indicator, (self.x, self.y))


class WinnerMessage(DrawableObject):
    def __init__(self, x: int, y: int, width: int, height: int, font_path):
        super().__init__(x, y, width, height)
        self.font = pygame.font.Font(font_path, 150)
        self.winner_selected = False

    def process_event(self, event) -> Tuple[bool, List[DrawableObject]]:
        if event.type == events.EVENT_SPACESHIP_DESTROYED:
            winner = "Red" if isinstance(event.obj, YellowSpaceship) else "Yellow"
            self.winning_str = f"{winner} Wins!!!"
            self.winner_selected = True

            pygame.event.set_blocked(None)
            pygame.event.set_allowed(pygame.QUIT)

        return []

    def draw(self, window):
        super().draw(window)
        if self.winner_selected:
            text_width, text_height = self.font.size(self.winning_str)

            color = RgbColors.YELLOW if "Yellow" in self.winning_str else RgbColors.RED

            text_surface = self.font.render(self.winning_str, True, color)

            window.blit(
                text_surface,
                (
                    self.width // 2 - text_width // 2,
                    self.height // 2 - text_height // 2,
                ),
            )
