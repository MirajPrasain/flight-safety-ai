# backend/models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Location(BaseModel):
    latitude: float
    longitude: float
    altitude_ft: float

class Speed(BaseModel):
    airspeed_knots: float
    groundspeed_knots: Optional[float] = None
    vertical_speed_fpm: float

class Engine(BaseModel):
    engine_1_rpm: float
    engine_2_rpm: float
    fuel_flow_gph: Optional[float] = None

class AircraftSystems(BaseModel):
    landing_gear_status: str # "UP", "DOWN", "TRANSIT"
    flap_setting: str
    autopilot_engaged: bool
    warnings: List[str] = []

class Environment(BaseModel):
    wind_speed_knots: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    temperature_c: Optional[float] = None
    visibility_miles: Optional[float] = None
    precipitation: str = "NONE"
    terrain_proximity_ft: Optional[float] = None

class PilotActions(BaseModel):
    throttle_percent: Optional[float] = None
    pitch_deg: Optional[float] = None
    roll_deg: Optional[float] = None
    yaw_deg: Optional[float] = None

class FlightData(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    flight_id: str
    aircraft_type: str
    pilot_id: str
    location: Location
    speed: Speed
    engine: Engine
    aircraft_systems: AircraftSystems
    environment: Environment
    pilot_actions: Optional[PilotActions] = None # Optional, for future use or simulation