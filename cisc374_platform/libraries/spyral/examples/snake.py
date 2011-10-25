import pygame
import spyral
from collections import deque
import random

geom = {}
images = {}
colors = {}

NORTH, SOUTH, EAST, WEST = range(4)
directions = [(0,-1), (0, 1), (1,0), (-1,0)]
keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT]

def grid_to_world(p):
    return spyral.point.scale(p, geom['block'])

class GridBlock(spyral.sprite.Sprite):
    def _get_grid_pos(self):
        return self._grid_pos
        
    def _set_grid_pos(self, pos):
        self._grid_pos = pos
        self.pos = grid_to_world(pos)
        
    grid_pos = property(_get_grid_pos, _set_grid_pos)

class SnakeBlock(GridBlock):
    def __init__(self):
        GridBlock.__init__(self)
        self.image = images['snake']

class AppleBlock(GridBlock):
    def __init__(self):
        GridBlock.__init__(self)
        self.image = images['apple']
        
class SnakeGame(spyral.scene.Scene):
    def __init__(self):
        spyral.scene.Scene.__init__(self)
        self.camera = spyral.director.get_camera()
        self.group = spyral.sprite.Group(self.camera)
        
        bg = spyral.util.new_surface(geom['size'])
        bg.fill(colors['background'])
        self.camera.set_background(bg)
        
        s = SnakeBlock()
        s.grid_pos = (geom['grid_size'][0] / 2, geom['grid_size'][1] / 2)
        self.dir = NORTH
        self.snake = deque()
        self.snake.append(s)
        self.group.add(s)
        
        self.apple = AppleBlock()
        self.apple.grid_pos = self.random_empty_block()
        self.group.add(self.apple)
        
        self.eating = 0
        
    def random_empty_block(self):
        def rand():
            return (random.randint(0, geom['grid_size'][0]-1),
                    random.randint(0, geom['grid_size'][1]-1))
        r = rand()
        l = map(lambda x: x.grid_pos, self.snake)
        while r in l:
            r = rand()
        return r
        
    def render(self):
        self.group.draw()
        self.camera.draw()
        
    def update(self, tick):
        self.group.update()
        changed = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in keys:
                    if changed:
                        # Put this back on the event queue
                        pygame.event.post(event)
                    else:
                        if event.key != keys[self.dir]:
                            dir = keys.index(event.key)
                            if(     len(self.snake) == 1 or
                                    (self.dir == NORTH and dir != SOUTH) or
                                    (self.dir == SOUTH and dir != NORTH) or
                                    (self.dir == EAST and dir != WEST) or
                                    (self.dir == WEST and dir != EAST)):
                                self.dir = keys.index(event.key)
                                changed = True
                        # Otherwise, we throw the key press away
        l = map(lambda x: x.grid_pos, self.snake)[1:]
        head = self.snake[0]
        if (head.grid_pos in l or
            head.grid_pos[0] < 0 or
            head.grid_pos[1] < 0 or
            head.grid_pos[0] >= geom['grid_size'][0] or
            head.grid_pos[1] >= geom['grid_size'][1]):
            # Game over!
            exit(0)
        if head.grid_pos == self.apple.grid_pos:
            self.eating = 4
            self.apple.grid_pos = self.random_empty_block()
        new_head_pos = spyral.point.add(head.grid_pos, directions[self.dir])
        if self.eating > 0:
            self.eating -= 1
            new_head = SnakeBlock()
            self.group.add(new_head)
        else:
            new_head = self.snake.pop()
        new_head.grid_pos = new_head_pos
        self.snake.appendleft(new_head)
        

if __name__ == "__main__":
    spyral.init()
    
    geom['size'] = (640, 480)
    geom['block'] = (10, 10)
    geom['grid_size'] = (geom['size'][0] / geom['block'][0],
                         geom['size'][1] / geom['block'][1])
    
    colors['snake'] = (150, 150, 150)
    colors['apple'] = (255, 0, 0)
    colors['background'] = (0, 0, 0)
    
    images['snake'] = spyral.util.new_surface(geom['block'])
    images['apple'] = spyral.util.new_surface(geom['block'])
    pygame.draw.rect(images['snake'],
                     colors['snake'],
                     ((0,0), spyral.point.sub(geom['block'], (1,1))))
    pygame.draw.rect(images['apple'],
                     colors['apple'],
                     ((0,0), spyral.point.sub(geom['block'], (1,1))))
                     
    
    spyral.director.init(geom['size'], ticks_per_second=10)
    spyral.director.push(SnakeGame())
    spyral.director.run()
