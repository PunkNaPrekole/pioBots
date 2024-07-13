from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class Cargo:
    name: str
    color_led: list[int]


@dataclass
class Pioneer:
    id: int
    filter: List = None
    home_object: str = None
    altitude: float = None
    position: List = None
    bonus_list: List = None
    cargo_color: List = None
    health: int = 100
    is_cargo: bool = False
    is_shooting: bool = False
    num_bullets: int = 0
    state: str = "landed_home"
    velocity: Any = None

    def update(self, pioneer: Dict):
        self.position = pioneer['current_pos']
        self.bonus_list = pioneer['data_role']['bonus_list']
        self.cargo_color = pioneer['data_role']['cargo_color']
        self.health = pioneer['health']
        self.is_cargo = pioneer['is_cargo']
        self.is_shooting = pioneer['is_shooting']
        self.num_bullets = pioneer['num_bullet']

    def update_state(self, state: str, velocity: Any):
        self.state = state
        self.velocity = velocity


@dataclass
class VisInfo:
    color: List[int]
    description: str

    def update(self, vis_info: Dict):
        self.color = vis_info['color']
        self.description = vis_info['description']


@dataclass()
class DataRole:
    current_cargo_color: List[List]
    current_conditions: int
    is_cargo: bool
    num_cargo: int

    def update(self, data_role: Dict):
        self.is_cargo = data_role['is_cargo']
        self.num_cargo = data_role['num_cargo']
        self.current_conditions = data_role['current_conditions']
        self.current_cargo_color = data_role['current_cargo_color']


@dataclass
class Polygon:
    id: int
    role: str
    custom_settings: Dict
    position: List[float]
    vis_info: VisInfo
    data_role: DataRole = None

    def update(self, data_role: Dict, vis_info: Dict):
        self.data_role = self.data_role.update(data_role)
        self.vis_info = self.vis_info.update(vis_info)



@dataclass()
class Team:
    name: str
    color: List
    city: str
    players: List
    score: Any  # тут хз int or float

    def update_players(self, players: List):
        for i, player in enumerate(self.players):
            player.update(players[i])
