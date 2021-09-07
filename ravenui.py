import pygame, sys

WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 50)
BLUE = (50, 50, 255)
ORANGE = (200, 100, 50)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
TRANS = (1, 1, 1)

class UI():
    def __init__(self, screen):
        self.screen = screen
        self.elements = []
        self.buttons = []
        self.sliders = []

        self.hidden_elements = []
        self.hidden_buttons = []
        self.hidden_sliders = []


    def update(self):
        for slider in self.sliders:
            if slider.hit:
                slider.move()

    def events(self, event_type):
        if event_type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                button.check_click()
            for slider in self.sliders:
                if slider.button_rect.collidepoint(mouse_pos):
                    slider.hit = True
        elif event_type == pygame.MOUSEBUTTONUP:
            for slider in self.sliders:
                slider.hit = False

    def draw(self):
        for element in self.elements:
            element.draw()

class Element():
    def __init__(self, ui):
        self.ui = ui
        self.screen = ui.screen
        ui.elements.append(self)

    def hide(self):
        if self in self.ui.elements:
            self.ui.elements.remove(self)
            self.ui.hidden_elements.append(self)
        if self in self.ui.buttons:
            self.ui.buttons.remove(self)
            self.ui.hidden_buttons.append(self)
        if self in self.ui.sliders:
            self.ui.sliders.remove(self)
            self.ui.hidden_sliders.append(self)

    def show(self):
        if self in self.ui.hidden_elements:
            self.ui.hidden_elements.remove(self)
            self.ui.elements.append(self)
        if self in self.ui.hidden_buttons:
            self.ui.hidden_buttons.remove(self)
            self.ui.buttons.append(self)
        if self in self.ui.hidden_sliders:
            self.ui.hidden_sliders.remove(self)
            self.ui.sliders.append(self)

class Button(Element):
    def __init__(self, ui, txt, pos, action, bg=WHITE, fg=BLACK, size=(100, 50), font_name="Segoe Print", font_size=16):
        super().__init__(ui)
        ui.buttons.append(self) # adds button to UI
        self.kind = "button"
        self.color = bg  # the static (normal) color
        self.bg = bg  # actual background color, can change on mouseover
        self.fg = fg  # text color
        self.size = size

        self.font = pygame.font.SysFont(font_name, font_size)
        self.txt = txt
        self.txt_surf = self.font.render(self.txt, 1, self.fg)
        self.txt_rect = self.txt_surf.get_rect(center=[s//2 for s in self.size])

        self.surface = pygame.surface.Surface(size)
        self.rect = self.surface.get_rect(topleft=pos)

        self.call_back_ = action

    def draw(self):
        self.mouseover()
        self.surface.fill(self.bg)
        self.surface.blit(self.txt_surf, self.txt_rect)
        self.screen.blit(self.surface, self.rect)

    def mouseover(self):
        self.bg = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.bg = GREY  # mouseover color

    def check_click(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.call_back_()

class Slider(Element):
    def __init__(self, ui, txt, pos, val, maxi, mini, float = False, font_name="Veranda", font_size=17):
        super().__init__(ui)
        ui.sliders.append(self)
        self.kind = "slider"
        self.float = float
        self.font = pygame.font.SysFont(font_name, font_size)
        self.val = val  # start value
        if not self.float:
            self.val = int(val)
        self.maxi = maxi  # maximum at slider position right
        self.mini = mini  # minimum at slider position left
        self.xpos = pos[0]  # x-location on screen
        self.ypos = pos[1]
        self.surf = pygame.surface.Surface((100, 50))
        self.hit = False  # the hit attribute indicates slider movement due to mouse interaction

        self.txt_surf = self.font.render(txt, 1, BLACK)
        self.txt_rect = self.txt_surf.get_rect(center=(50, 15))

        # Static graphics - slider background #
        self.surf.fill((100, 100, 100))
        pygame.draw.rect(self.surf, GREY, [0, 0, 100, 50], 3)
        pygame.draw.rect(self.surf, ORANGE, [10, 10, 80, 10], 0)
        pygame.draw.rect(self.surf, WHITE, [10, 38, 80, 5], 0)

        self.surf.blit(self.txt_surf, self.txt_rect)  # this surface never changes

        # dynamic graphics - button surface #
        self.button_surf = pygame.surface.Surface((20, 20))
        self.button_surf.fill(TRANS)
        self.button_surf.set_colorkey(TRANS)
        pygame.draw.circle(self.button_surf, BLACK, (10, 10), 6, 0)
        pygame.draw.circle(self.button_surf, ORANGE, (10, 10), 4, 0)

    def draw(self):
        """ Combination of static and dynamic graphics in a copy of
    the basic slide surface
    """
        # static
        surf = self.surf.copy()

        # dynamic
        pos = (10+int((self.val-self.mini)/(self.maxi-self.mini)*80), 40)
        self.button_rect = self.button_surf.get_rect(center=pos)
        surf.blit(self.button_surf, self.button_rect)
        self.button_rect.move_ip(self.xpos, self.ypos)  # move of button box to correct screen position
        # draws value selected on slider.
        if self.float:
            display_val = str(round(self.val, 5))
        else:
            display_val = str(int(self.val))
        value_txt_surf = self.font.render(display_val, 1, BLACK)
        value_txt_rect = value_txt_surf.get_rect(center=(pos[0], pos[1] - 12))
        surf.blit(value_txt_surf, value_txt_rect)

        # screen
        self.screen.blit(surf, (self.xpos, self.ypos))

    def move(self):
        """
    The dynamic part; reacts to movement of the slider button.
    """
        self.val = (pygame.mouse.get_pos()[0] - self.xpos - 10) / 80 * (self.maxi - self.mini) + self.mini
        if not self.float:
            self.val = int(self.val)
        if self.val < self.mini:
            self.val = self.mini
        if self.val > self.maxi:
            self.val = self.maxi

    def hide(self):
        if self in self.ui.elements:
            self.ui.elements.remove(self)
            self.ui.hidden_elements.append(self)
        if self in self.ui.sliders:
            self.ui.sliders.remove(self)
            self.ui.hidden_sliders.append(self)

    def show(self):
        if self in self.ui.elements:
            self.ui.elements.remove(self)
            self.ui.hidden_elements.append(self)
        if self in self.ui.sliders:
            self.ui.sliders.remove(self)
            self.ui.hidden_sliders.append(self)




