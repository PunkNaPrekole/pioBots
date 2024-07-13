import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

class AnimatedPlot:
    def __init__(self, points, polygons, moving_objects):
        self.home_points, self.fabric_points, self.recharge_points = points
        self.polygons = polygons
        self.moving_objects = moving_objects

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

        self.ax.set_xlim(-6, 6)
        self.ax.set_ylim(-6, 6)
        self.ax.set_zlim(0, 4)

        self.ax.grid(True)
        self.z_points = 0.0

        self.init_plot()

    def init_plot(self):
        x_points, y_points = zip(*self.home_points)
        self.ax.scatter(x_points, y_points, self.z_points, color='blue', label='fabrics', marker='s')

        x_points, y_points = zip(*self.fabric_points)
        self.ax.scatter(x_points, y_points, self.z_points, color='green', label='home points', marker='s')

        x_points, y_points = zip(*self.recharge_points)
        self.ax.scatter(x_points, y_points, self.z_points, color='purple', label='recharge', marker='s')

        colors = ['red', 'orange', 'purple', 'green']

        for i, polygon_points in enumerate(self.polygons):
            if polygon_points:
                polygon_points.append(polygon_points[0])
                x_poly, y_poly = zip(*polygon_points)
                self.ax.plot(x_poly, y_poly, self.z_points, marker='o', linestyle='-', color=colors[i % len(colors)],
                             label=f'anti block zone {i + 1}')

        self.moving_scatters = [self.ax.scatter([], [], [], color='red', label=f'moving object {i}') for i in range(len(self.moving_objects))]

        self.ax.legend(loc='upper right', bbox_to_anchor=(1, 1))

    def update_plot(self, frame):
        for i, scatter in enumerate(self.moving_scatters):
            obj = self.moving_objects[i]
            scatter._offsets3d = (obj.current_pos[0], obj.current_pos[1], obj.current_pos[2])

    def animate(self, interval=100):
        self.ani = FuncAnimation(self.fig, self.update_plot, frames=range(100), interval=interval)
        plt.show()


def draw_points_and_polygons(points, polygons, moving_objects):
    plot = AnimatedPlot(points, polygons, moving_objects)
    plot.animate()
