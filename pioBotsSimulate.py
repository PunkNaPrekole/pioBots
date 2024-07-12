import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class Drone:
    def __init__(self, id, home_position, team, charge, freeze=False, health=100, flight_altitude=1.0, landing_speed=0.2, takeoff_speed=0.2):
        self.id = id
        self.home_position = np.array(home_position)
        self.team = team
        self.charge = charge
        self.freeze = freeze
        self.health = health
        self.position = np.array(home_position)  # Изначальная позиция равна домашней точке
        self.end_position = None
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.flight_altitude = flight_altitude
        self.state = 'taking_off'
        self.landing_speed = landing_speed
        self.takeoff_speed = takeoff_speed
        self.wander_probability = 0.5
        self.has_cargo = False
        self.unfreeze_interval = 10
        self.freeze_timer = 0

    def update_position(self):
        if not self.freeze:
            if self.state == 'taking_off':
                if self.position[2] < self.flight_altitude:
                    self.position[2] += self.takeoff_speed
                else:
                    self.position[2] = self.flight_altitude
                    if self.has_cargo:
                        self.state = 'returning_home'
                    else:
                        self.state = 'flying_to_factory'

            elif self.state == 'flying_to_factory':
                if self.end_position is not None:
                    direction = self.end_position - self.position
                    direction[2] = 0
                    distance = np.linalg.norm(direction)
                    if distance > 0.3:
                        self.velocity = (direction / distance) / 3
                        if np.random.rand() < self.wander_probability:
                            self.velocity[:2] += np.random.uniform(-0.1, 0.1, size=2)
                    else:
                        self.velocity = np.array([0.0, 0.0, 0.0])
                        self.state = 'landing'

                    self.position[:2] += self.velocity[:2]
                    self.position[2] = self.flight_altitude

            elif self.state == 'landing':
                if self.position[2] > 0:
                    self.position[2] -= self.landing_speed
                else:
                    self.position[2] = 0
                    if self.has_cargo and np.linalg.norm(self.position[:2] - self.home_position[:2]) < 1.0:
                        self.state = 'landed_home'
                    else:
                        self.state = 'landed_factory'

            elif self.state == 'landed_factory':
                self.state = 'waiting_for_cargo'


            elif self.state == 'waiting_for_cargo':
                for factory in factories:
                    if np.linalg.norm(self.position[:2] - factory.position[:2]) < 0.3 and factory.has_cargo:
                        self.has_cargo = True
                        factory.has_cargo = False
                        self.state = 'taking_off'
                        self.end_position = self.home_position
                        break

            elif self.state == 'returning_home':
                direction = self.end_position - self.position
                direction[2] = 0
                distance = np.linalg.norm(direction)
                if distance > 0.5:
                    self.velocity = direction / distance
                    if np.random.rand() < self.wander_probability:
                        self.velocity[:2] += np.random.uniform(-0.1, 0.1, size=2)
                else:
                    self.velocity = np.array([0.0, 0.0, 0.0])
                    self.state = 'landing'

                self.position[:2] += self.velocity[:2]
                self.position[2] = self.flight_altitude

            elif self.state == 'landed_home':
                self.has_cargo = False
                self.end_position = None
                self.state = 'taking_off'

    def update(self):
        if self.freeze:
            self.freeze_timer += 1
            if self.freeze_timer >= self.unfreeze_interval:
                self.freeze = False
                self.freeze_timer = 0


class Factory:
    def __init__(self, position, cargo_interval=50):
        self.position = np.array(position)
        self.visitor = None
        self.has_cargo = False
        self.cargo_interval = cargo_interval
        self.cargo_timer = 0

    def update(self):
        self.cargo_timer += 1
        if self.cargo_timer >= self.cargo_interval:
            self.has_cargo = True
            self.cargo_timer = 0


def avoid_collisions(drones, enemy_drones, min_distance=0.3):
    all_drones = drones + enemy_drones
    for i, drone in enumerate(drones):
        for j, other_drone in enumerate(all_drones):
            if i != j:
                distance = np.linalg.norm(drone.position - other_drone.position)
                if distance < min_distance:
                    repulsion = (drone.position - other_drone.position) / distance
                    perpendicular = np.array([-repulsion[1], repulsion[0], 0])
                    if np.dot(drone.velocity[:2], perpendicular[:2]) < 0:
                        perpendicular = -perpendicular
                    drone.position += repulsion + perpendicular * 0.5


def assign_factories(drones, factories):
    assigned_factories = set()
    for drone in drones:
        if drone.state == 'taking_off' and not drone.has_cargo and drone.end_position is None:
            min_distance = float('inf')
            closest_factory = None
            for factory in factories:
                if tuple(factory.position) not in assigned_factories and factory.visitor != drone.team:
                    distance = np.linalg.norm(drone.position - factory.position)
                    if distance < min_distance:
                        min_distance = distance
                        closest_factory = factory
            if closest_factory is not None:
                drone.end_position = closest_factory.position
                assigned_factories.add(tuple(closest_factory.position))


def attack(drone, enemy_drones):
    if not drone.has_cargo:
        nearest_enemy = None
        nearest_enemy_distance = float("inf")
        for enemy in enemy_drones:
            distance = np.linalg.norm(enemy.position - drone.position)
            if distance < nearest_enemy_distance and not enemy.freeze:
                nearest_enemy_distance = distance
                nearest_enemy = enemy
        if nearest_enemy and nearest_enemy_distance < 1.0:
            drone.charge -= 1
            nearest_enemy.freeze = True
            nearest_enemy.cargo = False


def update_plot(frame):
    global drones, enemy_drones, factories, ax, scatter

    for factory in factories:
        factory.update()

    assign_factories(drones, factories)
    assign_factories(enemy_drones, factories)
    for drone in drones:
        attack(drone, enemy_drones)

    avoid_collisions(drones, enemy_drones)

    for drone in drones + enemy_drones:
        drone.update_position()
        drone.update()
        print(f"drone {drone.id} state:{drone.state}")
        #print(f"Drone _{drone.id} state: {drone.state}")

    colors = ['blue' if not drone.has_cargo else 'orange' for drone in drones]
    colors += ['red' if not drone.has_cargo else 'purple' for drone in enemy_drones]

    positions = np.array([drone.position for drone in drones + enemy_drones])
    scatter._offsets3d = (positions[:, 0], positions[:, 1], positions[:, 2])
    scatter.set_facecolor(colors)

    factory_colors = ['green' if not factory.has_cargo else 'yellow' for factory in factories]
    factory_positions = np.array([factory.position for factory in factories])
    ax.scatter(factory_positions[:, 0], factory_positions[:, 1], factory_positions[:, 2], marker='s', c=factory_colors, label='Factories')

    return scatter,


def main():
    global drones, enemy_drones, factories, ax, scatter

    drones = [
        Drone(1, home_position=[3.25, 0.25, 0.0], team=1, charge=1),
        Drone(2, home_position=[-0.25, 3.75, 0.0], team=1, charge=1),
        Drone(3, home_position=[-1.25, -4.75, 0.0], team=1, charge=1)
    ]
    enemy_drones = [
        Drone(5, home_position=[2.75, -4.75, 0.0], team=2, charge=1),
        Drone(6, home_position=[-1.25, -0.75, 0.0], team=2, charge=1),
        Drone(7, home_position=[-5.25, 4.25, 0.0], team=2, charge=1)
    ]
    factories = [
        Factory([3.25, 4.25, 0]),
        Factory([5.25, -2.75, 0]),
        Factory([0.75, -2.25, 0]),
        Factory([-3.25, 1.25, 0]),
        Factory([-4.25, -3.25, 0]),
        Factory([0.25, 1.25, 0])
    ]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter([], [], [], label='Drones')
    enemy_drone_legend = ax.scatter([], [], color='red', label='Enemy Drones')

    ax.scatter([drone.home_position[0] for drone in drones + enemy_drones],
               [drone.home_position[1] for drone in drones + enemy_drones],
               [drone.home_position[2] for drone in drones + enemy_drones],
               marker='^', color='purple', label='Home')
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_zlim(0, 3)
    ax.legend()

    ani = FuncAnimation(fig, update_plot, frames=range(1000), interval=200, blit=False)
    plt.show()


if __name__ == "__main__":
    main()
