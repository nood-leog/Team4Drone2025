
import cv2
import time
from networking import TelloNetworking
from movement import TelloMovement
from linetrace import LineTracer
from pynput import keyboard

def main():
    
    key_states = {
        'w': False,
        's': False,
        'a': False,
        'd': False,
        'i': False,
        'j': False,
        'u': False,
        'o': False,
    }
    
    def on_press(key):
        try:
            char_key = key.char
            if char_key in key_states:
                key_states[char_key] = True
        except AttributeError:
            pass
        
    def on_release(key):
        try:
            char_key = key.char
            if char_key in key_states:
                key_states[char_key] = False
        except AttributeError:
            if key == keyboard.Key.esc:
                return False
            pass
    
    networking = TelloNetworking()
    movement = TelloMovement(networking)
    linetracer = LineTracer(movement)

    cap = cv2.VideoCapture(networking.TELLO_CAMERA_ADDRESS)
    if not cap.isOpened():
        cap.open(networking.TELLO_CAMERA_ADDRESS)

    window_title = "OpenCV Window"
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
    linetracer.create_trackbars(window_title)

    pre_time = time.time()
    
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    try:
        while True:
            ret, frame = cap.read()
            if frame is None or frame.size == 0:
                continue
            
            SPEED = 75

            out_image = linetracer.process_frame(frame)
            cv2.imshow(window_title, out_image)

            key = cv2.waitKey(1)

            if key == 27:
                break
            elif key == ord('t'):
                movement.takeoff()
            elif key == ord('l'):
                movement.land()
            elif key == ord('1'):
                linetracer.flag = 1
            elif key == ord('2'):
                linetracer.flag = 0
                movement.send_rc_control(0, 0, 0, 0)
            
            if linetracer.flag == 0:
                fb = SPEED if key_states['w'] else -SPEED if key_states['s'] else 0
                lr = -SPEED if key_states['a'] else SPEED if key_states['d'] else 0
                ud = SPEED if key_states['i'] else -SPEED if key_states['j'] else 0
                yaw = -SPEED if key_states['u'] else SPEED if key_states['o'] else 0
                movement.send_rc_control(lr, fb, ud, yaw)

            current_time = time.time()
            if current_time - pre_time > 5.0:
                networking.send_command('command')
                pre_time = current_time

    except (KeyboardInterrupt, SystemExit):
        print("SIGINT detected")
    
    finally:
        networking.close()
        cap.release()
        cv2.destroyAllWindows()
        listener.stop()
        listener.join()

if __name__ == "__main__":
    main()
