import math

import pygame

from src import utils
from src.entities.systems.system import System
from src.entities.component import Position, Movement, Graphics, Flags, Tile

class CollisionSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    @staticmethod
    def determine_collision_side(rect1, rect2):
        if rect1.top > rect2.top:
            return "top"
        elif rect1.left > rect2.left:
            return "left"
        elif rect1.right < rect2.right:
            return "right"
        else:
            return "bottom"

    @staticmethod
    def collide_with_unwalkable_tiles(
        axis: str, unwalkable_rects, pos, movement, graphics
    ):
        rect = pygame.Rect(*pos.pos, *graphics.size)

        if axis == "x":
            for unwalkable_rect in unwalkable_rects:
                if rect.colliderect(unwalkable_rect):
                    if movement.vx > 0:
                        pos.pos.x = unwalkable_rect.left - rect.width
                    elif movement.vx < 0:
                        pos.pos.x = unwalkable_rect.right
                    movement.vx = 0

        elif axis == "y":
            for unwalkable_rect in unwalkable_rects:
                if rect.colliderect(unwalkable_rect):
                    if movement.vy > 0:
                        pos.pos.y = unwalkable_rect.top - rect.height
                    elif movement.vy < 0:
                        pos.pos.y = unwalkable_rect.bottom
                    movement.vy = 0

    def get_unwalkable_rects(self, neighboring_tiles):
        unwalkable_tile_rects = []

        for tile_entity_dict in neighboring_tiles:
            tile_entity, tile_pos = tile_entity_dict
            tile = self.world.component_for_entity(tile_entity, Tile)

            if self.world.component_for_entity(tile_entity, Flags).collidable:
                unwalkable_tile_rect = pygame.Rect(
                    tile_pos["x"] * tile.tile_width, tile_pos["y"] * tile.tile_height,
                    tile.tile_width, tile.tile_height
                )
                unwalkable_tile_rects.append(unwalkable_tile_rect)

        return unwalkable_tile_rects

    def collide_with_tiles(self, rect, movement, neighboring_tile_rects, entity):
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        rect.x += movement.vel.x * self.level_state.game_class.dt

        for neighboring_tile_rect in neighboring_tile_rects:
            if neighboring_tile_rect.colliderect(rect):
                if movement.vel.x > 0:
                    rect.right = neighboring_tile_rect.left
                    collision_types['right'] = True
                elif movement.vel.x < 0:
                    print('OMAGOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
                    rect.left = neighboring_tile_rect.right
                    collision_types['left'] = True

        """if entity == self.player:
            collidable_entities = self.world.get_components(
                Movement, Position, Graphics
            )
        else:
            collidable_entities = [(self.player, [self.world.component_for_entity(self.player, i) for i in (Movement, Position, Graphics)])]

        for nested_entity, (nested_movement, nested_pos, nested_graphics) in collidable_entities:
            if nested_entity == entity or nested_pos.rect is None:
                continue
            if rect.colliderect(nested_pos.rect):
                if nested_movement.vel.x < 0 and self.determine_collision_side(nested_pos.rect, rect) == "left":
                    rect.right = nested_pos.rect.left
                elif nested_movement.vel.x > 0 and self.determine_collision_side(nested_pos.rect, rect) == "right":
                    rect.left = nested_pos.rect.right"""

        rect.y += movement.vel.y

        for neighboring_tile_rect in neighboring_tile_rects:
            if neighboring_tile_rect.colliderect(rect):
                if movement.vel.y > 0:
                    movement.vel.y = 0
                    rect.bottom = neighboring_tile_rect.top
                    collision_types['bottom'] = True
                    # print('e')
                elif movement.vel.y < 0:
                    movement.vel.y = 0
                    rect.top = neighboring_tile_rect.bottom
                    collision_types['top'] = True
        return collision_types

    def process(self, event_list):
        # super().process(event_list)

        for entity, (pos, movement, graphics) in self.world.get_components(
            Position, Movement, Graphics
        ):
            pos.rect = pygame.Rect(*pos.pos, *graphics.size)
            neighboring_tile_rects = self.get_unwalkable_rects(
                utils.get_neighboring_tile_entities(self.level_state.tilemap, 1, pos)
            )
            # print((pos.tile_pos, movement.vel) if entity == self.player else 0)

            # Apply gravity
            # Weird bug, can patch it up by capping movement y vel
            movement.vel.y += movement.gravity_acc.y
            if movement.vel.y > 17:
                movement.vel.y = 17
            pos.pos.y += movement.vel.y

            collisions = self.collide_with_tiles(pos.rect, movement, neighboring_tile_rects, entity)
            if collisions["bottom"]:
                pos.on_ground = True
                movement.vel.y = 0

            pos.pos.x = pos.rect.x
            pos.pos.y = pos.rect.y
            pos.tile_pos = utils.pixel_to_tile(pos.pos)