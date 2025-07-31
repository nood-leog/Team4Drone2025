import cv2
import numpy as np

class LineTracer:
    def __init__(self, movement):
        self.movement = movement
        # RGB target color (default: yellow)
        self.target_r = 255
        self.target_g = 255
        self.target_b = 0
        # Color sensitivity (how much deviation from target color is allowed)
        self.sensitivity = 30
        # Movement control
        self.speed = 0
        self.flag = 0
        # Status tracking
        self.status_message = "Initializing..."
        self.status_color = (255, 255, 255)  # White text by default

    def create_trackbars(self, window_title):
        # Create window for trackbars
        cv2.namedWindow(window_title)
        # RGB target color controls
        cv2.createTrackbar("Target R", window_title, self.target_r, 255, self.on_trackbar)
        cv2.createTrackbar("Target G", window_title, self.target_g, 255, self.on_trackbar)
        cv2.createTrackbar("Target B", window_title, self.target_b, 255, self.on_trackbar)
        # Sensitivity control
        cv2.createTrackbar("Sensitivity", window_title, self.sensitivity, 100, self.on_trackbar)
        # Speed control
        cv2.createTrackbar("Speed", window_title, self.speed, 100, self.on_trackbar)

    def on_trackbar(self, val):
        pass

    def process_frame(self, frame):
        # Resize and crop ROI
        small_image = cv2.resize(frame, dsize=(480, 360))
        roi_image = small_image[250:359, 0:479]

        # Get current trackbar positions
        self.target_r = cv2.getTrackbarPos("Target R", "OpenCV Window")
        self.target_g = cv2.getTrackbarPos("Target G", "OpenCV Window")
        self.target_b = cv2.getTrackbarPos("Target B", "OpenCV Window")
        self.sensitivity = cv2.getTrackbarPos("Sensitivity", "OpenCV Window")
        self.speed = cv2.getTrackbarPos("Speed", "OpenCV Window")

        # Create color bounds based on target color and sensitivity
        lower_bound = np.array([
            max(0, self.target_b - self.sensitivity),
            max(0, self.target_g - self.sensitivity),
            max(0, self.target_r - self.sensitivity)
        ])
        upper_bound = np.array([
            min(255, self.target_b + self.sensitivity),
            min(255, self.target_g + self.sensitivity),
            min(255, self.target_r + self.sensitivity)
        ])

        # Create mask for color detection
        mask = cv2.inRange(roi_image, lower_bound, upper_bound)
        
        # Apply morphological operations
        kernel = np.ones((15, 15), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        
        # Find contours
        masked_image = cv2.bitwise_and(roi_image, roi_image, mask=mask)
        
        # Connected components analysis
        num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(mask)
        num_labels = num_labels - 1
        
        # Create status overlay background
        status_overlay = np.zeros((30, 480, 3), dtype=np.uint8)
        
        if num_labels >= 1:
            stats = np.delete(stats, 0, 0)
            center = np.delete(center, 0, 0)
            
            max_index = np.argmax(stats[:, 4])
            x = stats[max_index][0]
            y = stats[max_index][1]
            w = stats[max_index][2]
            h = stats[max_index][3]
            s = stats[max_index][4]
            mx = int(center[max_index][0])
            my = int(center[max_index][1])

            # Draw bounding box and area
            cv2.rectangle(masked_image, (x, y), (x + w, y + h), (255, 0, 255), 2)
            cv2.putText(masked_image, f"Area: {s}", (x, y + h + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

            if self.flag == 1:
                dx = 1.0 * (240 - mx)
                if abs(dx) < 50.0:
                    self.status_message = "Moving Forward!"
                    self.status_color = (0, 255, 0)  # Green
                    d = 0.0
                else:
                    if dx > 0:
                        self.status_message = "Turning Right..."
                        self.status_color = (255, 165, 0)  # Orange
                    else:
                        self.status_message = "Turning Left..."
                        self.status_color = (255, 165, 0)  # Orange
                    d = -dx
                
                d = 70 if d > 70.0 else d
                d = -70 if d < -70.0 else d
                
                if self.speed == 0:
                    self.status_message = "Stopped"
                    self.status_color = (0, 0, 255)  # Red
                
                self.movement.send_rc_control(0, self.speed, 0, int(d))
            else:
                self.status_message = "Line Found! (Control Disabled)"
                self.status_color = (255, 255, 0)  # Yellow
        else:
            self.status_message = "Searching for Line..."
            self.status_color = (128, 0, 128)  # Purple

        # Draw status message
        cv2.rectangle(masked_image, (0, 0), (480, 30), (0, 0, 0), -1)
        cv2.putText(masked_image, self.status_message, (10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.status_color, 2)
        
        # Add additional telemetry
        telemetry = f"Speed: {self.speed}% | Sensitivity: {self.sensitivity}"
        cv2.putText(masked_image, telemetry, (240, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        return masked_image

    def __del__(self):
        cv2.destroyAllWindows()