import cv2
import threading
import time
import sys
from networking import TelloNetworking
from movement import TelloMovement

def main():
    # Initialize networking and movement controllers
    networking = TelloNetworking()
    movement = TelloMovement(networking)

    # Start the status receiving and asking threads
    recv_thread = threading.Thread(target=networking.udp_receiver)
    recv_thread.daemon = True
    recv_thread.start()
    
    # Attempt to connect to the drone
    if not networking.connect():
        sys.exit() # Exit if connection fails
        
    # Start asking for status only after a successful connection
    ask_thread = threading.Thread(target=networking.ask_status)
    ask_thread.daemon = True
    ask_thread.start()

    # Start video stream
    networking.send_command('streamon')
    time.sleep(1)

    # Initialize video capture
    TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000'
    cap = cv2.VideoCapture(TELLO_CAMERA_ADDRESS)

    if not cap.isOpened():
        print("Failed to open video stream. Make sure the Tello is streaming.")
        cap.open(TELLO_CAMERA_ADDRESS)

    command_text = "None"

    while True:
        ret, frame = cap.read()
        
        # If the video frame is not received, it could be a sign of disconnection
        if not ret:
            networking.is_connected = False
            # Create a black screen to display the error message
            frame = cv2.UMat(480, 640, cv2.CV_8UC3)
            frame.setTo([0, 0, 0])

        # Resize frame for display
        frame_height, frame_width = frame.shape[:2]
        frame_resized = cv2.resize(frame, (frame_width // 2, frame_height // 2))

        # Check connection and display appropriate message
        if networking.is_connected:
            # Display status text on the frame
            cv2.putText(frame_resized, f"Cmd: {command_text}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame_resized, networking.battery_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame_resized, networking.time_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame_resized, networking.status_text, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            # Display a prominent "NOT CONNECTED" message
            cv2.putText(frame_resized, "DRONE NOT CONNECTED!", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


        cv2.imshow('Tello Camera View', frame_resized)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('t'):
            movement.takeoff()
            command_text = "Takeoff"
        elif key == ord('l'):
            movement.land()
            command_text = "Land"
        elif key == ord('w'):
            movement.forward()
            command_text = "Forward"
        elif key == ord('s'):
            movement.back()
            command_text = "Back"
        elif key == ord('a'):
            movement.left()
            command_text = "Left"
        elif key == ord('d'):
            movement.right()
            command_text = "Right"
        elif key == ord('r'):
            movement.up()
            command_text = "Up"
        elif key == ord('c'):
            movement.down()
            command_text = "Down"
        elif key == ord('q'):
            movement.ccw()
            command_text = "CCW"
        elif key == ord('e'):
            movement.cw()
            command_text = "CW"
        elif key == ord('m'):
            movement.set_speed()
            command_text = "Set Speed"

    # Cleanup
    print("Landing and shutting down.")
    movement.land()
    networking.send_command('streamoff')
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()