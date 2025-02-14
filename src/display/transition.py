"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""
from __future__ import annotations

from typing import Callable, Optional

from src import pygame, screen


class FadeTransition:
    FADE_IN = 0
    FADE_OUT = 1

    def __init__(self, mode: int, fade_rate: float, screen_to_fade: pygame.Surface = screen):
        self.mode = mode
        self.fade_rate = fade_rate
        self.screen_to_fade = screen_to_fade

        self.alpha = 255 if mode == self.FADE_IN else 0
        self.darkness = pygame.Surface(screen_to_fade.get_size())
        self.darkness.set_alpha(self.alpha)

    def draw(self):
        if self.mode == self.FADE_IN:
            self.alpha = max(self.alpha - self.fade_rate, 0)
        else:
            self.alpha = min(self.alpha + self.fade_rate, 255)

        self.darkness.set_alpha(self.alpha)
        self.screen_to_fade.blit(self.darkness, (0, 0))


class EaseTransition:
    def __init__(
        self,
        begin: float,
        end: float,
        duration: int,
        ease_func: Callable[[float], float],
        default_end: Optional[float] = None,
        callback: Optional[Callable[[], None]] = None,
    ):
        self.begin = begin
        self.end = end
        self.range = end - begin
        self.duration = duration
        self.ease_func = ease_func
        self.default_end = default_end
        self.callback = callback

        self.transitioning = False
        self.time_started = 0
        self.value = None

    @staticmethod
    def ease_in_out_quad(x: float):
        if x < 0.5:
            return 2 * x**2
        return 1 - (-x * 2 + 2) ** 2 / 2

    @staticmethod
    def ease_out_quad(x: float):
        return 1 - (1 - x) ** 2

    @staticmethod
    def ease_out_cub(x: float):
        return 1 - (1 - x) ** 3

    @staticmethod
    def ease_out_pow(power: int):
        def inner(x: float):
            return 1 - (1 - x) ** power

        return inner

    @staticmethod
    def ease_out_exp(x: float):
        if x == 1:
            return 1
        return 1 - (2 ** (-10 * x))

    def start(self):
        self.transitioning = True
        self.time_started = pygame.time.get_ticks()

    def stop(self):
        self.transitioning = False
        self.value = self.default_end

    def update(self):
        if not self.transitioning:
            return

        time_elapsed = pygame.time.get_ticks() - self.time_started
        self.value = self.ease_func(min(time_elapsed / self.duration, 1)) * self.range + self.begin

        if pygame.time.get_ticks() - self.time_started > self.duration:
            self.transitioning = False
            self.value = self.default_end
            if self.callback is not None:
                self.callback()
