import numpy as np
import parser


class BotsController:
    """
    Контроллер управления пионерами и эдуботами.
    """

    def __init__(self, bots, players, polygons):
        self.bots = bots
        self.players = players
        self.polygons = polygons
        self.fabrics = [polygon for polygon in polygons if polygon.role == "Fabric_RolePolygon"]
        self.ab_zones = [polygon for polygon in polygons if polygon.role == "AntiBlockZone_RolePolygon"]
        self.home_points = [polygon for polygon in polygons if polygon.role == "TakeoffArea_RolePolygon"]
        self.charge_points = [polygon for polygon in polygons if polygon.role == "Weapoint_RolePolygon"]
        self.game_state = None
        self.min_distance = 0.3
        self.min_attack_dist = 0.5


    def update_game_state(self):
        """Обновляет состояние игры"""
        self.game_state = parser.load_in_game_data("jsons/in_game.json")
        for bot in self.bots:
            updated_info = next((p for team in self.game_state.players_info for p in team.players if p.id == bot.id))
            bot.position = np.array(updated_info.current_pos[:3])
            bot.has_cargo = updated_info.data_role.get("is_cargo", False)
            bot.num_bullets = updated_info.data_role.get("num_bullet", 0)
        for polygon in self.fabrics:
            updated_polygon = next((poly for poly in self.game_state.polygon_manager if poly.id == polygon.id))
            polygon.data_role = updated_polygon.data_role
            polygon.vis_info = updated_polygon.vis_info
        for polygon in self.home_points:
            updated_polygon = next((poly for poly in self.game_state.polygon_manager if poly.id == polygon.id))
            polygon.data_role = updated_polygon.data_role
            polygon.vis_info = updated_polygon.vis_info
        for polygon in self.charge_points:
            updated_polygon = next((poly for poly in self.game_state.polygon_manager if poly.id == polygon.id))
            polygon.data_role = updated_polygon.data_role
            polygon.vis_info = updated_polygon.vis_info


    def choose_enemy(self, bot):
        min_distance = float('inf')
        for enemy in self.players:
            if enemy.has_cargo:
                distance = np.linalg.norm(bot.position[:2] - enemy.position[:2])
                if distance < min_distance:
                    min_distance = distance
                    bot.end_position = enemy.position
                    bot.state = "persecution"


    def choose_action(self, bot):
        """Выбирает действие"""
        best_fabric = None
        min_distance = float('inf')
        for fabric in self.fabrics:
            if fabric.data_role.get("is_cargo"):
                distance = np.linalg.norm(bot.position[:2] - fabric.position[:2])
                if distance < min_distance:
                    min_distance = distance
                    best_fabric = fabric
        if best_fabric:
            bot.end_position = best_fabric.position
            bot.state = "moving"
        elif bot.num_bullets <= 2:
            point = None
            for polygon in self.charge_points:
                if polygon.id in bot.filter:
                    point = polygon
            bot.end_position = point.position
            bot.state = "moving"
        else:
            self.choose_enemy(bot)


    def check_enemy(self, bot):
        for enemy in self.players:
            distance = np.linalg.norm(enemy.position - bot.position)
            if distance <= self.min_attack_dist:
                bot.enemy = True
                break


    def avoid_collision(self, bot):
        """Избегание столкновений с другими ботами."""
        for other_bot in self.bots + self.players:
            if bot.id != other_bot.id:
                distance = np.linalg.norm(bot.position - other_bot.position)
                if distance < self.min_distance:
                    repulsion = (bot.position - other_bot.position) / distance
                    bot.velocity += repulsion * 0.1


    def update_position(self, bot):
        if bot.state == 'moving':
            direction = bot.end_position[:2] - bot.position[:2]
            distance = np.linalg.norm(direction)
            if distance <= 0.3:
                bot.velocity = np.array([0.0, 0.0, 0.0])
                bot.state = 'landing'
            else:
                bot.velocity = direction / distance * 0.5
            self.avoid_collision(bot)
        elif bot.state == 'persecution':
            direction = bot.end_position[:2] - bot.position[:2]
            distance = np.linalg.norm(direction)
            if distance <= self.min_attack_dist:
                bot.enemy = True
                self.choose_action(bot)
            else:
                bot.velocity = direction / distance * 0.5
            self.avoid_collision(bot)
        elif bot.state == 'taking_off':
            if bot.has_cargo:
                bot.end_position = bot.home_point
                bot.state = 'moving'
            else:
                self.choose_action(bot)
        elif bot.state == 'landing':
            distance = np.linalg.norm(bot.position - bot.end_position)
            if distance < 0.3:
                if np.array_equal(bot.end_position, bot.home_point):
                    bot.state = 'landed_home'
                else:
                    bot.state = 'landed_fabric'
        elif bot.state == 'landed_home':
            if not bot.has_cargo:
                bot.state = 'taking_off'
        else:
            if bot.has_cargo:
                bot.state = 'taking_off'

    @staticmethod
    def generate_command(bot):
        """Генерирует пакет команд для управления ботом."""
        axis_0 = int(1500 + bot.velocity[0] * 500)
        axis_1 = int(1500 + bot.velocity[1] * 500)
        axis_2 = int(1500 + bot.velocity[2] * 500)
        command = {
            'axis_0': max(1000, min(axis_0, 2000)),
            'axis_1': max(1000, min(axis_1, 2000)),
            'axis_2': max(1000, min(axis_2, 2000)) if bot.type == "PioneerObject" else 1500,
            'axis_3': 1500,
            'takeoff': 1 if bot.state == "taking_off" else 0,
            'land': 1 if bot.state == "landing" else 0,
            'cargo_btn': 1 if bot.state == "at_factory" else 0,
            'fire_btn': 1 if bot.enemy else 0,
        }
        bot.enemy = False
        return command


def main():
    init_data = parser.load_init_game_data('jsons/init_game.json')
    teams = init_data.player_manager
    polygons = [parser.Polygon(
        id=polygon.id,
        position=polygon.position,
        role=polygon.role,
        vis_info=polygon.vis_info,
        data_role={}
    ) for polygon in init_data.polygon_manager]

    bots = []
    players = []
    for team in teams:
        if team.name_team == 'pioBots':
            for player in team.players:
                home_point = np.array(polygon.position for polygon in polygons if polygon.id == player.home_object)
                bots.append(parser.Bot(
                    id=int(player.robot),
                    position=home_point,
                    home_point=home_point,
                    velocity=np.array([0, 0, 0]),
                    has_cargo=False,
                    state="taking_off",
                    num_bullets=0,
                    type=player.control_object,
                    filter=player.filter,
                     end_position=None,
                    enemy=False
                ))
        else:
            for player in team.players:
                players.append(parser.Enemy(
                    id=int(player.robot),
                    position=np.array(player.home_object),
                    has_cargo=False,
                    num_bullets=0
                ))

    controller = BotsController(bots, players, polygons)

    while True:
        controller.update_game_state()
        for bot in controller.bots:
            command = controller.generate_command(bot)
            controller.update_position(bot)
            print(f"Bot {bot.id} Command: {command}")
