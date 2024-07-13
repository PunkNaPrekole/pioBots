import json
import typing
from gameObjects import *


@dataclass
class Parser:
    file_init: typing.Union[dict, None] = None
    file_in: typing.Union[dict, None] = None

    def read_init(self, file_name):
        with open(file_name) as file:
            j = json.load(file)
        self.file_init = j['config']

    def read_in(self, file_name):
        with open(file_name) as file:
            j = json.load(file)
        self.file_in = j

    def get_polygons(self):
        polygons = [Polygon(
            id=k,
            role=v["role"],
            custom_settings=v['custom_settings'],
            position=v["position"],
            vis_info=VisInfo(
                            color=v['vis_info']['color'],
                            description=v['vis_info']['description']
            )) for k, v in self.file_init['config']['Polygon_manager'].items()]
        return polygons

    def get_teams(self):
        teams = [Team(
            name=team['name_team'],
            color=team['color_team'],
            city=team['city_team'],
            players=[Pioneer(
                filter=p['filter'],
                home_object=p['home_object'],
                id=int(p['robot'])-1
            ) for p in team['players']],
            score=0
        )for team in self.file_init['config']['Player_manager']]
        return teams

    def parse_teams(self):
        teams = [Team(
            name=team['name_team'],
            color=team['color_team'],
            city=team['city_team'],
            players=[Pioneer(
                position=p['current_pos'],
                bonus_list=p['data_role']['bonus_list'],
                id=p['id'],
                health=['data_role']['health'],
                is_cargo=['data_role']['is_cargo'],
                is_shooting=['data_role']['is_shooting'],
                num_bullets=['data_role']['num_bullet']
            ) for p in team['players']],
            score=0
        ) for team in self.file_in['players_info']]
        return teams

    def parse_polygons(self):
        polygons = [Polygon(
            id=k,
            role=v["role"],
            custom_settings=v['custom_settings'],
            position=v["position"],
            vis_info=VisInfo(
                color=v['vis_info']['color'],
                description=v['vis_info']['description']
            )) for k, v in self.file_init['config']['Polygon_manager'].items()]
        return polygons

    def update_game_state(self, teams, polygons):
        for team in teams:
            team.update_players(self.parse_teams())
        for polygon in polygons:
            polygon.update(self.parse_polygons())
        pass
