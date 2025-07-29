import cv2
import threading
import time
import sys
from networking import TelloNetworking
from movement import TelloMovement
from pynput import keyboard
key_states = {
        'w': False, 's': False, 'a': False, 'd': False, # Forward/Back, Left/Right
        'q': False, 'e': False,                         # Yaw (Rotation)
        'r': False, 'c': False                          # Up/Down
    }

def main():
    # Initialize networking and movement controllers
    networking = TelloNetworking()
    movement = TelloMovement(networking)

    # Start the status receiving and asking threads
    recv_thread = threading.Thread(target=networking.udp_receiver)
    recv_thread.daemon = True
    recv_thread.start()

    if not networking.connect():
        sys.exit()

    ask_thread = threading.Thread(target=networking.ask_status)
    ask_thread.daemon = True
    ask_thread.start()

    networking.send_command('streamon')
    time.sleep(1)

    TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000'
    cap = cv2.VideoCapture(TELLO_CAMERA_ADDRESS)

    if not cap.isOpened():
        cap.open(TELLO_CAMERA_ADDRESS)


    listner = keyboard.Listener(on_press=on_press, on_release=on_release)
    listner.start()
    # --- New variables for continuous control ---
    command_text = "None"
    # Sensity of the movement
    SPEED = 50
    # Dictionary to keep track of which keys are currently pressed

    while True:
        ret, frame = cap.read()
        if not ret:
            networking.is_connected = False
            frame = cv2.UMat(480, 640, cv2.CV_8UC3)
            frame.setTo([0, 0, 0])

        frame_resized = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))

        # --- Handle Keyboard Input ---
        # We use a longer waitKey time to allow for smoother control.
        # This is also where we detect key releases (when key == -1)
        # key = cv2.waitKey(20) & 0xFF
        key_cv2 = cv2.waitKey(1) & 0xFF  # Use a shorter wait time for smoother control

        # --- Handle discrete commands first (takeoff, land, etc.) ---
        if key_cv2 == 27:  # ESC
            break
        elif key_cv2 == ord('t'):
            movement.takeoff()
            command_text = "Takeoff"
        elif key_cv2 == ord('l'):
            movement.land()
            command_text = "Land"
        elif key_cv2 == ord(' '): # Spacebar for emergency stop
            movement.stop()
            command_text = "EMERGENCY STOP"
            # Reset all RC values to 0
            for k in key_states: key_states[k] = False


        # --- Update the state of pressed keys ---
        # This part is tricky with cv2.waitKey. This implementation assumes that
        # if a new key is pressed, we update its state. A more advanced system
        # might use a different library (like 'pynput') for true key up/down events.
        # For our purpose, we will reset movement if no key is being pressed.
        # if key != 255 and chr(key) in key_states:
        #     # For simplicity, we'll make this a direct control loop.
        #     # When a key is pressed, we send the command. When it's not, we send stop.
        #     pass # We will handle this logic below

        # --- Calculate RC values based on key states ---
        # This structure naturally handles diagonal movement (e.g., W+A)
        # and stops movement when keys are released.
        # fb = SPEED if key == ord('w') else -SPEED if key == ord('s') else 0
        # lr = -SPEED if key == ord('a') else SPEED if key == ord('d') else 0
        # ud = SPEED if key == ord('r') else -SPEED if key == ord('c') else 0
        # yaw = -SPEED if key == ord('q') else SPEED if key == ord('e') else 0
        
        fb = 0
        if key_states['w']:
            fb = SPEED
        elif key_states['s']:
            fb = -SPEED
        lr = 0
        if key_states['a']:
            lr = -SPEED
        elif key_states['d']:
            lr = SPEED
        ud = 0
        if key_states['r']:
            ud = SPEED
        elif key_states['c']:
            ud = -SPEED
        yaw = 0
        if key_states['q']: # Rotate left
            yaw = -SPEED
        elif key_states['e']: # Rotate right
            yaw = SPEED

        # Send the command to the drone
        movement.send_rc_control(lr, fb, ud, yaw)

        # Update command text for display
        # if key != 255 and key != ord(' '):
        #     command_text = f"rc {lr} {fb} {ud} {yaw}"

        # --- Display Information ---
        if networking.is_connected:
            cv2.putText(frame_resized, f"Cmd: {command_text}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame_resized, networking.battery_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame_resized, networking.time_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame_resized, networking.status_text, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            cv2.putText(frame_resized, "DRONE NOT CONNECTED!", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow('Tello Camera View', frame_resized)

    # --- Cleanup ---
    print("Landing and shutting down.")
    movement.land()
    networking.send_command('streamoff')
    cap.release()
    cv2.destroyAllWindows()
    
    listner.stop()
    listner.join()
    
def on_press(key):
    try:
        char_key = key.char
        if char_key in key_states:
            key_states[char_key] = True
    except AttributeError:
        pass  # Handle special keys like ctrl, alt, etc.
    
def on_release(key):
    try:
        char_key = key.char
        if char_key in key_states:
            key_states[char_key] = False
    except AttributeError:
        pass  # Handle special keys like ctrl, alt, etc.
    
    if key == keyboard.Key.esc:
        # Stop listener
        return False

if __name__ == "__main__":
    main()
