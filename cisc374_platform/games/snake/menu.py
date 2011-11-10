import pygame
import spyral
from game import *

class Text(spyral.sprite.Sprite):
    
    def __init__(self, pos, label, font, color, align='left'):
        spyral.sprite.Sprite.__init__(self)
        self.label = label
        self.font = font
        self.color = color
        self.anchor_pos = pos
        self.align = align
        
        self.render()
        
    def render(self):
        self.images = [self.render_text(self.color), 
                       self.render_text(colors['menu_text_hightlight'])]
        self.image = self.images[0]
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()
        
        if self.align == 'right':
            self.rect.midright = self.anchor_pos
        elif self.align == 'center':
            self.rect.center = self.anchor_pos
        else:
            self.rect.midleft = self.anchor_pos
        
    def focus(self, focus=True):
        if focus:
            self.image = self.images[1]
        else:
            self.image = self.images[0]
            
    def set_label(self, label):
        self.label = label
        self.render()
        
    def render_text(self, color):
        width = 0
        height = 0
        lines = []
        for s in self.label.split("\n"):
            img = self.font.render(s, True, color)
            lines.append(img)
            
            if width < img.get_width():
                width = img.get_width()
            height += img.get_height()
        
        image = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        y = 0
        for img in lines:
            dest = img.get_rect()
            image.blit(img, (dest.left, y))
            y += dest.height
            
        return image


class Button(spyral.sprite.Sprite):
    
    def __init__(self, pos, label, font, color):
        spyral.sprite.Sprite.__init__(self)

        self.label = label
        self.font = font
        self.color = color
        self.highlight = False 

        self.render_text()
        self.render()
        self.rect.center = pos
        
    def render(self):
        if self.highlight:
            self.image = images['button_highlight'].copy()
        else:
            self.image = images['button_normal'].copy()
        
        dest = self.text.get_rect()
        dest.center = self.image.get_rect().center
        
        self.image.blit(self.text, dest)
        
        
    def render_text(self):
        width = 0
        height = 0
        lines = []
        for s in self.label.split("\n"):
            img = self.font.render(s, True, self.color)
            lines.append(img)
            
            if width < img.get_width():
                width = img.get_width()
            height += img.get_height()
        
        self.text = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        y = 0
        for img in lines:
            dest = img.get_rect()
            dest.centerx = width/2
            self.text.blit(img, (dest.left, y))
            y += dest.height
        
    def focus(self, focus=True):
        self.highlight = focus
        self.render()

class Menu(spyral.scene.Scene):
    """Menu Scene shows the game title, buttons to start game, select
    characters or view achievements."""
        
    def __init__(self):
        """Construct the Menu scene"""
        spyral.scene.Scene.__init__(self)
        
        self.root_camera = spyral.director.get_camera()
        self.camera = self.root_camera.make_child(virtual_size = (WIDTH,HEIGHT))    
        self.group = spyral.sprite.Group(self.camera)
        self.camera.set_background(images['menu_background'])
        
        center_x = self.camera.get_rect().centerx
        
        # game title sprite
        title = spyral.sprite.Sprite()
        title.image = images['menu_title']
        title.rect.center = (center_x, geom['menu_title_y'])
        
        # start button
        start = Button((center_x, geom['menu_start_y']), "START", 
                        fonts['menu_start'], colors['menu_start'])
        
        # character select button
        character = Button((center_x, geom['menu_character_y']), "Character\nSelect",
                           fonts['menu_character'], colors['menu_character'])
        
        # achievements/unlock button
        unlock = Text((geom['menu_unlock_x'], geom['menu_unlock_y']), "Achievements\nUnlocks",
                      fonts['menu_unlock'], colors['menu_unlock'])
        
        # quit button
        quit = Text((geom['menu_quit_x'], geom['menu_quit_y']), "QUIT",
                    fonts['menu_quit'], colors['menu_quit'], 'right')
        
        self.buttons = [start, character, unlock, quit]
        self.selected_button = 0
        self.buttons[self.selected_button].focus()
        
        self.group.add(title, start, character, unlock, quit)

    def render(self):
        """Render the current scene"""
        self.group.draw()   # draw group of sprites
        self.root_camera.draw()  # draw the current frame
    
    def update(self, tick):
        """Update the current scene based on user input"""
        
        for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.buttons[self.selected_button].focus(False)
                    self.selected_button = (self.selected_button + 1) % len(self.buttons)
                    self.buttons[self.selected_button].focus()
                
                elif event.key == pygame.K_UP:
                    self.buttons[self.selected_button].focus(False)
                    self.selected_button = (self.selected_button - 1) % len(self.buttons)
                    self.buttons[self.selected_button].focus()
                    
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.selected_button == 0:
                        # Start button clicked
                        # move to Game scene
                        spyral.director.push(Game("Anaconda" , 0))
                    
                    elif self.selected_button == 1:
                        # Character Select button clicked 
                        # move to CharacterSelect scene
                        spyral.director.push(CharacterSelect())
                        
                    elif self.selected_button == 2:
                        # Achievements/Unlocks button clicked
                        # move to Achievements scene
                        #spyral.director.push(Achievements())
                        pass
                    
                    elif self.selected_button == 3:
                        # Quit button clicked
                        exit(0)
        pygame.event.clear()

class Character(spyral.sprite.Sprite):
    
    def __init__(self, center, character):
        spyral.sprite.Sprite.__init__(self)
        self.set_character(character)
        self.rect.center = center
            
    def set_character(self, character):
        self.image = images['characters'][character]
    

class ColorSelect(spyral.sprite.Sprite):
    
    def __init__(self, center):
        spyral.sprite.Sprite.__init__(self)
        self.image = images['color_select']
        self.rect.center = center

class CharacterSelect(spyral.scene.Scene):
        
    def __init__(self):
        """Construct the Menu scene which shows the game title and 
        instructions."""
        
        # Init from the super class
        spyral.scene.Scene.__init__(self)
        
        self.root_camera = spyral.director.get_camera()
        self.camera = self.root_camera.make_child(virtual_size = (WIDTH,HEIGHT))    
        self.group = spyral.sprite.Group(self.camera)
        
        center_x = self.camera.get_rect().centerx

        # title sprite
        title = spyral.sprite.Sprite()
        title.image = images['character_title']
        title.rect.center = (center_x, geom['character_title_y'])
        
        # character name
        self.character_name = Text((center_x, geom['character_name_y']), strings['characters'][0],
                    fonts['character_name'], colors['character_name'], 'center')
        self.selected_character = 0
        self.character = Character((center_x, geom['character_image_y']), 0)

        # select color
        self.character_color = Text((center_x, geom['character_color_y']), "Color Select",
                     fonts['character_color'], colors['character_color'], 'center')
        self.selected_color = 0
        self.color_select = ColorSelect((center_x, geom['character_color_select_y']))
        
        # quit button
        back = Text((geom['character_back_x'], geom['character_back_y']), "BACK",
                    fonts['character_back'], colors['character_back'], 'right')
        
        
        # achievements/unlock
        unlock = Text((geom['character_unlock_x'], geom['character_unlock_y']), 
                      "Players select different\ncharacters, unlocked\nwith achievements",
                      fonts['character_unlock'], colors['character_unlock'])

        self.buttons = [self.character_name, self.character_color, back]
        self.selected_button = 0
        self.buttons[self.selected_button].focus()
        
        self.group.add(title, self.character_name, self.character, 
                       self.character_color, self.color_select, 
                       unlock, back)

    def on_enter(self):
        self.camera.set_background(images['menu_background'])
                
    def render(self):
        """Render the current scene"""
        self.group.draw()   # draw group of sprites
        self.root_camera.draw()  # draw the current frame
    
    def update(self, tick):
        """Update the current scene based on user input"""
        
        # get events (keyboard, mouse, etc.)
        for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.buttons[self.selected_button].focus(False)
                    self.selected_button = (self.selected_button + 1) % len(self.buttons)
                    self.buttons[self.selected_button].focus()
                
                elif event.key == pygame.K_UP:
                    self.buttons[self.selected_button].focus(False)
                    self.selected_button = (self.selected_button - 1) % len(self.buttons)
                    self.buttons[self.selected_button].focus()
                    
                elif event.key == pygame.K_LEFT:
                    if self.selected_button == 0:
                        # change character
                        self.selected_character = (self.selected_character - 1) % len(strings['characters'])
                        self.character_name.set_label(strings['characters'][self.selected_character])
                        self.character_name.focus()
                        
                        self.character.set_character(self.selected_character % len(images['characters']));
                    
                    elif self.selected_button == 1:
                        # change color
                        pass
                
                elif event.key == pygame.K_RIGHT:
                    if self.selected_button == 0:
                        # change character
                        self.selected_character = (self.selected_character + 1) % len(strings['characters'])
                        self.character_name.set_label(strings['characters'][self.selected_character])
                        self.character_name.focus()
                        
                        self.character.set_character(self.selected_character % len(images['characters']));
                        
                    elif self.selected_button == 1:
                        # change color
                        pass
                    
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.selected_button == 2:
                        # Back button clicked
                        spyral.director.pop()
        pygame.event.clear()

def launch():
    spyral.init()

    init()
    
    spyral.director.push(Menu())
    
    pygame.event.set_allowed(None)
    pygame.event.set_allowed(pygame.KEYDOWN)
    pygame.event.set_allowed(pygame.KEYUP)
    pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
