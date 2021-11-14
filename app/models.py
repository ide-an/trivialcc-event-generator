from sqlalchemy import (
        Column, Integer, String, DateTime, ForeignKey, Float, select
        )
from app.db import Base, db_session
import json

class Event(Base):
    __tablename__ = 'events'
    id  = Column(Integer, primary_key=True)
    name = Column(String(100))
    location = Column(String(100))
    site_url = Column(String(1000))
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)

    def __repr__(self):
        return f"Event(id  = {self.id!r}, name = {self.name!r}, location = {self.location!r}, site_url = {self.site_url!r}, start_datetime = {self.start_datetime!r}, end_datetime = {self.end_datetime!r})"

class Circle(Base):
    __tablename__ = 'circles'
    id  = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    space_id =  Column(Integer, ForeignKey('spaces.id'))
    name = Column(String(100))
    penname = Column(String(100))
    site_url = Column(String(1000))
    pixiv = Column(String(1000))
    twitter = Column(String(1000))

    def __repr__(self):
        return "Circle("+ (", ".join([
            f"id = {self.id!r}",
            f"event_id = {self.event_id!r}",
            f"space_id = {self.space_id!r}",
            f"name = {self.name!r}",
            f"penname = {self.penname!r}",
            f"site_url = {self.site_url!r}",
            f"pixiv = {self.pixiv!r}",
            f"twitter = {self.twitter!r}",
            ]))+")"

    @classmethod
    def find_by_event(cls, event):
        return db_session.execute(
                select(Circle, Space)
                .where(Circle.space_id == Space.id)
                .where(Circle.event_id == event.id)
                .order_by(Space.id)).all()

class Space(Base):
    __tablename__ = 'spaces'
    id  = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    name = Column(String(100))

    def __repr__(self):
        return "Space("+ (", ".join([
            f"id = {self.id!r}",
            f"event_id = {self.event_id!r}",
            f"name = {self.name!r}",
            ]))+")"

class Map(Base):
    __tablename__ = 'maps'
    id  = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    name = Column(String(100))
    image_url = Column(String(1000))

    def __repr__(self):
        return "Map("+ (", ".join([
            f"id = {self.id!r}",
            f"event_id = {self.event_id!r}",
            f"name = {self.name!r}",
            f"image_url = {self.image_url!r}",
            ]))+")"

class MapRegion(Base):
    __tablename__ = 'map_regions'
    id  = Column(Integer, primary_key=True)
    map_id = Column(Integer, ForeignKey('maps.id'))
    space_id = Column(Integer, ForeignKey('spaces.id'))
    x = Column(Float)
    y = Column(Float)
    w = Column(Float)
    h = Column(Float)

    def __repr__(self):
        return "MapRegion("+ (", ".join([
            f"id = {self.id!r}",
            f"map_id = {self.map_id!r}",
            f"space_id = {self.space_id!r}",
            f"x = {self.x!r}",
            f"y = {self.y!r}",
            f"w = {self.w!r}",
            f"h = {self.h!r}",
            ]))+")"
    def to_json(self):
        return json.dumps({
            "id": self.id,
            "map_id": self.map_id,
            "space_id": self.space_id,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            })

