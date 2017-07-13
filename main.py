import pyglet
from cpu import CPU
from ram import RAM
from display import Display


# The Chip8 had 4KB of RAM so that means an array of 4096 bytes
MEM_SIZE = 4096
WIDTH = 64
HEIGHT = 32
SCALE = 10

aram = RAM(MEM_SIZE)
adisplay = Display(WIDTH, HEIGHT, SCALE)
acpu = CPU(aram, adisplay)

if __name__ == '__main__':
    print("sup")

pyglet.app.run()
