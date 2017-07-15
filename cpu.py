class CPU:
    def __init__(self, ram, display):
        self.registers = [0] * 16  # The CHIP8 has 16 registers
        self.memory = ram.memory
        self.display = display
        self.offset = ram.offset
        self.I = 0  # Adress register
        self.pc = 0  # Currently executing address
        self.delay_timer = 0  # 8-bit timer register
        self.sound_timer = 0  # When this isn't zero there should be a beep
        # The chip8 supports 16 levels of nested subroutines
        self.stack = [0] * 16
        self.stack_pointer = 0  # Points to the top-level stack instruction
        self.opcode = 0

        # Opcode lookup table decyphered by looking at the first byte

        self.operation_lookup = {
            0x0: self.zero_opcodes,  # opcodes starting with zero
            0x1: self.jmp_to_addr,
            0x2: self.call_subroutine
        }

    def load_rom(self, filename):
        rom = open(filename, 'rb').read()
        i = 0
        while i < len(rom):
            self.memory[i + self.offset] = rom[i]
            i += 1
        rom.close()

    def fetch_opcode(self):
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]

    def decode_opcode():
        pass

    def initalize_cpu(self, filename):
        self.load_rom(filename)
        self.pc = self.offset
        self.fetch_opcode()
        print(self.opcode)

    # Here are the operations:

    def zero_opcodes(self):
        """ Opeartions that start with 0 are either
            0x0nnn - Jump to machine routine at  nnn (ignored)
            0x00E0 - Clear the display
            0x00EE - Return from a subroutine.
        """
        if self.opcode == 0x00E0:
            self.display.clear_display()
        elif self.opcode == 0x00EE:
            self.pc = self.stack[self.stack_pointer]
            self.stack.pop()
            self.stack_pointer -= 1

    def jmp_to_addr(self):
        """ 0x1nnn:
              The interpreter sets the program counter to nnn.
        """
        self.pc = self.opcode & 0x0FFF

    def call_subroutine(self):
        """0x2nnn:
            The interpreter increments the stack pointer, then puts the current
            PC on the top of the stack. The PC is then set to nnn.
        """
        self.stack_pointer += 1
        self.stack[self.stack_pointer] = self.pc
        self.pc = self.opcode & 0x0FFF
