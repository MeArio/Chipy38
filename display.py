import pygame
import pygame.gfxdraw


class Display():
    colors = {'white': (255, 255, 255)}

    def __init__(self, width, height, scale, debug=False):
        self.debug = debug
        self.debug_offset = 256
        self.width = width
        self.height = height
        if debug:
            self.width += int(self.debug_offset / scale)
        self.display_buffer = [
            [0] * self.width for _ in range(self.height)
        ]
        self.scale = scale
        self.draw_flag = False
        self.font_size = 9
        self.font = pygame.font.SysFont('Arial', self.font_size)

    def display_setup(self):
        self.screen = pygame.display.set_mode((
            self.width * self.scale,
            self.height * self.scale))
        self.surface = pygame.Surface(self.screen.get_size())
        self.surface = self.surface.convert()
        pygame.display.set_caption("Chip8py3 Emulator")

    def update_display(self):
        self.surface.fill((0, 0, 0, 0))  # Clears the display
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

    def clear_display(self):
        self.display_buffer = [
            [0] * self.width for _ in range(self.height)
        ]
        self.draw_flag = True

    def set_pixel(self, x, y):
        """
            Sets a pixel inside the buffer to on if it is 0 and returns
            False. Otherwise sets the pixel to off and returns True.
        """
        if self.display_buffer[y][x] == 0:
            self.display_buffer[y][x] = 1
            return False

        else:
            self.display_buffer[y][x] = 0
            return True

    def draw_registers(self, registers, pc, i, opcode):
        opcode_label = self.font.render(
            "OP: {}".format(hex(opcode)),
            1,
            (255, 255, 255))
        self.screen.blit(
            opcode_label,
            (
                self.width
                * self.scale
                - self.debug_offset
                + self.font_size,
                0))

        pc_label = self.font.render(
            "PC = {}".format(hex(pc)),
            1,
            (255, 255, 255))
        self.screen.blit(
            pc_label,
            (
                self.width
                * self.scale
                - self.debug_offset
                / self.scale
                - self.font_size * 3, 0))

        i_label = self.font.render(
            "I = {}".format(hex(i)),
            1,
            (255, 255, 255))
        self.screen.blit(
            i_label,
            (
                self.width
                * self.scale
                - self.debug_offset
                / self.scale
                - self.font_size * 3, 16))
        for i, register in enumerate(registers):
            register_label = self.font.render(
                "V{}: {}".format(i, register),
                1,
                (255, 255, 255)
                )
            self.screen.blit(
                register_label,
                (
                    self.width
                    * self.scale
                    - self.debug_offset
                    / self.scale
                    - self.font_size * 3, (i+2) * 16))
