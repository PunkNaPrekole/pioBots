import json
from gameObjects import *


def load_init_game_data(filepath: str) -> InitGameData:
    """
    function for parsing init_game.json
    :param filepath: path to init_game.json file
    :return: InitGameData object
    """
    with open(filepath, 'r') as file:
        data = json.load(file)

    config_data = data['config']

    game_description = config_data['Game_settings']['game_description']
    game_id = config_data['Game_settings']['game_id']
    time_game = config_data['Game_settings']['time_game']

    config_obj = Config(
        game_description=game_description,
        game_id=game_id,
        time_game=time_game
    )

    robot_manager = {k: Robot(**v) for k, v in config_data['Robot_manager'].items()}

    player_manager = []
    for team in config_data['Player_manager']:
        players = [Player(
            filter=player['filter'],
            home_object=player['home_object'],
            robot=player['robot']
        ) for player in team['players']]
        player_manager.append(Team(
            city_team=team['city_team'],
            color_team=team['color_team'],
            name_team=team['name_team'],
            players=players
        ))

    polygon_manager = [Polygon(
        id=int(k),
        position=v.get('position', []),
        role=v['role'],
        vis_info=VisInfo(**v['vis_info'])
    ) for k, v in config_data['Polygon_manager'].items()]

    return InitGameData(
        config=config_obj,
        player_manager=player_manager,
        polygon_manager=polygon_manager,
        robot_manager=robot_manager
    )


def load_in_game_data(filepath: str) -> InGameData:
    """
    function for parsing in_game.json
    :param filepath: path to in_game.json file
    :return: InGameData object
    """
    with open(filepath, 'r') as file:
        data = json.load(file)

    players_info = []
    for team in data['players_info']:
        players = [PlayerInfo(**player) for player in team['players']] # FIXME added field 'control_object'
        players_info.append(TeamInfo(
            city_team=team['city_team'],
            color_team=team['color_team'],
            name_team=team['name_team'],
            players=players
        ))

    polygon_manager = []
    if 'polygon_info' in data:
        polygon_manager = [PolygonInfo(
            id=int(k),
            current_pos=v['current_pos'],
            data_role=v.get('data_role'),
            name_role=v['name_role'],
            vis_info=VisInfo(**v['vis_info'])
        ) for k, v in data['polygon_info'].items()]

    return InGameData(
        players_info=players_info,
        polygon_manager=polygon_manager,
    )
