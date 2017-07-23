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

parser.add_argument(
    "-st",
    help="activates the stepper, key if f",
    action='store_true',
    dest='toggle')

parser.add_argument(
    "-d",
    help="display debug info on screen",
    action='store_true',
    dest='debug',
    default=False)

args = parser.parse_args()

# The Chip8 had 4KB of RAM so that means an array of 4096 bytes
MEM_SIZE = 4096
WIDTH = 64
HEIGHT = 32
SCALE = 10
OFFSET = 0x200
TIMER = pygame.USEREVENT + 1
TIMERS_UPDATE = 17
DEBUG = args.debug
if DEBUG:
    pygame.key.set_repeat(1, 100)

# Initializing all the emulator objects
display = Display(WIDTH, HEIGHT, SCALE, DEBUG)
ram = RAM(MEM_SIZE, OFFSET)
cpu = CPU(ram, display)
keys = config.keys

pause_toggle = True


def wait():
    global pause_toggle
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    cpu.dump_memory("memory")
                if event.key == pygame.K_p:
                    pause_toggle = False
                    return
                if event.key == pygame.K_f:
                    return
            if event.type == TIMER:
                cpu.update_timers()


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
    global pause_toggle

    while running:
        cpu.keys = [0] * 0xF
        pygame.time.wait(timer)
        if args.toggle and pause_toggle:
            wait()
        cpu.run_cycle()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause_toggle = True
                try:
                    cpu.keys[keys[chr(event.key)]] = 1
                except Exception:
                    pass
            if event.type == TIMER:
                cpu.update_timers()
            if event.type == pygame.QUIT:
                running = False

        if display.draw_flag or DEBUG:
            display.update_display()
            if DEBUG:
                display.draw_registers(
                    cpu.registers,
                    cpu.pc,
                    cpu.I,
                    cpu.opcode)
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
