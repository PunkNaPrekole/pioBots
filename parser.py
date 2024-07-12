import json
import typing
from arena_objects import dataclass
from arena_objects.polygon import Polygon
from arena_objects.pioneer import Pioneer
from arena_objects.cargo import Cargo


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
            j=json.load(file)
        self.file_in = j

    def get_polygons(self, file):
        polygons = []
        for i in file['polygon_info']:
            polygons.append(Polygon(id=i,
                                    role=file['polygon_info'][i]['name_role'],
                                    position=file['polygon_info'][i]['current_pos'],
                                    is_cargo=file['polygon_info'][i]['data_role']['is_cargo']
                                    if file['polygon_info'][i]['data_role'] else False,
                                    cargo=Cargo(color_led=file['polygon_info'][i]['data_role']['current_cargo_color'])
                                    if file['polygon_info'][i]['data_role'] else [0, 0, 0]))

        return polygons

    def get_pioneers(self, file):
        pioneers = []
        for team in file['players_info']:
            for player in team['players']:
                pioneers.append(Pioneer(id=player['id'],
                                        position=player['current_pos'],
                                        is_cargo=player['data_role']['is_cargo'],
                                        is_shooting=player['data_role']['is_shooting'],
                                        cargo=Cargo(color_led=player['data_role']['cargo_color'])))
        return pioneers


if __name__ == "__main__":
    parser = Parser()
    parser.read_in('in_game.json')
    parser.read_init('init_game.json')
    print(parser.get_polygons(parser.file_in)[2])
    print(parser.get_pioneers(parser.file_in)[1])

