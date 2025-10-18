from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import uuid


@dataclass
class HotelBooking:
    user_id: str
    room_id: str
    check_in_date: date
    check_out_date: date
    total_price: float

    booking_id: Optional[str]
    is_active: bool = True

    