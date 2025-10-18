from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid

@dataclass
class Flight:
    """Один сегмент полета (один рейс)"""
    
    origin_city: str
    destination_city: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    total_seats: int
    booked_seats: int = 0
    flight_id: Optional[str] = None

    @property
    def available_seats(self):
        return self.total_seats - self.booked_seats
    
    @property
    def duration(self) -> timedelta:
        return self.arrival_time - self.departure_time
    

@dataclass
class RouteSegment:
    """Сегмент маршрута, используемый для отображения пересадок"""
    flight: Flight
    layover_duration: Optional[timedelta] = None

@dataclass
class TicketRoute:
    """Полный маршрут (прямой или с пересадками)"""
    route_id: str
    segments: List[RouteSegment]
    is_fastest: bool = False
    is_cheapest: bool = False

    @property
    def total_cost(self):
        return sum(seg.flight.price for seg in self.segments)
    
    @property
    def total_duration(self) -> timedelta:
        if not self.segments:
            return timedelta(0)
        
        duration = self.segments[-1].flight.arrival_time - self.segments[0].flight.departure_time
        return duration