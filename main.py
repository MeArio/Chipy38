import pygame
from cpu import CPU
from ram import RAM
from display import Display
import argparse
import logging
import config

logger = logging.getLogger(__name__)
fh = logging.FileHandler('last.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)

parser = argparse.ArgumentParser()
parser.add_argument("rom", help="path to rom", type=str)
parser.add_argument(
    "-s",
    help="sets the window scale",
    dest="scale",
    type=int,
    default=10)

parser.add_argument(
    "-t",
    help="sets the delay between cpu cycles in ms",
    dest="timer",
    type=int,
    default=1)

args = parser.parse_args()

# The Chip8 had 4KB of RAM so that means an array of 4096 bytes
MEM_SIZE = 4096
WIDTH = 64
HEIGHT = 32
SCALE = 10
OFFSET = 0x200
TIMER = pygame.USEREVENT + 1
TIMERS_UPDATE = 17

# Initializing all the emulator objects
display = Display(WIDTH, HEIGHT, SCALE)
ram = RAM(MEM_SIZE, OFFSET)
cpu = CPU(ram, display)
keys = config.keys


def main_loop(args):
    """
        Runs the main loop.
    """
    timer = args.timer
    display.scale = args.scale
    display.display_setup()

    cpu.initalize_cpu(args.rom)
    pygame.time.set_timer(TIMER, TIMERS_UPDATE)
    running = True

    while running:
        cpu.keys = [0] * 0xF
        pygame.time.wait(timer)
        cpu.run_cycle()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                cpu.keys[keys[chr(event.key)]] = 1
            if event.type == TIMER:
                cpu.update_timers()
            if event.type == pygame.QUIT:
                running = False

        if display.draw_flag:
            display.update_display()
            pygame.display.flip()

        if cpu.opcode == 0x00FD:
            running = False


if __name__ == '__main__':
    try:
        main_loop(args)
    except Exception:
        logger.info(
            " Current Addr: {}\n Curr Opcode: {}\n Nxt Opcode: {}".format(
                hex(cpu.pc),
                hex(cpu.memory[cpu.pc] << 8 | cpu.memory[cpu.pc + 1]),
                hex(cpu.memory[cpu.pc+1] << 8 | cpu.memory[cpu.pc + 2])))
        logger.exception("Here be crash")

    pygame.quit()
