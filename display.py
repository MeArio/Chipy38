import pygame
import pygame.gfxdraw


class Display():
    colors = {'white': (255, 255, 255)}

    def __init__(self, width, height, scale):
        self.width = width
        self.height = height
        self.display_buffer = [[0] * self.width for _ in range(self.height)]
        self.scale = scale

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
