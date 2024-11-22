from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np

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


@dataclass()
class Bot:
    id: int
    position: np.ndarray
    home_point: np.ndarray
    num_bullets: int
    end_position: Optional
    state: str
    has_cargo: bool
    velocity: np.ndarray
    type: str
    filter: List
    enemy: bool


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
    players: List


@dataclass
class Polygon:
    id: str
    position: List
    role: str
    vis_info: VisInfo
    data_role: Dict


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
    robot_manager: List[Robot]


@dataclass
class InGameData:
    players_info: List[Team]
    polygon_manager: List[Polygon]


