import itertools
from typing import List
from game_objs import DrawableObject


def find_collisions(game_objs: List[DrawableObject]):
    object_combinations = [x for x in itertools.product(game_objs, game_objs)]

    for pair in object_combinations:
        obj1 = pair[0]
        obj2 = pair[1]

        if obj1 == obj2:
            continue

        if obj1.get_bounding_rectangle().colliderect(obj2.get_bounding_rectangle()):
            obj1.handle_collision(obj2)
