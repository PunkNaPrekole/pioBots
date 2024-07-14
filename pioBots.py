import numpy as np
import parser


class BotsController:
    """
    Класс BotsController управляет действиями дронов в игре (пока только пионеров)

    bots - список ботов (пока только пионеров)
    players - список вражеских игроков (пока только пионеров)
    fabrics - список фабрик, выбираются из полигонов по роли
    home_points - Список стартовых зон, выбираются из полигонов по роли
    recharge_points - список "заправок", выбираются из полигонов по роли
    ab_zones - список зон блокировки, выбираются из полигонов по роли
    game_state - текущее состояние игры, загруженное из файла, объект InGameData
    min_distance - минимальное расстояние между дронами (для avoid_collision)

    update_game_state - загружает данные из in_game.json на выходе объект InGameData
    choose_factory - выбирает фабрику для дрона, учитывая ценность груза и расстояние до нее
    avoid_collision - для избежания коллизий
    is_bot_in_zones - проверка на нахождение дрона в зоне блокировки
    attack - выбирает ближайшего enemy с грузом для атаки
    update_position - апдейтит состояние дрона
    generate_command - генерит пакет команд для дрона
    """

    def __init__(self, bots, players, polygons):
        self.bots = bots
        self.players = players
        self.fabrics = [polygon for polygon in polygons if polygon.role == "Fabric_RolePolygon"]
        self.home_points = [polygon for polygon in polygons if polygon.role == "TakeoffArea_RolePolygon"]
        self.recharge_points = [polygon for polygon in polygons if polygon.role == "Weapoint_RolePolygon"]
        self.ab_zones = [polygon for polygon in polygons if polygon.role == "AntiBlockZone_RolePolygon"]
        self.game_state = None
        self.min_distance = 0.3

    def update_game_state(self):
        self.game_state = parser.load_in_game_data("jsons/in_game.json")

    def choose_factory(self, bot):
        best_fabric = None
        best_choice = -float('inf')
        for fabric in self.fabrics:
            distance = np.linalg.norm(bot.position[:2] - fabric.position[:2])
            is_occupied_by_team = any(
                np.array_equal(other_drone.end_position, fabric.position) for other_drone in self.bots if
                other_drone.id != bot.id)
            is_occupied_by_enemy = any(np.array_equal(enemy.position, fabric.position) for enemy in self.players)
            choice = fabric.cargo_value - distance
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

    def avoid_collision(self, bot):
        all_drones = self.bots + self.players
        for other_drone in all_drones:
            if bot.id != other_drone.id:
                distance = np.linalg.norm(bot.position - other_drone.position)
                if distance < self.min_distance:
                    repulsion = (bot.position - other_drone.position) / distance
                    perpendicular = np.array([-repulsion[1], repulsion[0], 0])
                    if np.dot(bot.velocity[:2], perpendicular[:2]) < 0:
                        perpendicular = -perpendicular
                    bot.velocity = repulsion + perpendicular * 0.5

    def is_bot_in_zones(self, bot):

        def is_bot_in_zone(zone):
            area = np.array(zone)
            x_min, y_min = np.min(area, axis=0)
            x_max, y_max = np.max(area, axis=0)

            x, y = bot.position[:2]

            return x_min <= x <= x_max and y_min <= y <= y_max

        return any(is_bot_in_zone(zone) for zone in self.ab_zones)

    def attack(self, bot):
        if not bot.has_cargo and not self.is_bot_in_zones(bot):
            nearest_enemy = None
            nearest_enemy_dist = float("inf")
            for enemy in self.players:
                if enemy.has_cargo:
                    distance = np.linalg.norm(enemy.position - bot.position)
                    if distance < nearest_enemy_dist:
                        nearest_enemy_dist = distance
                        nearest_enemy = enemy
            bot.enemy = nearest_enemy

    def update_position(self, bot):
        if bot.state != "blocked":
            self.avoid_collision(bot)
            self.attack(bot)
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
                else:
                    self.choose_factory(bot)

            elif bot.state == 'landing':
                if np.linalg.norm(
                        bot.position - bot.home_position) < 0.3:  # FIXME подумать на счет landing, успеет ли
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

    @staticmethod
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

        if bot.enemy and np.linalg.norm(bot.enemy.position - bot.position) < 1.0:  # FIXME вот тут тоже жоска подумать
            packet['fire_btn'] = 1
            bot.enemy = None

        return packet


def main():
    init_data = parser.load_init_game_data('jsons/init_game.json')

    teams = init_data.player_manager
    polygons = init_data.polygon_manager
    home_points = [polygon for polygon in polygons if polygon.role == "TakeoffArea_RolePolygon"]

    bots = []
    players = []
    for team in teams:
        for player in team.players:
            if player.method_control_obj == "BotControl":
                bots.append(parser.Pioneer(
                    id=int(player.robot),
                    position=np.array(
                        next((home.position for home in home_points if home.id == int(player.home_object)), None)),
                    home_point_id=int(player.home_object),
                    num_bullets=0,
                    end_position=None,  # FIXME надо тоже подумать мб
                    state="landed_home",
                    has_cargo=False,
                    velocity=np.array([0, 0, 0])
                ))
    controller = BotsController(bots, players, polygons)
    while True:  # ну тут не while True, а while game_time из init_data
        controller.update_game_state()
        for bot in controller.bots:
            controller.update_position(bot)
            command = controller.generate_command(bot)  # ну тут тоже чутка долепить


if __name__ == "__main__":
    main()
