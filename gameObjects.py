from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np


@dataclass
class CargoSettings:
    balls_loading: int
    balls_unloading: float
    color_led: List[int]
    str_name: str


@dataclass
class RolePlayer:
    custom_settings: Dict
    name_role: str


@dataclass
class VisInfo:
    color: List[int]
    description: str


@dataclass
class PlayerInfo:
    altitude: float # delete
    balls_command: int # delete
    balls_user: int # delete
    centre_info: str
    centre_value: int
    current_pos: List[float]
    data_object: Dict
    data_role: Dict
    full_delay: int
    id: int
    speed: int
    time_game: str # delete


@dataclass
class TeamInfo:
    city_team: str
    color_team: List[int]
    name_team: str
    players: List[PlayerInfo]


@dataclass
class PolygonInfo:
    id: int
    current_pos: List
    data_role: Optional[Dict]
    name_role: str
    vis_info: VisInfo


@dataclass
class ServerInfo:
    gameTime: str
    game_description: str
    state: int
    state_old: int
    version: str




@dataclass()
class Bot:
    id: int
    position: np.ndarray
    home_point_id: int
    num_bullets: int
    end_position: Optional
    state: str
    has_cargo: bool
    velocity: np.ndarray
    type: str



@dataclass
class InGameData:
    players_info: List[TeamInfo]
    polygon_manager: List[PolygonInfo]


@dataclass()
class Enemy:
    id: int
    position: np.ndarray
    has_cargo: bool
    num_bullets: int


@dataclass
class Robot:
    id: int
    control_obj: str


@dataclass
class Player:
    filter: List[str]
    home_object: str
    robot: str
    control_object: str


@dataclass
class Team:
    city_team: str
    color_team: List[int]
    name_team: str
    players: List[Player]


@dataclass
class Polygon:
    id: int
    position: List
    role: str
    vis_info: VisInfo


@dataclass
class Config:
    game_description: str
    game_id: int
    time_game: float


@dataclass
class InitGameData:
    config: Config
    player_manager: List[Team]
    polygon_manager: List[Polygon]
    robot_manager: Dict[str, Robot]


