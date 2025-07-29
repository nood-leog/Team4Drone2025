class TelloMovement:
    def __init__(self, networking):
        self.networking = networking

    def takeoff(self):
        """Sends the takeoff command."""
        self.networking.send_command('takeoff')

    def land(self):
        """Sends the land command."""
        self.networking.send_command('land')

    def up(self):
        """Moves the drone up by 20 cm."""
        self.networking.send_command('up 20')

    def down(self):
        """Moves the drone down by 20 cm."""
        self.networking.send_command('down 20')

    def forward(self):
        """Moves the drone forward by 40 cm."""
        self.networking.send_command('forward 40')

    def back(self):
        """Moves the drone backward by 40 cm."""
        self.networking.send_command('back 40')

    def right(self):
        """Moves the drone right by 40 cm."""
        self.networking.send_command('right 40')

    def left(self):
        """Moves the drone left by 40 cm."""
        self.networking.send_command('left 40')

    def cw(self):
        """Rotates the drone clockwise by 90 degrees."""
        self.networking.send_command('cw 90')

    def ccw(self):
        """Rotates the drone counter-clockwise by 90 degrees."""
        self.networking.send_command('ccw 90')

    def set_speed(self, n=40):
        """Sets the drone's speed."""
        self.networking.send_command(f'speed {n}')