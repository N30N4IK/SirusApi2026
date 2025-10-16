from pydantic import BaseModel
from typing import Optional, List
from core.domain.hotel import RoomType

class HotelCreateUpdate(BaseModel):
    name: str
    city: str
    stars: int
    description: str

class RoomCreateUpdate(BaseModel):
    hotel_id: str
    room_number: str
    room_type: RoomType
    capacity: int
    rooms_count: int
    price_per_night: float

class RoomResponse(BaseModel):
    room_id: str
    hotel_id: str
    room_number: str
    room_type: RoomType
    capacity: int
    rooms_count: int
    price_per_night: float

    class Config: from_attributer = True

class HotelResponse(BaseModel):
    hotel_id: str
    name: str
    city: str
    stars: int
    desctiprion: str

    class Config: from_attributes = True

class HotelUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    stars: Optional[int] = None
    description: Optional[str] = None