
class TelloMovement:
    def __init__(self, networking):
        self.networking = networking

    def takeoff(self):
        self.networking.send_command('takeoff')

    def land(self):
        self.networking.send_command('land')

    # def up(self):
    #     self.networking.send_command('up 20')

    # def down(self):
    #     self.networking.send_command('down 20')

    # def forward(self):
    #     self.networking.send_command('forward 0')

    # def back(self):
    #     self.networking.send_command('back 0')

    # def right(self):
    #     self.networking.send_command('right 0')

    # def left(self):
    #     self.networking.send_command('left 0')

    # def cw(self):
    #     self.networking.send_command('cw 90')

    # def ccw(self):
    #     self.networking.send_command('ccw 90')

    # def set_speed(self, n=40):
    #     self.networking.send_command(f'speed {n}')

    def send_rc_control(self, a, b, c, d):
        self.networking.send_command(f'rc {a} {b} {c} {d}')
