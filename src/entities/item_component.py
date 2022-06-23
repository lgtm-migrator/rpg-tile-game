"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines item components, similar to the components in component.py
"""

from src import pygame

class Item:
    def __init__(self, cooldown, owner=None):
        self.owner = owner
        self.used = False

        self.cooldown = cooldown


class ItemPosition:
    def __init__(self, pos, in_inventory=False):
        self.pos = pos
        self.rect = None
        self.in_inventory = in_inventory


class ItemGraphics:
    def __init__(self, sprite, icon=None, world_sprite=None):
        self.original_img = sprite
        self.current_img = sprite
        self.size = sprite.get_rect().size
        self.bound_size = sprite.get_bounding_rect().size

        if icon is None:
            self.icon = pygame.transform.smoothscale(self.original_img, (50, 50))
        else:
            self.icon = pygame.transform.smoothscale(icon, (50, 50))

        if world_sprite is None:
            self.world_sprite = sprite
        else:
            self.world_sprite = world_sprite


class Consumable:
    def __init__(self, num_uses=1):
        self.uses_left = num_uses


class MeleeWeapon:
    def __init__(self, attack_damage, effects=None):
        self.attack_damage = attack_damage

        self.hit = False
        self.effects = effects


class RangedWeapon:
    def __init__(self, projectile_damage, effects=None):
        self.projectile_damage = projectile_damage

        self.effects = effects


class SlashingSword:
    def __init__(self, angle=0):
        self.angle = angle

        self.rect = None  # Reassign position after interaction with ItemPosition


class GravityBow:
    def __init__(self, launch_vel, angle=0):
        self.angle = angle
        self.launch_vel = launch_vel


class Medkit:
    def __init__(self, heal_power):
        self.heal_power = heal_power


class Projectile:
    def __init__(self, vel, gravity=False):
        self.vel = vel
        self.gravity = gravity
