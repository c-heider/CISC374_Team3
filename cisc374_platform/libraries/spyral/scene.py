import pygame
import spyral

class Director(object):
    """
    The director, accessible at *spyral.director*, handles running the game.
    It will switch between scenes and call their render and update methods
    as necessary.
        """
    def __init__(self):
        self._initialized = False
        pass

    def init(self, size = (0, 0),
                   fullscreen       = False,
                   caption          = "spyral",
                   max_fps          = 30,
                   ticks_per_second = 30):
        """
        Initializes the director.
        
        | *size* is the resolution of the display. (0,0) uses the screen resolution
        | *fullscreen* determines whether the display starts fullscreen
        | *caption* is the window caption
        | *max_fps* sets the fps cap on the game.
        | *ticks_per_second* sets the number of times scene.update() should be
           called per frame. This will remain the same, even if fps drops.
        """
        if self._initialized:
            print 'Warning: Tried to initialize the director twice. Ignoring.'
        pygame.init()
        pygame.font.init()

        flags = 0
        # These flags are going to be managed better or elsewhere later
        resizable        = False
        noframe          = False
        
        if resizable:
            flags |= pygame.RESIZABLE
        if noframe:
            flags |= pygame.NOFRAME
        if fullscreen:
            flags |= pygame.FULLSCREEN
        self._screen = pygame.display.set_mode(size, flags)

        self._initialized = True

        self._camera = spyral.camera.Camera(virtual_size=size, root=True)
        pygame.display.set_caption(caption)

        self._stack = []
        self._tick = 0

        self._max_fps = max_fps
        self._tps = ticks_per_second

    def get_camera(self):
        """
        Returns the root camera for the display.
        """
        return self._camera

    def get_scene(self):
        """
        Returns the currently running scene.
        """
        if len(self._stack) > 0:
            return self._stack[-1]
        return None

    def get_tick(self):
        """
        Returns the current tick number, where ticks happen on each update,
        not on each frame.
        """
        return self._tick

    def replace(self, scene):
        """
        Replace the currently running scene on the stack with *scene*.
        This does return control, so remember to return after calling it.
        """
        if len(self._stack) > 0:
            old = self._stack.pop()
            old.on_exit()
            spyral.sprite._switch_scene()
            self._camera._exit_scene(old)
        self._stack.append(scene)
        self._camera._enter_scene(scene)
        scene.on_enter()
        pygame.event.get()

    def pop(self):
        """
        Pop the top scene off the stack, returning control to the next scene
        on the stack. If the stack is empty, the program will quit.

        This does return control, so remember to return after calling it.
        """
        if len(self._stack) < 1:
            return
        scene = self._stack.pop()
        scene.on_exit()
        spyral.sprite._switch_scene()
        self._camera._exit_scene(scene)
        if len(self._stack) > 0:
            scene = self._stack[-1]
            self._camera._enter_scene(scene)
            scene.on_enter()
        else:
            exit(0)
        pygame.event.get()

    def push(self, scene):
        """
        Place *scene* on the top of the stack, and move control to it.

        This does return control, so remember to return after calling it.
        """
        if len(self._stack) > 0:
            old = self._stack[-1]
            old.on_exit()
            spyral.sprite._switch_scene()
            self._camera._exit_scene(old)
        self._stack.append(scene)
        self._camera._enter_scene(scene)
        scene.on_enter()
        pygame.event.get()

    def run(self):
        """
        Runs the scene as dictated by the stack. Does not return.
        """
        if self._stack > 0:
            while True:
                scene = self.get_scene()
                clock = scene.clock
                clock.tick()
                if clock.frame_ready:
                    scene.render()
                if clock.update_ready:
                    scene.update(self._tick)
                    self._tick += 1

class Scene(object):
    """
    Represents a state of the game as it runs.
    
    *self.clock* will contain an instance of GameClock which can be replaced
    or changed as is needed.
    """
    def __init__(self, ticks_per_second = None, max_fps = None):
        """
        By default, ticks_per_second and max_fps are pulled from the director.
        """
        from sys import platform

        if platform in('win32', 'cygwin'):
            time_source = None
        else:
            time_source = lambda: pygame.time.get_ticks() / 1000.

        self.clock = spyral._lib.gameclock.GameClock(
                            time_source=time_source,
                            max_fps=max_fps or spyral.director._max_fps,
                            ticks_per_second=ticks_per_second or spyral.director._tps)
        self.clock.use_wait = False

    def on_exit(self):
        """
        Called by the director when this scene is about to run.
        """
        pass

    def on_enter(self):
        """
        Called by the director when this scene is exiting.
        """
        pass

    def render(self):
        """
        Called by the director when a new frame needs to be rendered.
        """
        pass

    def update(self, tick):
        """
        Called by the director when a new game logic step should be taken.
        """
        pass
