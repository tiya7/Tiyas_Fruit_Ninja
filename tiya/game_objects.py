"""Game object definitions and spawn helpers."""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import List

import numpy as np

from .config import (
    FRUIT_RADIUS,
    GRAVITY,
    MAX_LAUNCH_VX,
    MAX_LAUNCH_VY,
    MIN_LAUNCH_VX,
    MIN_LAUNCH_VY,
    SLICE_RADIUS_BONUS,
)

FRUIT_NAMES = [
    "watermelon.png","banana.png","orange.png","apple.png",
    "pineapple.png","grapes.png","strawberry.png","peach.png",
    "cherries.png","mango.png","kiwi.png","pear.png",
    "lemon.png","melon.png","blueberries.png",
]
BOMB_CHANCE = 0.10


@dataclass
class FruitObj:
    sprite_name: str
    x: float
    y: float
    vx: float
    vy: float
    is_bomb: bool = False
    sliced: bool = False
    spawn_time: float = field(default_factory=time.time)
    splash_timer: float = 0.0
    SPLASH_DURATION: float = 0.5

    def update(self, dt: float) -> None:
        self.vy += GRAVITY * dt
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        if self.splash_timer > 0:
            self.splash_timer -= dt

    def is_offscreen(self, h: int, w: int) -> bool:
        return self.y > h + FRUIT_RADIUS*2 or self.x < -250 or self.x > w+250

    def hit_test(self, px: int, py: int) -> bool:
        """Generous hit detection — uses FRUIT_RADIUS + bonus."""
        r = FRUIT_RADIUS + SLICE_RADIUS_BONUS
        dx = self.x - px
        dy = self.y - py
        return (dx*dx + dy*dy) <= (r*r)


@dataclass
class Particle:
    x: float; y: float; vx: float; vy: float
    color: tuple; life: float = 0.5; max_life: float = 0.5

    def update(self, dt: float) -> None:
        self.vy += GRAVITY * 0.25 * dt
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.life -= dt

    @property
    def alive(self) -> bool:
        return self.life > 0

    @property
    def alpha(self) -> float:
        return max(0.0, self.life / self.max_life)


def spawn_fruit(screen_w: int, screen_h: int) -> FruitObj:
    is_bomb = random.random() < BOMB_CHANCE
    sprite  = "bomb.png" if is_bomb else random.choice(FRUIT_NAMES)
    margin  = int(screen_w * 0.15)
    x  = random.randint(margin, screen_w - margin)
    y  = screen_h + FRUIT_RADIUS
    vx = random.uniform(MIN_LAUNCH_VX, MAX_LAUNCH_VX)
    vy = random.uniform(MIN_LAUNCH_VY, MAX_LAUNCH_VY)
    return FruitObj(sprite_name=sprite, x=float(x), y=float(y),
                    vx=vx, vy=vy, is_bomb=is_bomb)


def make_particles(x: float, y: float, color_bgr: tuple, count: int = 22) -> List[Particle]:
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2*np.pi)
        speed = random.uniform(150, 500)
        life  = random.uniform(0.3, 0.6)
        particles.append(Particle(
            x=x, y=y,
            vx=speed*np.cos(angle),
            vy=speed*np.sin(angle) - 250,
            color=color_bgr, life=life, max_life=life,
        ))
    return particles
