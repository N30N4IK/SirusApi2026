from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import uuid

class RoomType(str, Enum):
    STANDART = 'standart'
    LARGE = 'large'
    PREMIUM = 'premium'


@dataclass
class Room:
    hotel_id: str
    room_number: str
    room_type: RoomType
    capacity: int
    rooms_count: int
    price_per_night: float
    room_id: Optional[str] = None

@dataclass
class Hotel:
    name: str
    city: str
    stars: int
    description: str
    hotel_id: Optional[str] = None