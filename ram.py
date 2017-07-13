class RAM:
    def __init__(self, mem_size, offset):
        self.MEM_SIZE = mem_size  # Memory size
        self.memory = [0] * mem_size  # Memory array
        self.offset = offset

    def load_rom(self, filename):
        rom = open(filename, 'rb').read()
        i = 0
        while i < len(rom):
            self.memory[i + self.offset] = hex(rom[i])
            i += 1
