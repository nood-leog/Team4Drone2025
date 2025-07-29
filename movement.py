class TelloMovement:
    def __init__(self, networking):
        self.networking = networking

    def send_rc_control(self, left_right, forward_backward, up_down, yaw):
        """
        Send RC control commands to the drone.
        Arguments:
            left_right: -100 to 100
            forward_backward: -100 to 100
            up_down: -100 to 100
            yaw: -100 to 100
        """
        command = f"rc {left_right} {forward_backward} {up_down} {yaw}"
        # We don't want to print every rc command, so we call the base sender
        try:
            self.networking.sock.sendto(command.encode('utf-8'), self.networking.TELLO_ADDRESS)
        except Exception as e:
            print(f"Error sending rc command: {e}")


    def takeoff(self):
        """Sends the takeoff command."""
        self.networking.send_command('takeoff')

    def land(self):
        """Sends the land command."""
        self.networking.send_command('land')

    def stop(self):
        """Sends the emergency stop command."""
        self.networking.send_command('stop')

    def flipLeft(self):
        """Sends the flip left command."""
        self.networking.send_command('flip l')

    def flipRight(self):
        """Sends the flip right command."""
        self.networking.send_command('flip r')

    def flipForward(self):
        """Sends the flip forward command."""
        self.networking.send_command('flip f')

    def flipBackward(self):
        """Sends the flip backward command."""
        self.networking.send_command('flip b')

    

    # Note: The old movement functions (up, down, forward, etc.) are no longer
    # used by main.py but can be kept for other potential uses.