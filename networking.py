import socket
import time

# A timeout (in seconds) to determine if the connection is lost
CONNECTION_TIMEOUT = 5.0

class TelloNetworking:
    def __init__(self):
        self.TELLO_IP = '192.168.10.1'
        self.TELLO_PORT = 8889
        self.TELLO_ADDRESS = (self.TELLO_IP, self.TELLO_PORT)

        # Local port for receiving drone status
        self.LOCAL_PORT = 9010 # Use a different port to avoid conflicts
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # We need to handle the case where the port is already in use
        try:
            self.sock.bind(('', self.LOCAL_PORT))
        except OSError as e:
            print(f"Error binding to socket: {e}")
            print("Please ensure no other Tello scripts are running and try again.")
            exit()

        # Connection State
        self.is_connected = False
        self.last_response_time = None

        # Status text fields
        self.battery_text = "Battery:"
        self.time_text = "Time:"
        self.status_text = "Status: Disconnected"

    def connect(self):
        """
        Attempts to establish a connection by sending 'command' and waiting for 'ok'.
        Returns True on success, False on failure.
        """
        self.send_command('command', check_connection=False)
        
        # Wait for a response for up to 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5:
            # The receiver thread updates the status text
            if self.status_text == "Status:ok":
                self.is_connected = True
                self.last_response_time = time.time()
                print("Drone connected successfully!")
                return True
            time.sleep(0.1)
            
        print("Failed to connect to the drone. Please ensure it is on and connected to the same Wi-Fi network.")
        return False

    def send_command(self, command, check_connection=True):
        """Sends a command to the Tello drone, optionally checking the connection status first."""
        if check_connection and not self.is_connected:
            print(f"Cannot send '{command}': Drone not connected.")
            return

        try:
            self.sock.sendto(command.encode('utf-8'), self.TELLO_ADDRESS)
        except Exception as e:
            print(f"Error sending command: {e}")
            self.is_connected = False

    def udp_receiver(self):
        """Receives status updates from the Tello drone."""
        while True:
            try:
                data, server = self.sock.recvfrom(1518)
                resp = data.decode(encoding="utf-8").strip()
                self.last_response_time = time.time() # Update timestamp on any response
                self.is_connected = True # If we receive anything, we are connected

                if resp.isdecimal():
                    self.battery_text = "Battery:" + resp + "%"
                elif resp.endswith('s'):
                    self.time_text = "Time:" + resp
                else:
                    self.status_text = "Status:" + resp
            except Exception:
                # This will trigger if the socket is closed or another error occurs
                self.is_connected = False
                break

    def ask_status(self):
        """Periodically asks for status and checks for connection timeouts."""
        while True:
            if not self.is_connected:
                time.sleep(1)
                continue
            
            # Check for timeout
            if self.last_response_time and (time.time() - self.last_response_time > CONNECTION_TIMEOUT):
                print("Connection to drone lost (timeout).")
                self.is_connected = False
                self.status_text = "Status: Disconnected"

            self.send_command('battery?')
            time.sleep(0.5)
            self.send_command('time?')
            time.sleep(0.5)
