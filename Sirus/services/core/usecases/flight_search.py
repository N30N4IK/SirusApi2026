from core.ports.out.flight_repo import FlightRepository
from core.domain.flight import Flight, TicketRoute, RouteSegment
from typing import List, Optional, Dict, Tuple, Any
from datetime import date, timedelta, datetime
import uuid

MAX_LAYOVER_TIME = timedelta(hours=24)

class FlightSearchService:
    def __init__(self, flight_repo: FlightRepository):
        self._repo = flight_repo

    
    def _find_connecting_routes(self, origin: str, destination: str, start_date: date, passengers: int) -> List[TicketRoute]:
        """Находит все возодные маршруты с 0, 1 или 2 пересадки, соблюдая ограничение на время пересадки (<24 часа). Использует BFS (Breadth-First Search) для поиска по уровням (пересадкам)"""

        all_flight = self._repo.find_flights_by_criteria(origin, start_date, passengers)

        flights_by_origin: Dict[str, List[Flight]] = {}
        for f in all_flight:
            flights_by_origin.setdefault(f.origin_city, []).append(f)

        routes: List[TicketRoute] = []

        queue: List[Tuple[str, datetime, List[RouteSegment]]] = [(origin, datetime.min, [])]

        max_segments = 3

        while queue:
            current_city, prev_arrival_time, current_segments = queue.pop(0)

            if len(current_segments) >= max_segments:
                continue

            possible_flight = flights_by_origin.get(current_city, [])

            for flight in possible_flight:
                layover = flight.departure_time - prev_arrival_time

                if prev_arrival_time != datetime.min:
                    if layover > MAX_LAYOVER_TIME or layover < timedelta(minutes=30):
                        continue

                new_segments = current_segments + [RouteSegment(flight=flight, layover_duration=layover if prev_arrival_time != datetime.min else None)]

                if flight.destination_city == destination:
                    routes.append(
                        TicketRoute(route_id=str(uuid.uuid4()), segments=new_segments)
                    )
                    continue

                queue.append((
                    flight.destination_city,
                    flight.arrival_time,
                    new_segments
                ))

        return routes
    
    def search_flights(self, origin_city: str, destination_city: str, date: date, passengers: int) -> List[Dict[str, Any]]:
        """Ищет рейсы, категоризирует их по стоимости и скорости, и упорядочивает результаты"""
        if passengers <= 0:
            raise ValueError('Кол-во пассажиров должно быть больше нуля')
        
        all_routes = self._find_connecting_routes(origin_city, destination_city, date, passengers)

        if not all_routes:
            return []
        
        metrics = [
            {'route': r,
             'cost': r.total_cost * passengers,
             'duration_seconds': r.total_duration.total_seconds()
             }
             for r in all_routes
        ]

        cheapset_cost = min(m['cost'] for m in metrics)
        fastest_duration = min(m['duration_seconds'] for m in metrics)

        results: List[Dict[str, Any]] = []

        for m in metrics:
            is_cheapset = m['cost'] == cheapset_cost
            is_fastest = m['duration_seconds'] == fastest_duration

            route_dict = {
                'route_id': m['route'].route_id,
                'segments': m['route'].segments,
                'total_cost': m['cost'],
                'total_duration': str(m['route'].total_duration),
                'categories': []
            }

            if is_cheapset: route_dict['categories'].append('cheapset')
            if is_fastest: route_dict['categories'].append('fastest')

            results.append(route_dict)
        
        def custom_sort(item):
            is_special = bool(item['categories'])
            return (-is_special, item['total_cost'])
        
        results.sort(key=custom_sort)

    # --- CRUD ---

    def create_flight(self, data: Dict[str, Any]) -> Flight:
        flight = Flight(**data)
        return self._repo.save_flight(flight)
    
    def delete_flight(self, flight_id: str) -> None:
        self._repo.delete_flight(flight_id)