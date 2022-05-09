# Imports
import numpy as np
import cv2


# Function declarations
def undistortion(frame, calib_param):
	frame = cv2.undistort(frame, calib_param[0], calib_param[1], None, calib_param[2])
	x, y, w, h = calib_param[3]
	return frame[y:y + h, x:x + w]


def get_chessboard_points(chessboard_shape, dx, dy):
	points = []
	for i in range(chessboard_shape[1]):
		points.extend([i * dx, j * dy, 0] for j in range(chessboard_shape[0]))
	return np.array(points)


def calibrateCamera(calib_img):
	print("Calibrating ...")
	print(len(calib_img))

	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

	# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
	objp = np.zeros((6 * 9, 3), np.float32)
	objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

	# Arrays to store object points and image points from all the images.
	world_pts = []  # 3d point in real world space
	img_pts = []  # 2d points in image plane.

	gray = None
	img = None

	for i, img in enumerate(calib_img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		# Find the chess board corners
		ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

		# If found, add object points, image points (after refining them)
		if ret:
			world_pts.append(objp)
			corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
			img_pts.append(corners2)

			# Draw and display the corners
			img = cv2.drawChessboardCorners(img, (9, 6), corners2, ret)
			d = f"img {i}"
			cv2.imshow(d, img)
			cv2.moveWindow(d, 0, 0)

	rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(world_pts, img_pts, gray.shape[::-1], None, None)

	h, w = img.shape[:2]
	new_K, roi = cv2.getOptimalNewCameraMatrix(K, dist, (w, h), 1, (w, h))

	print("Intrisincs :", K)
	print("New intrisincs :", new_K)
	print("Dist coef :", dist)
	print("The overall RMS re-projection error :", rms)

	cv2.waitKey()
	cv2.destroyAllWindows()

	return [K, dist, new_K, roi]


def mainCalibration(calibrated, calib_img, calib_img_nb, frame, key):
	if not calibrated:
		if len(calib_img) < calib_img_nb and key == 99:
			calib_img.append(frame)
			print(f"Picture saved ! You need {calib_img_nb - len(calib_img)} more")
		if len(calib_img) == calib_img_nb:
			calib_param = calibrateCamera(calib_img)
			return True, calib_param
	return calibrated, []
