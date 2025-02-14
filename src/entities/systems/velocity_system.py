"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the velocity system, used to "move" entities around
"""

from __future__ import annotations

import math

from src import pygame, utils
from src.entities.components import ai_component, component
from src.entities.components.component import (Flags, Graphics, Movement,
                                               Position)
from src.entities.systems.system import System
from src.types import Dts, Events


class VelocitySystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

        self.settings = self.level_state.settings
        self.player_settings = self.settings["mobs/player"]

    def handle_player_keys(self, event_list: Events):
        keys = pygame.key.get_pressed()
        player_movement = self.world.component_for_entity(self.player, Movement)
        player_pos = self.world.component_for_entity(self.player, Position)
        player_graphics = self.world.component_for_entity(self.player, Graphics)

        player_movement.vx, player_movement.vy = 0, 0
        player_movement.vel.x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_movement.vel.x = -player_movement.speed
            player_pos.direction = -1
            player_graphics.sprites_state = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_movement.vel.x = player_movement.speed
            player_pos.direction = 1
            player_graphics.sprites_state = "right"

        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_SPACE or event.key == pygame.K_w
                ) and player_pos.on_ground:
                    player_pos.on_ground = False
                    player_movement.vel.y = self.player_settings["jump_vel"]

                    # TODO: Add jump particles

    def process(self, event_list: Events, dts: Dts):
        self.handle_player_keys(event_list)

        for entity, (flags, pos, movement) in self.world.get_components(Flags, Position, Movement):
            if flags.rotatable:
                movement.rot = (
                    self.world.component_for_entity(self.player, Position).pos - pos.pos
                ).angle_to(pygame.Vector2(1, 0))

            # AI: Follow entity closely
            if self.world.has_component(entity, ai_component.FollowsEntityClose):
                follows_entity_close = self.world.component_for_entity(
                    entity, ai_component.FollowsEntityClose
                )
                entity_followed = follows_entity_close.entity_followed
                entity_followed_pos = self.world.component_for_entity(
                    entity_followed, component.Position
                )

                # Follow entity if and ONLY if:
                # 1. The entity's tile y coordinate is the same as the enemy's
                # 2. The distance from entity to enemy is less than 10, in tile space
                if (
                    pos.tile_pos.distance_to(entity_followed_pos.tile_pos)
                    < follows_entity_close.follow_range
                ):
                    if entity_followed_pos.tile_pos.y == pos.tile_pos.y:
                        mob_tile = utils.pixel_to_tile(pos.pos)
                        tile_next_beneath = self.tilemap.tiles.get(
                            (0, (mob_tile.x + math.copysign(1, movement.vel.x), mob_tile.y + 1))
                        )
                        tile_prev_beneath = self.tilemap.tiles.get(
                            (0, (mob_tile.x - math.copysign(1, movement.vel.x), mob_tile.y + 1))
                        )

                        if entity_followed_pos.pos.x > pos.pos.x and tile_next_beneath is not None:
                            movement.vel.x = movement.speed
                            pos.direction = 1
                        elif (
                            entity_followed_pos.pos.x < pos.pos.x and tile_prev_beneath is not None
                        ):
                            movement.vel.x = -movement.speed
                            pos.direction = -1
                    else:  # Check if about to fall from platform
                        mob_tile = utils.pixel_to_tile(pos.pos)
                        tile_next_beneath = self.tilemap.tiles.get(
                            (0, (mob_tile.x + 1, mob_tile.y + 1))
                        )
                        tile_prev_beneath = self.tilemap.tiles.get(
                            (0, (mob_tile.x - 1, mob_tile.y + 1))
                        )

                        if (
                            pos.direction == 1
                            and tile_next_beneath is None
                            or pos.direction == -1
                            and tile_prev_beneath is None
                        ):
                            movement.vel.x *= -1
                            pos.direction *= -1

            if flags.mob_type == "walker_enemy":
                movement.vel.x = movement.speed * pos.direction

                mob_tile = utils.pixel_to_tile(pos.pos)
                tile_next_beneath = (
                    mob_tile.x + math.copysign(1, movement.vel.x),
                    mob_tile.y + 1,
                )
                tile_next = (tile_next_beneath[0], mob_tile.y)

                actual_tile_next = self.tilemap.tiles.get((0, tile_next))
                if actual_tile_next or not self.tilemap.tiles.get((0, tile_next_beneath)):
                    if actual_tile_next and not actual_tile_next.get("unwalkable"):
                        continue
                    pos.direction *= -1
