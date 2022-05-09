# Imports
import apriltag
import cv2


# Function declarations
def draw(frame, results):
    cX = 0
    cY = 0
    ptA = 0
    ptB = 0
    ptC = 0
    ptD = 0
    for r in results:
        (ptA, ptB, ptC, ptD) = r.corners
        ptB = (int(ptB[0]), int(ptB[1]))
        ptC = (int(ptC[0]), int(ptC[1]))
        ptD = (int(ptD[0]), int(ptD[1]))
        ptA = (int(ptA[0]), int(ptA[1]))
        # draw the bounding box of the AprilTag detection
        cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
        cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
        cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
        cv2.line(frame, ptD, ptA, (0, 255, 0), 2)
        # draw the center (x, y)-coordinates of the AprilTag
        (cX, cY) = (int(r.center[0]), int(r.center[1]))
        cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)
        cv2.circle(frame, (ptA[0], ptA[1]), 5, (178, 39, 255), -1)
        cv2.circle(frame, (ptB[0], ptB[1]), 5, (255, 92, 68), -1)
        cv2.circle(frame, (ptC[0], ptC[1]), 5, (23, 251, 255), -1)
        cv2.circle(frame, (ptD[0], ptD[1]), 5, (47, 255, 26), -1)
        # draw the tag family on the frame
        tagFamily = r.tag_family.decode("utf-8")
        cv2.putText(frame, tagFamily, (ptA[0], ptA[1] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # show the output frame after AprilTag detection
    centers = [[cX, cY], [ptA[0], ptA[1]], [ptB[0], ptB[1]], [ptC[0], ptC[1]], [ptD[0], ptD[1]]]
    return frame, centers


def detectAprilTag(frame):
    centers = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    options = apriltag.DetectorOptions(families="tag36h11")
    detector = apriltag.Detector(options)
    results = detector.detect(gray)
    if len(results) > 0:
        frame, centers = draw(frame, results)
    return frame, centers
