from gameObjects import *
import json

def load_init_game_data(filepath: str) -> InitGameData:
    with open(filepath, 'r') as file:
        data = json.load(file)

    config_data = data.get('config')
    game_settings = config_data.get('Game_settings')

    config_obj = Config(
        game_description=game_settings.get('game_description'),
        game_id=game_settings.get('game_id'),
        time_game=game_settings.get('time_game')
    )
    robot_data = config_data.get('Robot_manager').items()
    robot_manager = [
        Robot(id=k,
              control_obj=v.get('control_obj')) for k, v in robot_data]

    player_manager = [
        Team(
            city_team=team.get('city_team'),
            color_team=team.get('color_team'),
            name_team=team.get('name_team'),
            players=[
                Player(
                    filter=player.get('filter'),
                    home_object=player.get('home_object'),
                    robot=player.get('robot'),
                    control_object=next(robot.control_obj for robot in robot_manager if robot.id == player.get('robot'))
                )
                for player in team.get('players')
            ]
        )
        for team in config_data.get('Player_manager')
    ]

    polygon_manager = [
        Polygon(
            id=k,
            position=v.get('position'),
            role=v.get('role'),
            vis_info=VisInfo(**v.get('vis_info')),
             data_role={}
        )
        for k, v in config_data.get('Polygon_manager').items()
    ]

    return InitGameData(
        config=config_obj,
        player_manager=player_manager,
        polygon_manager=polygon_manager,
        robot_manager=robot_manager
    )

def load_in_game_data(filepath: str) -> InGameData:
    with open(filepath, 'r') as file:
        data = json.load(file)

    players_info = [
        Team(
            city_team=team.get('city_team'),
            color_team=team.get('color_team'),
            name_team=team.get('name_team'),
            players=[PlayerInfo(**player) for player in team.get('players')]
        )
        for team in data.get('players_info')
    ]

    polygon_manager = [
        Polygon(
            id=k,
            position=v.get('current_pos'),
            data_role=v.get('data_role'),
            role=v.get('name_role'),
            vis_info=VisInfo(**v.get('vis_info'))
        ) for k, v in data.get('polygon_info').items()
    ]

    return InGameData(
        players_info=players_info,
        polygon_manager=polygon_manager
    )