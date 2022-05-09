#!/usr/bin/python3

# Importing python3 from local, just use "python3 <binary>" if is not the same location

# Imports
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

import arguments
import calibrate
import aprilTag

plots = []


# Function declarations
def getCameraPos(R, t, axes):
    global plots

    C = - R.T @ t
    lenght = 5

    camera_points = np.array([[0, 0, 0, 1],  # origen
                              [lenght, 0, 0, 1],  # Punto en eje X
                              [0, lenght, 0, 1],  # Punto en eje Y
                              [0, 0, lenght, 1]])  # Punto en eje Z

    camera_points = camera_points.T
    x_scene = R.T @ (np.array([camera_points[0:3, 1]]).T - t)
    y_scene = R.T @ (np.array([camera_points[0:3, 2]]).T - t)
    z_scene = R.T @ (np.array([camera_points[0:3, 3]]).T - t)

    l1 = axes.plot3D([C[0][0], x_scene[0][0]], [C[1][0], x_scene[1][0]], [C[2][0], x_scene[2][0]], 'r')
    l2 = axes.plot3D([C[0][0], y_scene[0][0]], [C[1][0], y_scene[1][0]], [C[2][0], y_scene[2][0]], 'g')
    l3 = axes.plot3D([C[0][0], z_scene[0][0]], [C[1][0], z_scene[1][0]], [C[2][0], z_scene[2][0]], 'b')
    p = axes.scatter3D(C[0], C[1], C[2])

    plots.append([l1, l2, l3, p])
    if len(plots) >= 10:
        plots = []
        plt.clf()
        axes = plotStart(False)
    plt.draw()
    plt.pause(0.001)
    return axes


def drawAxis(R, tvec, calib_param, points_2D, frame):
    camera_vector_3d, _ = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), R, tvec, calib_param[2], calib_param[1])
    point1 = (int(points_2D[0][0]), int(points_2D[0][1]))
    point2 = (int(camera_vector_3d[0][0][0]), int(camera_vector_3d[0][0][1]))
    cv2.line(frame, point1, point2, (63, 87, 48), 2)


def plotStart(init):
    if init:
        plt.figure()
    length = 12
    axes = plt.axes(projection='3d')
    axes.set_xlabel('X')
    axes.set_ylabel('Y')
    axes.set_zlabel('Z')
    plt.ion()
    plt.show()

    axes.scatter3D(0, 0, 0)
    axes.plot3D([0, 0, length], [0, 0, 0], [0, 0, 0], 'r-', linewidth=3)
    axes.plot3D([0, 0, 0], [0, 0, length], [0, 0, 0], 'g-', linewidth=3)
    axes.plot3D([0, 0, 0], [0, 0, 0], [0, 0, length], 'b-', linewidth=3)
    plt.draw()
    plt.pause(0.001)

    return axes


def transform2dTo3d(centers, calib_param, frame):
    points_2D = np.array([
        (centers[0][0], centers[0][1]),
        (centers[1][0], centers[1][1]),
        (centers[2][0], centers[2][1]),
        (centers[3][0], centers[3][1]),
        (centers[4][0], centers[4][1]),
    ], dtype="double")
    points_3D = np.array([
        (0.0, 0.0, 0.0),
        (-7.7, -7.7, 0.0),
        (-7.7, 7.7, 0.0),
        (7.7, 7.7, 0.0),
        (7.7, -7.7, 0.0),
    ])
    success, rvec, tvec = cv2.solvePnP(points_3D, points_2D, calib_param[2], calib_param[1], flags=0)

    R = 0
    if success:
        R, _ = cv2.Rodrigues(rvec)
        drawAxis(R, tvec, calib_param, points_2D, frame)

    return success, R, rvec, tvec


def resizeFrame(frame, percent):
    width = int(frame.shape[1] * percent // 100)
    height = int(frame.shape[0] * percent // 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)


def mainLoop(mode, url):
    calibrated = False
    calib_img = []
    calib_param = []
    calib_img_nb = 6

    cam = cv2.VideoCapture(0) if mode == "webcam" else cv2.VideoCapture(url)
    win_name = "Not calibrated"

    axes = plotStart(True)

    i = 0
    while True:
        _, frame = cam.read()
        frame = resizeFrame(frame, 50)
        key = cv2.waitKey(1)
        if not calibrated:
            calibrated, calib_param = calibrate.mainCalibration(calibrated, calib_img, calib_img_nb, frame, key)
            if calib_param:
                win_name = "Calibrated"
        else:
            frame = calibrate.undistortion(frame, calib_param)
            frame, centers = aprilTag.detectAprilTag(frame)
            if centers:
                success, R, rvec, tvec = transform2dTo3d(centers, calib_param, frame)
                if success and i >= 5:
                    axes = getCameraPos(R, tvec, axes)
                    i = 0

        cv2.imshow(win_name, frame)
        cv2.moveWindow(win_name, 0, 0)
        if key in [8, 27, 32, 113]:
            break
        i += 1

    cam.release()
    cv2.destroyAllWindows()


def main():
    mode, url = arguments.getArguments()
    mainLoop(mode, url)


# Main body
if __name__ == '__main__':
    main()
