from sqlalchemy import Column, String, Enum, ForeignKey, Integer, Float, DateTime, Boolean, Date
from sqlalchemy.orm import declarative_base, relationship

from services.core.domain.hotel import RoomType
from services.core.domain.user import Role
Base = declarative_base()



class HotelORM(Base):
    __tablename__ = 'hotels'
    hotel_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, index=True, nullable=False)
    stars = Column(Integer, index=True, nullable=False)
    description = Column(String)

    rooms = relationship('RoomORM', back_populates='hotel')

class RoomORM(Base):
    __tablename__ = 'rooms'
    room_id = Column(String, primary_key=True, index=True)
    hotel_id = Column(String, ForeignKey('hotels.hotel_id'), nullable=False)
    room_number = Column(String, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)
    capacity = Column(Integer, nullable=False)
    rooms_count = Column(Integer, nullable=False)
    price_per_night = Column(Float, index=True, nullable=False)

    hotel = relationship('HotelORM', back_populates='rooms')


class UserORM(Base):
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.USER, nullable=False)

    def __repr__(self):
        return f"<UserORM(email-'{self.email}', role='{self.role}')"
    
class FlightORM(Base):
    __tablename__ = 'flights'
    flight_id = Column(String, primary_key=True, index=True)
    origin_city = Column(String, index=True, nullable=False)
    destination_city = Column(String, index=True, nullable=False)
    departure_time = Column(DateTime, index=True, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    total_seats = Column(Integer, nullable=False)
    booked_seats = Column(Integer, default=0, nullable=False)

class HotelBookingORM(Base):
    __tablename__ = 'hotel_bookings'
    booking_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    room_id = Column(String, ForeignKey('rooms.room_id'), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    total_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship('UserORM')
    room = relationship('RoomORM')
    