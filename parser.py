import json
from gameObjects import *


def load_init_game_data(filepath: str) -> InitGameData:
    with open(filepath, 'r') as file:
        data = json.load(file)

    config_data = data['config']

    cargo_settings = [CargoSettings(**cargo) for cargo in config_data['Game_mechanics']['cargo_settings']]
    game_description = config_data['Game_settings']['game_description']
    game_id = config_data['Game_settings']['game_id']
    time_game = config_data['Game_settings']['time_game']

    config_obj = Config(
        cargo_settings=cargo_settings,
        game_description=game_description,
        game_id=game_id,
        time_game=time_game
    )

    player_manager = []
    for team in config_data['Player_manager']:
        players = [Player(
            description=player['description'],
            filter=player['filter'],
            home_object=player['home_object'],
            method_control_obj=player['method_control_obj'],
            name_player=player['name_player'],
            robot=player['robot'],
            role_player=RolePlayer(**player['role_player'])
        ) for player in team['players']]
        player_manager.append(Team(
            city_team=team['city_team'],
            color_team=team['color_team'],
            name_team=team['name_team'],
            players=players
        ))

    polygon_manager = [Polygon(
        custom_settings=v.get('custom_settings', {}),
        ind_for_led_controller=v.get('ind_for_led_controller'),
        position=v.get('position', []),
        role=v['role'],
        vis_info=VisInfo(**v['vis_info'])
    ) for v in config_data['Polygon_manager'].values()]

    robot_manager = {k: Robot(**v) for k, v in config_data['Robot_manager'].items()}

    return InitGameData(
        config=config_obj,
        player_manager=player_manager,
        polygon_manager=polygon_manager,
        robot_manager=robot_manager,
        spare_robots=config_data['Spare_robots']
    )


def load_in_game_data(filepath: str) -> InGameData:
    with open(filepath, 'r') as file:
        data = json.load(file)

    players_info = []
    for team in data['players_info']:
        players = [PlayerInfo(**player) for player in team['players']]
        players_info.append(TeamInfo(
            city_team=team['city_team'],
            color_team=team['color_team'],
            name_team=team['name_team'],
            players=players
        ))

    polygon_manager = []
    if 'polygon_manager' in data:
        polygon_manager = [PolygonInfo(
            current_pos=v['current_pos'],
            data_role=v.get('data_role'),
            name_role=v['name_role'],
            vis_info=VisInfo(**v['vis_info'])
        ) for v in data['polygon_manager'].values()]

    server_info = ServerInfo(**data['server_info'])

    return InGameData(
        players_info=players_info,
        polygon_manager=polygon_manager,
        server_info=server_info
    )


init_game_data = load_init_game_data('../jsons/init_game.json')
in_game_data = load_in_game_data('../jsons/in_game.json')
