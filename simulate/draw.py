import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def draw_points_and_polygons(points, polygons):
    home_points, fabric_points, recharge_points = points
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_zlim(0, 4)

    ax.grid(True)
    z_points = 0.0
    x_points, y_points = zip(*home_points)
    ax.scatter(x_points, y_points, z_points, color='blue', label='home points', marker='s')

    x_points, y_points = zip(*fabric_points)
    ax.scatter(x_points, y_points, z_points, color='green', label='fabrics', marker='s')

    x_points, y_points = zip(*recharge_points)
    ax.scatter(x_points, y_points, z_points, color='purple', label='recharge', marker='s')

    colors = ['red', 'orange', 'purple', 'green']

    for i, polygon_points in enumerate(polygons):
        if polygon_points:
            polygon_points.append(polygon_points[0])

            x_poly, y_poly = zip(*polygon_points)

            ax.plot(x_poly, y_poly, z_points, marker='o', linestyle='-', color=colors[i % len(colors)],
                    label=f'anti block zone {i + 1}')

    ax.legend(loc='upper right', bbox_to_anchor=(1, 1))
    plt.show()
