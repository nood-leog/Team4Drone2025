import cv2
import numpy as np
from typing import Tuple, Optional
import time

class LineTracer:
    def __init__(self, movement):
        self.movement = movement
        
        # Performance optimization
        self.frame_width = 480
        self.frame_height = 360
        self.roi_height = 100  # Smaller ROI for faster processing
        self.fps_limit = 30
        self.last_frame_time = 0
        
        # Line detection parameters
        self.yellow_lower = np.array([20, 100, 100])  # HSV yellow range
        self.yellow_upper = np.array([30, 255, 255])
        self.min_line_area = 500  # Minimum area to consider as valid line
        self.corner_detection_threshold = 0.8
        
        # PID Controller parameters
        self.kp = 0.8  # Proportional gain
        self.ki = 0.1  # Integral gain
        self.kd = 0.2  # Derivative gain
        self.integral = 0
        self.last_error = 0
        
        # Movement parameters
        self.base_speed = 50
        self.max_turn_speed = 70
        self.racing_altitude = 100  # cm
        self.corner_slowdown = 0.7  # Speed multiplier at corners
        
        # State tracking
        self.lost_line_counter = 0
        self.max_lost_frames = 10
        self.corner_detected = False
        self.last_valid_center = None

    def detect_line(self, roi_frame) -> Tuple[bool, Optional[np.ndarray], float]:
        """
        High-performance line detection using HSV color space
        Returns: (line_found, center_point, line_angle)
        """
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for yellow color
        mask = cv2.inRange(hsv, self.yellow_lower, self.yellow_upper)
        
        # Optimized morphological operations
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return False, None, 0.0
            
        # Get largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < self.min_line_area:
            return False, None, 0.0
            
        # Get center and angle of line
        M = cv2.moments(largest_contour)
        if M["m00"] == 0:
            return False, None, 0.0
            
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        center = np.array([cx, cy])
        
        # Calculate line angle using PCA
        points = np.float32(largest_contour).reshape(-1, 2)
        _, _, vh = np.linalg.svd(points - np.mean(points, axis=0))
        angle = np.arctan2(vh[0][1], vh[0][0])
        
        return True, center, angle

    def detect_corner(self, mask) -> bool:
        """
        Detect corners using Harris corner detector
        """
        corners = cv2.goodFeaturesToTrack(mask, 4, 0.01, 30)
        return corners is not None and len(corners) >= 2

    def calculate_pid_control(self, error: float) -> float:
        """
        PID controller for smooth line following
        """
        self.integral += error
        derivative = error - self.last_error
        self.last_error = error
        
        # Anti-windup
        self.integral = np.clip(self.integral, -100, 100)
        
        return (self.kp * error + 
                self.ki * self.integral + 
                self.kd * derivative)

    def process_frame(self, frame):
        # Frame rate control
        current_time = time.time()
        if current_time - self.last_frame_time < 1.0/self.fps_limit:
            return None
        self.last_frame_time = current_time
        
        # Resize and extract ROI
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        roi = frame[self.frame_height-self.roi_height:self.frame_height, :]
        
        # Detect line
        line_found, center, angle = self.detect_line(roi)
        
        if not line_found:
            self.lost_line_counter += 1
            if self.lost_line_counter > self.max_lost_frames:
                self.movement.send_rc_control(0, 0, 0, 0)  # Stop if line lost
                return frame
            # Use last known position if available
            if self.last_valid_center is not None:
                center = self.last_valid_center
        else:
            self.lost_line_counter = 0
            self.last_valid_center = center
            
        # Calculate error from center
        error = (self.frame_width/2 - center[0]) / (self.frame_width/2)  # Normalized error
        
        # Get PID control value
        control = self.calculate_pid_control(error)
        
        # Detect corners for speed adjustment
        self.corner_detected = self.detect_corner(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))
        speed = self.base_speed * (self.corner_slowdown if self.corner_detected else 1.0)
        
        # Send control commands
        turn_rate = int(np.clip(control * self.max_turn_speed, -self.max_turn_speed, self.max_turn_speed))
        self.movement.send_rc_control(0, int(speed), 0, turn_rate)
        
        # Visualization
        cv2.rectangle(frame, (0, self.frame_height-self.roi_height), 
                     (self.frame_width, self.frame_height), (0,255,0), 2)
        
        if line_found:
            cv2.circle(frame, (int(center[0]), 
                             int(center[1] + self.frame_height-self.roi_height)), 
                      5, (0,0,255), -1)
            
        # Add telemetry
        cv2.putText(frame, f"Error: {error:.2f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(frame, f"Speed: {speed}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(frame, "CORNER" if self.corner_detected else "STRAIGHT", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                   (0,0,255) if self.corner_detected else (0,255,0), 2)
        
        return frame

    def __del__(self):
        cv2.destroyAllWindows()