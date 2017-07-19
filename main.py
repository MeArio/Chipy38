import pygame
from cpu import CPU
from ram import RAM
from display import Display
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("rom", help="path to rom", type=str)
args = parser.parse_args()

# The Chip8 had 4KB of RAM so that means an array of 4096 bytes
MEM_SIZE = 4096
WIDTH = 64
HEIGHT = 32
SCALE = 10
OFFSET = 0x200
TIMER = pygame.USEREVENT + 1


def main_loop(args):
    """
        Runs the main loop.
    """
    display = Display(WIDTH, HEIGHT, SCALE)
    display.display_setup()
    ram = RAM(MEM_SIZE, OFFSET)
    cpu = CPU(ram, display)
    cpu.initalize_cpu(args.rom)
    pygame.time.set_timer(TIMER, 17)
    running = True

    while running:
        pygame.time.wait(1)
        cpu.run_cycle()

        for event in pygame.event.get():
            if event.type == TIMER:
                cpu.update_timers()
            if event.type == pygame.QUIT:
                running = False

        if cpu.opcode == 0x00FD:
            running = False


if __name__ == '__main__':
    main_loop(args)
    pygame.quit()
