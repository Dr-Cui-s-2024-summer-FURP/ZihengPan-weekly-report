import numpy as np
import open3d as o3d
import cv2
import matplotlib.pyplot as plt

# 读取点云数据
data = np.loadtxt('output_point_cloud_with_normals.txt')

# 提取坐标 (x, y, z)
points = data[:, 0:3]

# 可视化点云数据
def plot_point_cloud(points, title="Point Cloud"):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title(title)
    plt.show()

plot_point_cloud(points, title="Original Point Cloud")

# 点云滤波：去除噪声点
def remove_noise(points, nb_neighbors=20, std_ratio=2.0):
    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(points)
    cl, ind = cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    return np.asarray(cl.points)

filtered_points = remove_noise(points)

# 可视化滤波后的点云
plot_point_cloud(filtered_points, title="Filtered Point Cloud")

# 将点云转换为图像
def points_to_image(points, image_size=(1000, 1000), scale=100):
    image = np.zeros(image_size, dtype=np.uint8)
    for point in points:
        x, y = point
        img_x = int((x - np.min(points[:, 0])) * scale)
        img_y = int((y - np.min(points[:, 1])) * scale)
        if 0 <= img_x < image_size[0] and 0 <= img_y < image_size[1]:
            image[img_y, img_x] = 255
    return image

# 处理一个投影面的点云数据
def process_projection(points, projection_axes, image_size=(1000, 1000), scale=100, threshold=50, minLineLength=10, maxLineGap=5):
    projected_points = points[:, projection_axes]
    image = points_to_image(projected_points, image_size, scale)
    
    # 使用Hough变换检测线条
    lines = cv2.HoughLinesP(image, 1, np.pi / 180, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)
    
    # 可视化结果
    plt.figure(figsize=(10, 10))
    plt.imshow(image, cmap='gray')
    
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                plt.plot([x1, x2], [y1, y2], 'r')
        print(f"Detected {len(lines)} lines.")
    else:
        print("No lines detected. Consider adjusting Hough transform parameters.")
    
    plt.title(f'Detected Lines on Projection: {projection_axes}')
    plt.show()

# 投影到XY平面
process_projection(filtered_points, [0, 1], image_size=(1000, 1000), scale=100, threshold=50, minLineLength=10, maxLineGap=5)

# 投影到XZ平面
process_projection(filtered_points, [0, 2], image_size=(1000, 1000), scale=100, threshold=50, minLineLength=10, maxLineGap=5)

# 投影到YZ平面
process_projection(filtered_points, [1, 2], image_size=(1000, 1000), scale=100, threshold=50, minLineLength=10, maxLineGap=5)
