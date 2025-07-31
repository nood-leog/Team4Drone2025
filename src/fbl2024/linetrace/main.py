
import cv2
import time
from networking import TelloNetworking
from movement import TelloMovement
from linetrace import LineTracer

def main():
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

    try:
        while True:
            ret, frame = cap.read()
            if frame is None or frame.size == 0:
                continue

            out_image = linetracer.process_frame(frame)
            cv2.imshow(window_title, out_image)

            key = cv2.waitKey(1)

            if key == 27:
                break
            elif key == ord('w'):
                movement.forward()
            elif key == ord('s'):
                movement.back()
            elif key == ord('a'):
                movement.left()
            elif key == ord('d'):
                movement.right()
            elif key == ord('t'):
                movement.takeoff()
            elif key == ord('l'):
                movement.land()
            elif key == ord('r'):
                movement.up()
            elif key == ord('c'):
                movement.down()
            elif key == ord('q'):
                movement.ccw()
            elif key == ord('e'):
                movement.cw()
            elif key == ord('1'):
                linetracer.flag = 1
            elif key == ord('2'):
                linetracer.flag = 0
                movement.send_rc_control(0, 0, 0, 0)
            elif key == ord('y'):
                linetracer.b = min(100, linetracer.b + 10)
            elif key == ord('h'):
                linetracer.b = max(0, linetracer.b - 10)

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

if __name__ == "__main__":
    main()
