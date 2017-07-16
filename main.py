import pygame
from cpu import CPU
from ram import RAM
from display import Display


# The Chip8 had 4KB of RAM so that means an array of 4096 bytes
MEM_SIZE = 4096
WIDTH = 64
HEIGHT = 32
SCALE = 10
OFFSET = 0x200

aram = RAM(MEM_SIZE, OFFSET)
adisplay = Display(WIDTH, HEIGHT, SCALE)
acpu = CPU(aram, adisplay)

pygame.init()
running = True

adisplay.display_setup()

if __name__ == '__main__':
    print("sup")
    acpu.initalize_cpu('breakout.ch8')
    print(acpu.memory)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        adisplay.update_display()
        pygame.display.flip()
    pygame.quit()
