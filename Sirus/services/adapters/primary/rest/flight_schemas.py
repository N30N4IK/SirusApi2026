from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime, date, timedelta


class FlightCreate(BaseModel):
    origin_city: str
    destination_city: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    total_seats: int

class FlightUpdate(BaseModel):
    origin_city: Optional[str] = None
    destionation_city: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[float] = None
    total_seats: Optional[int] = None


class RouteSegmentResponse(BaseModel):
    flight_od: str
    origin_city: str
    destination_city: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    duration: timedelta
    layover_duration: Optional[timedelta] = None
    
    @classmethod
    def from_domain(cls, segment):
        return cls(
            flight_id=segment.flight.flight_id,
            origin_city=segment.flight.origin_city,
            destination_city=segment.flight.destination_city,
            departure_time=segment.flight.departure_time,
            arrival_time=segment.flight.arrival_time,
            price=segment.flight.price,
            duration=segment.flight.duration,
            layover_duration=segment.layover_duration
        )
    
class TicketRouteResponse(BaseModel):
    route_id: str
    segment: List[RouteSegmentResponse]
    total_cost: float
    total_duration: str
    categories: List[str]