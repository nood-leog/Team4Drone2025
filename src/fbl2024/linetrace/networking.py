import socket
import time
import threading

class TelloNetworking:
    def __init__(self):
        self.TELLO_IP = '192.168.10.1'
        self.TELLO_PORT = 8889
        self.TELLO_ADDRESS = (self.TELLO_IP, self.TELLO_PORT)
        self.TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000'

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.TELLO_PORT))

        self.response = None
        self.battery_text = "Battery:"
        self.time_text = "Time:"
        self.status_text = "Status:"

        self.recv_thread = threading.Thread(target=self.udp_receiver)
        self.recv_thread.daemon = True
        self.recv_thread.start()

        self.ask_thread = threading.Thread(target=self.ask)
        self.ask_thread.daemon = True
        self.ask_thread.start()

        self.send_command('command')
        time.sleep(2)
        self.send_command('streamon')
        time.sleep(2)
        self.send_command('setfps low')


    def udp_receiver(self):
        while True:
            try:
                data, server = self.sock.recvfrom(1518)
                resp = data.decode(encoding="utf-8").strip()
                if resp.isdecimal():
                    self.battery_text = "Battery:" + resp + "%"
                elif resp[-1:] == "s":
                    self.time_text = "Time:" + resp
                else:
                    self.status_text = "Status:" + resp
            except:
                pass

    def ask(self):
        while True:
            try:
                self.send_command('battery?')
            except:
                pass
            time.sleep(0.5)
            try:
                self.send_command('time?')
            except:
                pass
            time.sleep(0.5)

    def send_command(self, command):
        try:
            self.sock.sendto(command.encode(encoding="utf-8"), self.TELLO_ADDRESS)
        except Exception as e:
            print(f"Error sending command: {e}")

    def close(self):
        self.send_command('streamoff')
        self.sock.close()
