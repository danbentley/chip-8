from typing import Iterator

import enum

import pygame

from .events import Event, EventType


class Keyboard(enum.Enum):
    ONE = (pygame.K_1, 0x1)
    TWO = (pygame.K_2, 0x2)
    THREE = (pygame.K_3, 0x3)
    FOUR = (pygame.K_4, 0xC)
    Q = (pygame.K_q, 0x4)
    W = (pygame.K_w, 0x5)
    E = (pygame.K_e, 0x6)
    R = (pygame.K_r, 0xD)
    A = (pygame.K_a, 0x7)
    S = (pygame.K_s, 0x8)
    D = (pygame.K_d, 0x9)
    F = (pygame.K_f, 0xE)
    Z = (pygame.K_z, 0xA)
    X = (pygame.K_x, 0x0)
    C = (pygame.K_c, 0xB)
    V = (pygame.K_v, 0xF)


class PyGameBackend:
    def get(self) -> Iterator[Event]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                yield Event(keycode=event.key, type=EventType.KEYDOWN)
            if event.type == pygame.KEYUP:
                yield Event(keycode=event.key, type=EventType.KEYUP)
