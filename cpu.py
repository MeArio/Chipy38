class CPU:
    def __init__(self, ram, display):
        self.registers = [0] * 16  # The CHIP8 has 16 registers
        self.memory = ram.memory
        self.offset = ram.offset
        self.I = 0  # Adress register
        self.pc = 0  # Currently executing address
        self.delay_timer = 0  # 8-bit timer register
        self.sound_timer = 0  # When this isn't zero there should be a beep
        # The chip8 supports 16 levels of nested subroutines
        self.stack = [0] * 16
        self.stack_pointer = 0  # Points to the top-level stack instruction
        self.opcode = 0

    def load_rom(self, filename):
        rom = open(filename, 'rb').read()
        i = 0
        while i < len(rom):
            self.memory[i + self.offset] = rom[i]
            i += 1

    def fetch_opcode(self):
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]

    def initalize_cpu(self, filename):
        self.load_rom(filename)
        self.pc = self.offset
        self.fetch_opcode()
        print(self.opcode)
