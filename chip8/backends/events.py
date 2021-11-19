import dataclasses
from typing import Optional
import enum


class EventType(enum.Enum):
    QUIT = enum.auto()
    KEYDOWN = enum.auto()
    KEYUP = enum.auto()


@dataclasses.dataclass
class Event:
    type: EventType
    keycode: Optional[int] = None
