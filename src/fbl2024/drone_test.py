import socket
import threading
import cv2
import time
import numpy as np

# データ受け取り用の関数
def udp_receiver():
        global battery_text
        global time_text
        global status_text

        while True: 
            try:
                data, server = sock.recvfrom(1518)
                resp = data.decode(encoding="utf-8").strip()
                # レスポンスが数字だけならバッテリー残量
                if resp.isdecimal():    
                    battery_text = "Battery:" + resp + "%"
                # 最後の文字がsなら飛行時間
                elif resp[-1:] == "s":
                    time_text = "Time:" + resp
                else: 
                    status_text = "Status:" + resp
            except:
                pass

# 問い合わせ
def ask():
    while True:
        try:
            sent = sock.sendto('battery?'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
        time.sleep(0.5)

        try:
            sent = sock.sendto('time?'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
        time.sleep(0.5)


# 離陸
def takeoff():
        print("-----")
        try:
            sent = sock.sendto('takeoff'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 着陸
def land():
        try:
            sent = sock.sendto('land'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 上昇(20cm)
def up():
        try:
            sent = sock.sendto('up 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 下降(20cm)
def down():
        try:
            sent = sock.sendto('down 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 前進(40cm)
def forward():
        try:
            sent = sock.sendto('forward 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 後進(40cm)
def back():
        try:
            sent = sock.sendto('back 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 右に進む(40cm)
def right():
        try:
            sent = sock.sendto('right 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 左に進む(40cm)
def left():
        try:
            sent = sock.sendto('left 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 右回りに回転(90 deg)
def cw():
        try:
            sent = sock.sendto('cw 90'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 左回りに回転(90 deg)
def ccw():
        try:
            sent = sock.sendto('ccw 90'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 速度変更(例：速度40cm/sec, 0 < speed < 100)
def set_speed(n=40):
        try:
            sent = sock.sendto(f'speed {n}'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass


# Tello側のローカルIPアドレス(デフォルト)、宛先ポート番号(コマンドモード用)
# TELLO_IP = '192.168.10.1'
# TELLO_PORT = 8889
# TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)

# Telloからの映像受信用のローカルIPアドレス、宛先ポート番号
TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000'

TELLO_PORT= 8889
TELLO_IP = '192.168.10.1'
# TELLO_IP = '192.168.0.11'
TELLO_ADDRESS = (TELLO_IP , TELLO_PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

command_text = "None"
battery_text = "Battery:"
time_text = "Time:"
status_text = "Status:"

# キャプチャ用のオブジェクト
cap = None

# データ受信用のオブジェクト備
response = None

# 通信用のソケットを作成
# ※アドレスファミリ：AF_INET（IPv4）、ソケットタイプ：SOCK_DGRAM（UDP）
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 自ホストで使用するIPアドレスとポート番号を設定
sock.bind(('', TELLO_PORT))

# 問い合わせスレッド起動
ask_thread = threading.Thread(target=ask)
ask_thread.deamon = True
# ask_thread.setDaemon(True)
ask_thread.start()

# 受信用スレッドの作成
recv_thread = threading.Thread(target=udp_receiver, args=())
recv_thread.daemon = True
recv_thread.start()

# コマンドモード
sock.sendto('command'.encode('utf-8'), TELLO_ADDRESS)

time.sleep(1)

# カメラ映像のストリーミング開始
sock.sendto('streamon'.encode('utf-8'), TELLO_ADDRESS)

time.sleep(1)

if cap is None:
    cap = cv2.VideoCapture(TELLO_CAMERA_ADDRESS)

if not cap.isOpened():
    cap.open(TELLO_CAMERA_ADDRESS)
# cap = cv2.VideoCapture(0)

time.sleep(1)


while True:
    ret, frame = cap.read()

    # 動画フレームが空ならスキップ
    if frame is None or frame.size == 0:
        continue

    # カメラ映像のサイズを半分にする
    frame_height, frame_width = frame.shape[:2]
    frame_resized = cv2.resize(frame, (frame_width//2, frame_height//2))
    frame_output = frame_resized    
    

    # 送信したコマンドを表示
    cv2.putText(frame_output,
            text="Cmd:" + command_text,
            org=(10, 20),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # バッテリー残量を表示
    cv2.putText(frame_output,
            text=battery_text,
            org=(10, 40),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # 飛行時間を表示
    cv2.putText(frame_output,
            text=time_text,
            org=(10, 60),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # ステータスを表示
    cv2.putText(frame_output,
            text=status_text,
            org=(10, 80),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # カメラ映像を画面に表示
    cv2.imshow('Tello Camera View', frame_output)

    # キー入力を取得
    key = cv2.waitKey(1)

    # escキーで終了
    if key == 27:
        break
    # wキーで前進
    elif key == ord('w'):
        forward()
        command_text = "Forward"
    # sキーで後進
    elif key == ord('s'):
        back()
        command_text = "Back"
    # aキーで左進
    elif key == ord('a'):
        left()
        command_text = "Left"
    # dキーで右進
    elif key == ord('d'):
        right()
        command_text = "Right"
    # tキーで離陸
    elif key == ord('t'):
        takeoff()
        command_text = "Take off"
    # lキーで着陸
    elif key == ord('l'):
        land()
        command_text = "Land"
    # rキーで上昇
    elif key == ord('r'):
        up()
        command_text = "Up"
    # cキーで下降
    elif key == ord('c'):
        down()
        command_text = "Down"
    # qキーで左回りに回転
    elif key == ord('q'):
        ccw()
        command_text = "Ccw"
    # eキーで右回りに回転
    elif key == ord('e'):
        cw()
        command_text = "Cw"
    # mキーで速度変更
    elif key == ord('m'):
        set_speed()
        command_text = "Changed speed"

cap.release()
cv2.destroyAllWindows()

# ビデオストリーミング停止
sock.sendto('streamoff'.encode('utf-8'), TELLO_ADDRESS)