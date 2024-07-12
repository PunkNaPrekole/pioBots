import numpy as np
from parser import Parser


class Pioneer:
    def __init__(self, id, home_position, team, charge, health=100, enemy=None, flight_altitude=1.0):
        self.id = id
        self.home_position = np.array(home_position)
        self.team = team
        self.charge = charge  # num_bullets
        self.freeze = False
        self.health = health
        self.enemy = enemy
        self.position = self.home_position
        self.end_position = None
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.flight_altitude = flight_altitude
        self.state = 'landed_home'
        self.has_cargo = False


def update_position(pioneer):
    if not pioneer.freeze:
        if pioneer.state == 'taking_off':
            if pioneer.has_cargo:
                pioneer.state = 'returning_home'
            else:
                pioneer.state = 'flying_to_factory'

        elif pioneer.state == 'flying_to_factory':
            if pioneer.end_position is not None:
                direction = pioneer.end_position - pioneer.position
                direction[2] = 0
                distance = np.linalg.norm(direction)
                if distance > 0.3:
                    pioneer.velocity = (direction / distance) / 3
                else:
                    pioneer.velocity = np.array([0.0, 0.0, 0.0])
                    pioneer.state = 'landing'

        elif pioneer.state == 'landing':
            if np.linalg.norm(pioneer.position[:2] - pioneer.home_position[:2]) < 0.3:
                pioneer.state = 'landed_home'
            else:
                pioneer.state = 'landed_factory'

        elif pioneer.state == 'landed_factory':
            pioneer.state = 'waiting_for_cargo'

        elif pioneer.state == 'waiting_for_cargo':
            if pioneer.has_cargo:
                pioneer.state = 'taking_off'
                pioneer.end_position = pioneer.home_position

        elif pioneer.state == 'returning_home':
            direction = pioneer.end_position - pioneer.position
            direction[2] = 0
            distance = np.linalg.norm(direction)
            if distance > 0.3:
                pioneer.velocity = (direction / distance) / 3
            else:
                pioneer.velocity = np.array([0.0, 0.0, 0.0])
                pioneer.state = 'landing'

        elif pioneer.state == 'landed_home':
            pioneer.has_cargo = False
            pioneer.end_position = None
            pioneer.state = 'taking_off'


def generate_command(pioneer):
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

    if pioneer.state == 'moving_to_factory' or pioneer.state == 'returning_home':
        packet['axis_0'] = int(1500 + pioneer.velocity[0] * 500)
        packet['axis_1'] = int(1500 + pioneer.velocity[1] * 500)

    if pioneer.state == 'taking_cargo':
        packet['cargo_btn'] = 1
    elif pioneer.state == 'landing':
        packet['land'] = 1
    elif pioneer.state == 'taking_off':
        packet['takeoff'] = 1
    if pioneer.enemy and np.linalg.norm(pioneer.enemy.position - pioneer.position) < 1.0 or pioneer.state == 'waiting_for_enemy':
        packet['fire_btn'] = 1
        pioneer.enemy = None

    return packet


def avoid_collisions(pioneers, enemy_pioneers, min_distance=0.3):
    all_drones = pioneers + enemy_pioneers
    for pioneer in pioneers:
        for other_pioneer in all_drones:
            if pioneer.id != other_pioneer.id:
                distance = np.linalg.norm(pioneer.position - other_pioneer.position)
                if distance < min_distance:
                    repulsion = (pioneer.position - other_pioneer.position) / distance
                    perpendicular = np.array([-repulsion[1], repulsion[0], 0])
                    if np.dot(pioneer.velocity[:2], perpendicular[:2]) < 0:
                        perpendicular = -perpendicular
                    pioneer.velocity = repulsion + perpendicular * 0.5


def choose_factory(pioneers, enemy_pioneers, factories):
    k = 0.2
    for pioneer in pioneers:
        best_factory = None
        best_choice = -float('inf')
        for factory in factories:
            distance = np.linalg.norm(pioneer.position[:2] - factory.position[:2])
            is_occupied_by_team = any(np.array_equal(other_drone.end_position, factory.position) for other_drone in pioneers if other_drone.id != pioneer.id)
            is_occupied_by_enemy = any(np.array_equal(enemy.position, factory.position) for enemy in enemy_pioneers)
            choice = factory.cargo_value - distance * k
            if is_occupied_by_team:
                choice -= 1
            if is_occupied_by_enemy:
                choice -= 2
                if distance < 1.0:
                    best_factory = factory
                    pioneer.state = "waiting_for_enemy"
                    break
            if choice > best_choice:
                best_choice = choice
                best_factory = factory
        pioneer.end_position = best_factory.position


def attack(pioneers, enemy_pioneers):
    for pioneer in pioneers:
        if not pioneer.has_cargo:
            nearest_enemy = None
            nearest_enemy_dist = float("inf")
            for enemy in enemy_pioneers:
                if enemy.has_cargo:
                    distance = np.linalg.norm(enemy.position - pioneer.position)
                    if distance < nearest_enemy_dist:
                        nearest_enemy_dist = distance
                        nearest_enemy = enemy
            pioneer.enemy = nearest_enemy


def main():

    drones = Parser.get_pioneers()
    pioneers = [pioneer for pioneer in drones if pioneer.team == 1]
    enemy_pioneers = [pioneer for pioneer in pioneers if pioneer.team != 1]
    polygons = Parser.get_polygons()
    factories = [polygon for polygon in polygons if polygon.role == "Fabric_RolePolygon"]
    while True:
        for pioneer in pioneers:
            update_position(pioneer)
        avoid_collisions(pioneers, enemy_pioneers)
        choose_factory(pioneers, enemy_pioneers, factories)
        attack(pioneers, enemy_pioneers)


if __name__ == "__main__":
    main()
