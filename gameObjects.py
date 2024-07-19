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
class Player:
    description: str
    filter: List[str]
    home_object: str
    method_control_obj: str
    name_player: str
    robot: str
    role_player: RolePlayer


@dataclass
class Team:
    city_team: str
    color_team: List[int]
    name_team: str
    players: List[Player]


@dataclass
class VisInfo:
    color: List[int]
    description: str


@dataclass
class Polygon:
    id: int
    custom_settings: Dict
    ind_for_led_controller: Optional[int]
    position: List
    role: str
    vis_info: VisInfo


@dataclass
class Robot:
    control_obj: str
    filter_position: Dict
    ip: str
    port: int
    title: str


@dataclass
class Config:
    cargo_settings: List[CargoSettings]
    game_description: str
    game_id: int
    time_game: float


@dataclass
class InitGameData:
    config: Config
    player_manager: List[Team]
    polygon_manager: List[Polygon]
    robot_manager: Dict[str, Robot]
    spare_robots: List


@dataclass
class PlayerInfo:
    altitude: float
    balls_command: int
    balls_user: int
    centre_info: str
    centre_value: int
    current_pos: List[float]
    data_object: Dict
    data_role: Dict
    full_delay: int
    id: int
    speed: int
    time_game: str


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


@dataclass
class InGameData:
    players_info: List[TeamInfo]
    polygon_manager: List[PolygonInfo]
    server_info: ServerInfo


@dataclass()
class Pioneer:
    id: int
    position: np.ndarray
    home_point_id: int
    num_bullets: int
    end_position: np.ndarray
    state: str
    has_cargo: bool
    velocity: np.ndarray
