import pyglet
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

if __name__ == '__main__':
    print("sup")
    aram.load_rom('breakout.ch8')
    print(aram.memory)
    pyglet.app.run()
