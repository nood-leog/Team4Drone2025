
import cv2
import numpy as np

class LineTracer:
    def __init__(self, movement):
        self.movement = movement
        self.h_min = 0
        self.h_max = 179
        self.s_min = 0
        self.s_max = 255
        self.v_min = 0
        self.v_max = 255
        self.flag = 0
        self.b = 0

    def create_trackbars(self, window_title):
        cv2.createTrackbar("H_min", window_title, self.h_min, 179, self.on_trackbar)
        cv2.createTrackbar("H_max", window_title, self.h_max, 179, self.on_trackbar)
        cv2.createTrackbar("S_min", window_title, self.s_min, 255, self.on_trackbar)
        cv2.createTrackbar("S_max", window_title, self.s_max, 255, self.on_trackbar)
        cv2.createTrackbar("V_min", window_title, self.v_min, 255, self.on_trackbar)
        cv2.createTrackbar("V_max", window_title, self.v_max, 255, self.on_trackbar)

    def on_trackbar(self, val):
        pass

    def process_frame(self, frame):
        small_image = cv2.resize(frame, dsize=(480, 360))
        bgr_image = small_image[250:359, 0:479]
        hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

        self.h_min = cv2.getTrackbarPos("H_min", "OpenCV Window")
        self.h_max = cv2.getTrackbarPos("H_max", "OpenCV Window")
        self.s_min = cv2.getTrackbarPos("S_min", "OpenCV Window")
        self.s_max = cv2.getTrackbarPos("S_max", "OpenCV Window")
        self.v_min = cv2.getTrackbarPos("V_min", "OpenCV Window")
        self.v_max = cv2.getTrackbarPos("V_max", "OpenCV Window")

        bin_image = cv2.inRange(hsv_image, (self.h_min, self.s_min, self.v_min), (self.h_max, self.s_max, self.v_max))
        kernel = np.ones((15, 15), np.uint8)
        dilation_image = cv2.dilate(bin_image, kernel, iterations=1)
        masked_image = cv2.bitwise_and(hsv_image, hsv_image, mask=dilation_image)

        num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(dilation_image)
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        center = np.delete(center, 0, 0)

        if num_labels >= 1:
            max_index = np.argmax(stats[:, 4])
            x = stats[max_index][0]
            y = stats[max_index][1]
            w = stats[max_index][2]
            h = stats[max_index][3]
            s = stats[max_index][4]
            mx = int(center[max_index][0])
            my = int(center[max_index][1])

            cv2.rectangle(masked_image, (x, y), (x + w, y + h), (255, 0, 255))
            cv2.putText(masked_image, "%d" % (s), (x, y + h + 15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))

            if self.flag == 1:
                dx = 1.0 * (240 - mx)
                d = 0.0 if abs(dx) < 50.0 else dx
                d = -d
                d = 70 if d > 70.0 else d
                d = -70 if d < -70.0 else d
                self.movement.send_rc_control(0, int(self.b), 0, int(d))

        return masked_image
