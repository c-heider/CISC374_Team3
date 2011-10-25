class TimerSprite(Sprite):
    def __init__(self, *args):
        Sprite.__init__(self, *args)
        self.countdown = -1
        self.visible = False

    def show(self, ticks):
        """ Takes a number of ticks to show the sprite for. """
        self.visible = True
        self.countdown = ticks

    def update(self):
        if self.countdown < 0:
            return
        if self.countdown == 0:
            self.visible = False
        self.countdown -= 1