from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime, date, timedelta

class BookingResponse(BaseModel):
    booking_id: str
    user_id: str
    room_id: str
    check_in_date: date
    check_out_date: date
    total_price: float
    is_active: bool

    class Config: from_attributes = True