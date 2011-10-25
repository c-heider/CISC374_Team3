# This is a modified version of the spyral skeleton example, which includes
# comments only for the differences required to work with the launcher
import pygame
import spyral

SIZE = (1200, 900)
BG_COLOR = (100, 0, 0)

class Game(spyral.scene.Scene):
    def __init__(self):
        spyral.scene.Scene.__init__(self)
        # When using the launcher, we need to always make a subcamera that
        # uses our internal resolution. The internal resolution should always be
        # 1200 x 900, as that is the size on the XOs
        self.root_camera = spyral.director.get_camera()
        self.camera = self.root_camera.make_child(real_size = (0,0),
                                      virtual_size = SIZE)
        self.group = spyral.sprite.Group(self.camera)
        bg = spyral.util.new_surface(SIZE)
        bg.fill(BG_COLOR)
        self.camera.set_background(bg)
                
    def render(self):
        self.group.draw()
        # We only need to instruct the root camera to draw
        self.root_camera.draw()
        
    def update(self, tick):
        self.group.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                spyral.director.pop()

def launch():
    # The launch function for the cisc374 launcher
    # The launch function should push the necessary Scene(s) on the stack
    spyral.director.push(Game())