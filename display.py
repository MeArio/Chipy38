import pygame
import pygame.gfxdraw


class Display():
    colors = {'white': (255, 255, 255)}

    def __init__(self, width, height, scale):
        self.width = width + 1
        self.height = height + 1
        self.display_buffer_init = [
            [0] * self.width for _ in range(self.height)
        ]
        self.display_buffer = self.display_buffer_init
        self.scale = scale
        self.draw_flag = False

    def display_setup(self):
        self.screen = pygame.display.set_mode((
            self.width * self.scale,
            self.height * self.scale))
        self.surface = pygame.Surface(self.screen.get_size())
        self.surface = self.surface.convert()

    def update_display(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.display_buffer[y][x] == 1:
                    pygame.gfxdraw.box(
                        self.surface,
                        (x * self.scale, y * self.scale, self.scale,
                         self.scale),
                        Display.colors['white'])
        self.screen.blit(self.surface, (0, 0))
        self.draw_flag = False

    def set_pixel(self, x, y):
        """
            Sets a pixel inside the buffer to on if it is 0 and returns
            False. Otherwise sets the pixel to off and returns True.
        """
        print(x, y)
        if self.display_buffer[y][x] == 0:
            self.display_buffer[y][x] = 1
            return False
        else:
            self.display_buffer[y][x] = 0
            return True
