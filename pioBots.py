import numpy as np

import parser
from parser import load_init_game_data, load_in_game_data


def update_position(bot):
    if bot.state != "blocked":
        if bot.state == 'taking_off':
            bot.state = 'flying_to_factory' if not bot.has_cargo else 'returning_home'

        elif bot.state == 'flying_to_factory':
            if bot.end_position is not None:
                direction = bot.end_position - bot.position
                direction[2] = 0
                distance = np.linalg.norm(direction)
                if distance > 0.3:
                    bot.velocity = (direction / distance) / 3
                else:
                    bot.velocity = np.array([0.0, 0.0, 0.0])
                    bot.state = 'landing'

        elif bot.state == 'landing':
            if np.linalg.norm(bot.position - bot.home_position) < 0.3: # FIXME подумать на счет приземления успеет ли
                bot.state = 'landed_home'
            else:
                bot.state = 'landed_factory'

        elif bot.state == 'landed_factory':
            if bot.has_cargo:
                bot.state = 'taking_off'
                bot.end_position = bot.home_position

        elif bot.state == 'returning_home':
            direction = bot.end_position - bot.position
            direction[2] = 0
            distance = np.linalg.norm(direction)
            if distance > 0.3:
                bot.velocity = (direction / distance) / 3
            else:
                bot.velocity = np.array([0.0, 0.0, 0.0])
                bot.state = 'landing'

        elif bot.state == 'landed_home':
            if not bot.has_cargo:
                bot.end_position = None
                bot.state = 'taking_off'


def generate_command(bot):
    packet = {
        'axis_0': 1500,
        'axis_1': 1500,
        'axis_2': 1500,
        'axis_3': 1500,
        'fire_btn': 0,
        'cargo_btn': 0,
        'takeoff': 0,
        'land': 0
    }

    if bot.state in ['flying_to_factory', 'returning_home']:
        packet['axis_0'] = int(1500 + bot.velocity[0] * 500)
        packet['axis_1'] = int(1500 + bot.velocity[1] * 500)

    if bot.state == 'landed_factory':
        packet['cargo_btn'] = 1
    elif bot.state == 'landing':
        packet['land'] = 1
    elif bot.state == 'taking_off':
        packet['takeoff'] = 1

    if bot.enemy and np.linalg.norm(bot.enemy.position - bot.position) < 1.0: # FIXME вот тут тоже жоска подумать
        packet['fire_btn'] = 1
        bot.enemy = None

    return packet


def avoid_collisions(bots, players, min_distance=0.3):
    all_drones = bots + players
    for bot in bots:
        for other_drone in all_drones:
            if bot.id != other_drone.id:
                distance = np.linalg.norm(bot.position - other_drone.position)
                if distance < min_distance:
                    repulsion = (bot.position - other_drone.position) / distance
                    perpendicular = np.array([-repulsion[1], repulsion[0], 0])
                    if np.dot(bot.velocity[:2], perpendicular[:2]) < 0:
                        perpendicular = -perpendicular
                    bot.velocity = repulsion + perpendicular * 0.5


def choose_factory(bots, players, fabrics):
    k = 0.2
    for bot in bots:
        best_fabric = None
        best_choice = -float('inf')
        for fabric in fabrics:
            distance = np.linalg.norm(bot.position[:2] - fabric.position[:2])
            is_occupied_by_team = any(np.array_equal(other_drone.end_position, fabric.position) for other_drone in bots if other_drone.id != bot.id)
            is_occupied_by_enemy = any(np.array_equal(enemy.position, fabric.position) for enemy in players)
            choice = fabric.cargo_value - distance * k
            if is_occupied_by_team:
                choice -= 1
            if is_occupied_by_enemy:
                choice -= 2
                if distance < 1.0:
                    best_fabric = fabric
                    bot.state = "waiting_for_enemy"
                    break
            if choice > best_choice:
                best_choice = choice
                best_fabric = fabric
        bot.end_position = best_fabric.position


def is_bot_in_zones(bot, zones):

    def is_bot_in_zone(zone):
        area = np.array(zone)
        x_min, y_min = np.min(area, axis=0)
        x_max, y_max = np.max(area, axis=0)

        x, y = bot.position[:2]

        return x_min <= x <= x_max and y_min <= y <= y_max       # conjunction

    return any(is_bot_in_zone(zone) for zone in zones)


def attack(bots, players, zones):
    for bot in bots:
        if not bot.has_cargo and not is_bot_in_zones(bot, zones):
            nearest_enemy = None
            nearest_enemy_dist = float("inf")
            for enemy in players:
                if enemy.has_cargo:
                    distance = np.linalg.norm(enemy.position - bot.position)
                    if distance < nearest_enemy_dist:
                        nearest_enemy_dist = distance
                        nearest_enemy = enemy
            bot.enemy = nearest_enemy


def main():
    init_data = load_init_game_data('jsons/init_game.json')
    in_data = load_in_game_data('jsons/in_game.json')

    teams = init_data.player_manager
    polygons = init_data.polygon_manager

    fabrics = [polygon for polygon in polygons if polygon.role == "Fabric_RolePolygon"]
    home_points = [polygon for polygon in polygons if polygon.role == "TakeoffArea_RolePolygon"]
    recharge_points = [polygon for polygon in polygons if polygon.role == "Weapoint_RolePolygon"]
    ab_zones = [polygon for polygon in polygons if polygon.role == "AntiBlockZone_RolePolygon"]

    bots = []
    players = []
    for team in teams:
        for player in team.players:
            if player.method_control_obj == "BotControl":
                bots.append(parser.Pioneer(
                    id=int(player.robot),
                    position=np.array(next((home.position for home in home_points if home.id == int(player.home_object)), None)),
                    home_point_id=int(player.home_object),
                    num_bullets=0,
                    end_position=None,
                    state="landed_home",
                    has_cargo=False,
                    velocity=np.array([0, 0, 0])
                ))
    while True:
        choose_factory(bots, players, fabrics)
        for bot in bots:
            update_position(bot)  # FIXME необходимо переписать функцию update_position, а еще вызывать generate_command необходимо перед update_position
        avoid_collisions(bots, players)
        attack(bots, players, ab_zones)


""" 
   fabrics = [point for point in polygons if point.role == "Fabric_RolePolygon"]
    landing_points = [point for point in polygons if point.role == "TakeoffArea_RolePolygon"]
    antiBlockZones = [point for point in polygons if point.role == "AntiBlockZone_RolePolygon"]
    recharge_zones = [point for point in polygons if point.role == "Weapoint_RolePolygon"]

    pioneers = [pioneer for pioneer in drones if pioneer.team == 1]
    enemy_pioneers = [pioneer for pioneer in pioneers if pioneer.team != 1]
    factories = [polygon for polygon in polygons if polygon.role == "Fabric_RolePolygon"]
    while True:
        for pioneer in pioneers:
            update_position(pioneer)
        avoid_collisions(pioneers, enemy_pioneers)
        choose_factory(pioneers, enemy_pioneers, factories)
        attack(pioneers, enemy_pioneers)
"""

if __name__ == "__main__":
    main()
