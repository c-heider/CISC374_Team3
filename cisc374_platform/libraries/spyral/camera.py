from __future__ import division
import spyral
import pygame
import math
import operator
import sys


@spyral.memoize.SmartMemoize
def _scale(s, factor):
    if factor == (1.0, 1.0):
        return s
    size = s.get_size()
    new_size = (int(math.ceil(size[0] * factor[0])),
                int(math.ceil(size[1] * factor[1])))
    t = pygame.transform.scale(s,
            new_size,
            spyral.util.new_surface(new_size))
    return t


class Camera(object):
    """
    Represents an area to draw to. It can handle automatic scaling with optional
    offsets, layering, and more soon.
    """
    def __init__(self, virtual_size = None,
                       real_size    = None,
                       offset       = (0, 0),
                       layers       = ['all'],
                       root         = False):
        if root:
            self._surface = pygame.display.get_surface()
            if real_size is None or real_size == (0,0):
                self._rsize = self._surface.get_size()
            else:
                self._rsize = real_size
        elif real_size is None:
            raise ValueError("Must specify a real_size.")
        else:
            self._rsize = real_size

        if virtual_size is None or virtual_size == (0,0):
            self._vsize = self._rsize
            self._scale = (1.0, 1.0)
        else:
            self._vsize = virtual_size
            self._scale = (self._rsize[0] / self._vsize[0],
                           self._rsize[1] / self._vsize[1])
        self._background = None
        self._root = root
        self._offset = offset
        self._layers = layers

        if self._root:
            self._background = pygame.surface.Surface(self._rsize)
            self._background.fill((255, 255, 255))
            self._surface.blit(self._background, (0, 0))
            self._blits = []
            self._dirty_rects = []
            self._clear_this_frame = []
            self._clear_next_frame = []
            self._static_blits = {}
            self._rs = self
            self._rect = self._surface.get_rect()
            self._saved_blits = {}
            self._backgrounds = {}

    def make_child(self, virtual_size = None,
                         real_size    = None,
                         offset       = (0, 0),
                         layers       = ['all']):
        """
        Method for creating a new Camera.
        
        | *virtual_size* is a size of the virtual resolution to be used.
        | *real_size* is a size of the resolution with respect to the parent
          camera (not to the physical display, unless the parent camera is the
          root one). This allows multi-level nesting of cameras, if needed.
        | *offset* is a position offset of where this camera should be in the
          parent camera's coordinates.
        | *layers* is a list of layers which should be drawn bottom to top.
        """
        if real_size == (0,0) or real_size == None:
            real_size = self.get_size()
        y = spyral.camera.Camera(virtual_size, real_size, offset, layers, 0)
        y._parent = self
        offset = spyral.point.scale(offset, self._scale)
        y._offset = (offset[0] + self._offset[0],
                     offset[1] + self._offset[1])
        y._scale = (self._scale[0] * y._scale[0],
                    self._scale[1] * y._scale[1])
        y._rect = pygame.Rect(y._offset,
                              spyral.point.scale(real_size, self._scale))
        y._rs = self._rs
        return y

    def get_size(self):
        """
        Returns the virtual size of this camera's display.
        """
        return self._vsize
        
    def get_rect(self):
        """
        Returns a rect the virtual size of this camera's display
        """
        return pygame.rect.Rect((0,0), self._vsize)

    def set_background(self, surface):
        """
        Sets a background for this camera's display.
        """
        # This is CPython specific, but right now so is Pygame.
        if sys._getframe(1).f_code.co_name == "__init__":
            raise RuntimeError("Background initialization must be done in a scene's on_enter, not __init__")
        if surface.get_size() != self._vsize:
            raise ValueError("Background size must match the display size.")
        if not self._root:
            self._rs._background.blit(_scale(surface, self._scale),
                                      self._offset)
            self._rs._clear_this_frame.append(self._rs._background.get_rect())
        else:
            self._background = surface
            self._clear_this_frame.append(surface.get_rect())

    def _blit(self, surface, position, layer, flags):
        position = spyral.point.scale(position, self._scale)
        position = (position[0] + self._offset[0],
                    position[1] + self._offset[1])
        try:
            layer = self._layers.index(layer)
        except ValueError:
            layer = len(self._layers)

        new_surface = _scale(surface, self._scale)
        r = pygame.Rect(position, new_surface.get_size())

        if self._rect.contains(r):
            pass
        elif self._rect.colliderect(r):
            x = r.clip(self._rect)
            y = x.move(-r.left, -r.top)
            new_surface = new_surface.subsurface(y)
            r = x
        else:
            return

        self._rs._blits.append((new_surface,
                                r.topleft,
                                layer,
                                flags))

    def _static_blit(self, sprite, surface, position, layer, flags):
        position = spyral.point.scale(position, self._scale)
        position = (position[0] + self._offset[0],
                    position[1] + self._offset[1])
        try:
            layer = 0 + layer
        except TypeError:
            try:
                layer = self._layers.index(layer)
            except ValueError:
                layer = len(self._layers)

        rs = self._rs
        redraw = sprite in rs._static_blits
        if redraw:
            r2 = rs._static_blits[sprite][1]
        new_surface = _scale(surface, self._scale)
        r = pygame.Rect(position, new_surface.get_size())
        if self._rect.contains(r):
            pass
        elif self._rect.colliderect(r):
            x = r.clip(self._rect)
            y = x.move(-r.left, -r.top)
            new_surface = new_surface.subsurface(y)
            r = x
        else:
            return

        rs._static_blits[sprite] = (new_surface,
                                  r,
                                  layer,
                                  flags)
        if redraw:
            rs._clear_this_frame.append(r2.union(r))
        else:
            rs._clear_this_frame.append(r)

    def _remove_static_blit(self, sprite):
        if not self._root:
            self._rs._remove_static_blit(sprite)
            return
        try:
            x = self._static_blits.pop(sprite)
            self._clear_this_frame.append(x[1])
        except:
            pass

    def draw(self):
        """
        Draws the current frame. Should be called only once per frame by
        the current Scene.
        """

        # This function sits in a potential hot loop
        # For that reason, some . lookups are optimized away
        if not self._root:
            return
        screen = self._surface

        # Let's finish up any rendering from the previous frame
        # First, we put the background over all blits
        x = self._background.get_rect()
        for i in self._clear_this_frame:
            i = x.clip(i)
            b = self._background.subsurface(i)
            screen.blit(b, i)

        # Now, we need to blit layers, while simultaneously re-blitting
        # any static blits which were obscured
        s = self._static_blits.values()
        blits = self._blits
        clear_this = self._clear_this_frame
        clear_next = self._clear_next_frame
        update_this = []
        screen_rect = screen.get_rect()
        s.sort(key=operator.itemgetter(2))
        blits.sort(key=operator.itemgetter(2))
        i = j = 0
        drawn_static = 0
        v = pygame.version.vernum
        # Reminder: blits are (surf, pos, layer)
        for layer in xrange(-100, 20):
            if len(s) > 0:
                while i < len(s) and s[i][2] == layer:
                    surf, pos, layer, flags = s[i]
                    # Now, does this need to be redrawn
                    for rect in clear_this:
                        if pos.colliderect(rect):
                            if v < (1, 8):
                                screen.blit(surf, pos)
                            else:
                                screen.blit(surf, pos, None, flags)
                            clear_this.append(pos)
                            drawn_static += 1
                            break
                    i = i + 1
            if len(blits) > 0 and layer >= 0:
                while j < len(blits) and blits[j][2] == layer:
                    # These are moving blits, so we need to make sure that
                    # they will be cleared on the next frame
                    surf, pos, layer, flags = blits[j]
                    blit_rect = pygame.Rect(pos, surf.get_size())
                    if screen_rect.contains(blit_rect):
                        if v < (1, 8):
                            r = screen.blit(surf, pos)
                        else:
                            r = screen.blit(surf, pos, None, flags)
                        clear_next.append(r)
                    elif screen_rect.colliderect(blit_rect):
                        x = blit_rect.clip(screen_rect)
                        y = x.move(-blit_rect.left, -blit_rect.top)
                        b = surf.subsurface(y)
                        if v < (1, 8):
                            r = screen.blit(b, x)
                        else:
                            r = screen.blit(b, x, None, flags)
                        clear_next.append(r)
                    j = j + 1

        # print "%d / %d static drawn, %d dynamic" %
        #       (drawn_static, len(s), len(blits))
        pygame.display.set_caption("%d / %d static, %d dynamic. %d ups, %d fps" %
            (drawn_static, len(s), len(blits), spyral.director.get_scene().clock.get_ups(),
            spyral.director.get_scene().clock.get_fps()))
        # Do the display update
        pygame.display.update(self._clear_next_frame + self._clear_this_frame)
        # Get ready for the next call
        self._clear_this_frame = self._clear_next_frame
        self._clear_next_frame = []
        self._blits = []
        
    def _exit_scene(self, scene):
        self._saved_blits[scene] = self._static_blits
        self._static_blits = {}
        self._backgrounds[scene] = self._background
        self._background = pygame.surface.Surface(self._rsize)
        self._background.fill((255, 255, 255))
        self._surface.blit(self._background, (0, 0))
        
    def _enter_scene(self, scene):
        self._static_blits = self._saved_blits.pop(scene, self._static_blits)
        if scene in self._backgrounds:
            self._background = self._backgrounds.pop(scene)
            self._clear_this_frame.append(self._background.get_rect())

    def layers(self):
        """ Returns a list of this camera's layers. """
        return self._layers[:]

    def world_to_local(self, pos):
        """
        Converts coordinates from the display to coordinates in this camera's
        space. If the coordinate is outside, then it returns None.
        """
        if self._rect.collidepoint(pos):
            pos = spyral.point.sub(pos, self._offset)
            pos = spyral.point.unscale(pos, self._scale)
            return pos
        return None
