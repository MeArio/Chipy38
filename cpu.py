from collections import deque
import logging
import bit_utils
import math

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
fh = logging.FileHandler('last.log', mode='w')
fh.setLevel(logging.INFO)
logger.addHandler(fh)


class UnknownOpcodeException(Exception):
    def __init__(self, opcode):
        super(UnknownOpcodeException, self).__init__(
            "The opcode isn't valid {}".format(hex(opcode)))
        logger.error("The opcode isn't valid {}".format(hex(opcode)))


class CPU:
    def __init__(self, ram, display):
        self.registers = [0] * 16  # The CHIP8 has 16 registers
        self.memory = ram.memory
        self.fontset = ram.fontset
        self.display = display
        self.offset = ram.offset
        self.I = 0  # Adress register
        self.pc = 0  # Currently executing address
        self.delay_timer = 0  # 8-bit timer register
        self.sound_timer = 0  # When this isn't zero there should be a beep
        # The chip8 supports 16 levels of nested subroutines
        self.stack = deque(maxlen=16)
        self.stack_pointer = -1  # Points to the top-level stack instruction
        self.opcode = 0

        # Opcode lookup table decyphered by looking at the first byte

        self.operation_lookup = {
            0x0: self.zero_opcodes,  # opcodes starting with zero
            0x1: self.jmp_to_addr,
            0x2: self.call_subroutine,
            0x3: self.branch_if_equal_val,
            0x4: self.branch_if_not_equal_val,
            0x5: self.branch_if_equal_reg,
            0x6: self.set_reg_to_val,
            0x7: self.add_to_reg,
            0x8: self.logical_operations,
            0xD: self.draw_pixel_to_display,
            0xA: self.set_I_to_address,
            0xF: self.other_operations
        }

        # basically opcodes starting with 8 the last byte is the operation
        self.logical_operation_lookup = {
            0x0: self.set_reg_to_reg,
            0x1: self.bitwise_or,
            0x2: self.bitwise_and,
            0x3: self.bitwise_xor,
            0x4: self.add_reg_to_reg,
            0x5: self.sub_reg_from_reg,
            0x6: self.right_shift,
            0x7: self.subn_reg_from_reg,
            0x8: self.left_shift
        }

        self.other_operation_lookup = {
            0x33: self.bin_coded_dec
        }

    def load_fontset(self):
        for i, (_, _) in enumerate(zip(self.memory, self.fontset)):
                self.memory[i] = self.fontset[i]

    def load_rom(self, filename):
        cart = open(filename, 'rb')
        rom = cart.read()
        i = 0
        while i < len(rom):
            self.memory[i + self.offset] = rom[i]
            i += 1
        cart.close()

    def fetch_opcode(self):
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]

    def decode_opcode(self):
        # This makes sure I get only the first byte
        operation = (self.opcode & 0xF000) >> 12
        try:
            self.operation_lookup[operation]()
        except KeyError:
            raise UnknownOpcodeException(self.opcode)

    def update_timers(self):
        if (self.delay_timer > 0):
            self.delay_timer -= 1
        if (self.sound_timer > 0):
            self.delay_timer -= 1

    def run_cycle(self):
        self.fetch_opcode()
        self.decode_opcode()
        self.update_timers()
        self.pc += 2

    def initalize_cpu(self, filename):
        self.load_fontset()
        self.pc = self.offset
        self.load_rom(filename)

    def return_middle_registers(self, opcode):
        """
            Return a tuple consisting of the registers in between an opcode

            >>> return_middle_registers(8231)
            (2, 3)
        """
        registers = (opcode & 0x0FF0) >> 4
        register_x = (registers & 0xF0) >> 4
        register_y = registers & 0x0F
        return (register_x, register_y)

    # Here are the operations:

    def zero_opcodes(self):
        """ Opeartions that start with 0 are either
            0nnn - Jump to machine routine at  nnn (ignored)
            00E0 - Clear the display
            00EE - Return from a subroutine.
        """
        if self.opcode == 0x00E0:
            self.display.clear_display()
            logger.info("Cleared display")
        elif self.opcode == 0x00EE:
            logger.info("Returned from subroutine at {}".format(hex(self.pc)))
            self.pc = self.stack[self.stack_pointer]
            self.stack.pop()
            self.stack_pointer -= 1
            logger.info("to address at {}".format(hex(self.pc)))

    def logical_operations(self):
        operation = self.opcode & 0xF
        try:
            self.logical_operation_lookup[operation]()
        except KeyError:
            raise UnknownOpcodeException(self.opcode)

    def other_operations(self):
        operation = self.opcode & 0xFF
        try:
            self.other_operation_lookup[operation]()
        except KeyError:
            raise UnknownOpcodeException(self.opcode)

    def jmp_to_addr(self):
        """
            1nnn - Jump to location nnn.
            The interpreter sets the program counter to nnn.
        """
        self.pc = self.opcode & 0x0FFF
        logger.info("Jumped to address at {}".format(hex(self.pc)))

    def call_subroutine(self):
        """0x2nnn:
            The interpreter increments the stack pointer, then puts the current
            PC on the top of the stack. The PC is then set to nnn.
        """
        self.stack_pointer += 1
        self.stack.append(self.pc)
        self.pc = self.opcode & 0x0FFF
        logger.info("Called subroutine at {}".format(hex(self.pc)))

    def branch_if_equal_val(self):
        """
            3xkk -  Skip next instruction if Vx = kk.
            The interpreter compares register Vx to kk, and if they are equal,
            increments the program counter by 2.
        """
        register = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0xFF
        if self.registers[register] == value:
            self.pc += 2
            logger.info("Skipped {} because V{} and {} are equal".format(
                hex(self.pc - 2),
                register,
                value))

    def branch_if_not_equal_val(self):
        """
            4xkk - Skip next instruction if Vx != kk.
            The interpreter compares register Vx to kk, and if they are not
            equal, increments the program counter by 2.
        """
        register = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0xFF
        if self.registers[register] != value:
            self.pc += 2
            logger.info(
                "Didn't skip {} because V{} and {} are not equal".format(
                    hex(self.pc - 2),
                    register,
                    value))

    def branch_if_equal_reg(self):
        """
            5xy0 - Skip next instruction if Vx = Vy.
            The interpreter compares register Vx to register Vy, and if they
            are equal, increments the program counter by 2.
        """
        registers = self.return_middle_registers(self.opcode)

        if self.registers[registers[0]] == self.registers[registers[1]]:
            self.pc += 2
            logger.info(
              "Skipped {} because register V{} and V{} are equal to {}".format(
                 hex(self.pc - 2),
                 registers[0],
                 registers[1],
                 self.registers[registers[0]]))

    def set_reg_to_val(self):
        """
            6xkk - Set Vx = kk.
            The interpreter puts the value kk into register Vx.
        """
        register = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        self.registers[register] = value
        logger.info("Set register V{} to {}".format(register, value))

    def add_to_reg(self):
        """
           7xkk - Set Vx = Vx + kk.
           Adds the value kk to the value of register Vx, then stores the
           result in Vx.
        """
        register = (self.opcode & 0xF00) >> 8
        value = self.opcode & 0xFF
        sum = self.registers[register] + value
        if sum > 0xFF:
            sum = bit_utils.wrap_around(sum, 0xFF + 1)
        self.registers[register] = sum
        logger.info("Added {} to register V{}".format(value, register))

    def set_reg_to_reg(self):
        """
            8xy0 - Set Vx = Vy.
            Stores the value of register Vy in register Vx.
        """
        register = self.return_middle_registers(self.opcode)
        self.registers[register[0]] = self.registers[register[1]]
        logger.info("Set register V{} to V{}".format(register[0], register[1]))

    def bitwise_or(self):
        """
            8xy1 - Set Vx = Vx OR Vy.
            Performs a bitwise OR on the values of Vx and Vy, then stores the
            result in Vx. A bitwise OR compares the corrseponding bits from two
            values, and if either bit is 1, then the same bit in the result is
            also 1. Otherwise, it is 0.
        """
        register = self.return_middle_registers(self.opcode)
        self.registers[register[0]] = (
            self.registers[register[0]] | self.registers[register[1]])
        logger.info("Bitwise OR on V{} and V{} for {}".format(
            register[0],
            register[1]),
            self.registers[register[0]])

    def bitwise_and(self):
        """
            8xy2 - Set Vx = Vx AND Vy.
            Performs a bitwise AND on the values of Vx and Vy, then stores the
            result in Vx. A bitwise AND compares the corrseponding bits from
            two values, and if both bits are 1, then the same bit in the result
            is also 1. Otherwise, it is 0.
        """
        register = self.return_middle_registers(self.opcode)
        self.registers[register[0]] = (
            self.registers[register[0]] & self.registers[register[1]])
        logger.info("Bitwise AND on V{} and V{} for {}".format(
            register[0],
            register[1]),
            self.registers[register[0]])

    def bitwise_xor(self):
        """
            8xy3 - Set Vx = Vx XOR Vy.
            Performs a bitwise exclusive OR on the values of Vx and Vy, then
            stores the result in Vx. An exclusive OR compares the corrseponding
            bits from two values, and if the bits are not both the same, then
            the corresponding bit in the result is set to 1. Otherwise, it is 0
        """
        register = self.return_middle_registers(self.opcode)
        self.registers[register[0]] = (
            self.registers[register[0]] ^ self.registers[register[1]])
        logger.info("Bitwise AND on V{} and V{} for {}".format(
            register[0],
            register[1]),
            self.registers[register[0]])

    def add_reg_to_reg(self):
        """
            8xy4 - Set Vx = Vx + Vy, set VF = carry.
            The values of Vx and Vy are added together. If the result is
            greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0.
            Only the lowest 8 bits of the result are kept, and stored in Vx.
        """
        register = self.return_middle_registers(self.opcode)
        sum = self.registers[register[0]] + self.registers[register[1]]
        if sum > 0xFF:
            self.registers[0xF] = 1
            self.registers[register[0]] = sum & 0xFF
        else:
            self.registers[0xF] = 0
            self.registers[register[0]] = sum
        logger.info("Added V{} to V{} and got {}".format(
            register[0],
            register[1],
            self.registers[register[0]]))

    def sub_reg_from_reg(self):
        """
            8xy5 - Set Vx = Vx - Vy, set VF = NOT borrow.
            If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted
            from Vx, and the results stored in Vx.
        """
        register = self.return_middle_registers(self.opcode)
        if self.registers[register[0]] > self.registers[register[1]]:
            self.registers[0xF] = 1
            self.registers[register[0]] -= self.registers[register[1]]
        else:
            self.registers[0xF] = 0
            self.registers[register[0]] = (
                256
                + self.registers[register[0]]
                - self.registers[register[1]])
        # the 256 is there to simulate a wrap around of an unsigned integer
        logger.info("Subtracted V{} from V{} and got {}".format(
            register[1],
            register[0],
            self.registers[register[0]]))

    def draw_pixel_to_display(self):
        """
            Dxyn - Display n-byte sprite starting at memory location I at
            (Vx, Vy), set VF = collision.

            The interpreter reads n bytes from memory, starting at the address
            stored in I. These bytes are then displayed as sprites on screen at
            coordinates (Vx, Vy). Sprites are XORed onto the existing screen.
            If this causes any pixels to be erased, VF is set to 1, otherwise
            it is set to 0. If the sprite is positioned so part of it is
            outside the coordinates of the display, it wraps around to the
            opposite side of the screen.
        """
        register = self.return_middle_registers(self.opcode)
        x = self.registers[register[0]]
        y = self.registers[register[1]]
        height = self.opcode & 0xF

        self.registers[0xF] = 0

        x = bit_utils.wrap_around(x, self.display.width)
        y = bit_utils.wrap_around(y, self.display.height)

        for yline in range(0, height):
            pixels = self.memory[self.I + yline]
            y1 = bit_utils.wrap_around(y + yline, self.display.height)
            for xline in range(0, 8):
                x1 = bit_utils.wrap_around(x + xline, self.display.width)
                if pixels & (0x80 >> xline) != 0:
                    if self.display.set_pixel(x1, y1):
                        self.registers[0xF] = 1

        self.display.draw_flag = True
        logger.info("Drawing sprite from {} to {}".format(
            hex(self.I),
            hex(self.I + height)))

    def set_I_to_address(self):
        """
            Annn - Set I = nnn.
            The value of register I is set to nnn.
        """
        self.I = self.opcode & 0xFFF
        logger.info("Set I to {}".format(hex(self.I)))

    def right_shift(self):
        """
            8x06 - Set Vx = Vx SHR 1.
            If the least-significant bit of Vx is 1, then VF is set to 1,
            otherwise 0. Then Vx is divided by 2.
        """
        register = (self.opcode & 0xFFF) >> 8
        bits = self.registers[register]
        if bits & 0b1 == 1:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0

        self.registers[register] = self.registers[register] >> 1
        logger.info("Shifted register V{} 1 bit to the right got {}".format(
            register,
            hex(self.registers[register])))

    def subn_reg_from_reg(self):
        """
            8xy7 - Set Vx = Vy - Vx, set VF = NOT borrow.
            If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted
            from Vy, and the results stored in Vx.
        """
        register = self.return_middle_registers(self.opcode)
        if self.registers[register[1]] > self.registers[register[0]]:
            self.registers[0xF] = 1
            self.registers[register[0]] = (
                self.registers[register[1]]
                - self.registers[register[0]])
        else:
            self.registers[0xF] = 0
            self.registers[register[0]] = (
                256
                + self.registers[register[1]]
                - self.registers[register[0]])

        logger.info("Subtracted V{} from V{} and got {}".format(
            register[1],
            register[0],
            self.registers[register[0]]))

    def left_shift(self):
        """
            8x0E - Set Vx = Vx SHL 1.
            If the most-significant bit of Vx is 1, then VF is set to 1,
            otherwise to 0. Then Vx is multiplied by 2.
        """
        register = (self.opcode & 0xFFF) >> 8
        bits = self.registers[register]
        if bits & 0b1 == 1:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0

        self.registers[register] = self.registers[register] << 1
        logger.info("Shifted register V{} 1 bit to the left got {}".format(
            register,
            hex(self.registers[register])))

    def bin_coded_dec(self):
        """
            Fx33 - Store BCD representation of Vx in memory locations I, I+1,
            and I+2.
            The interpreter takes the decimal value of Vx, and places the
            hundreds digit in memory at location in I, the tens digit at
            location I+1, and the ones digit at location I+2.
        """
        register = (self.opcode & 0xFFF) >> 8
        value = self.registers[register]
        self.memory[self.I] = int(math.floor(value / 100))
        self.memory[self.I + 1] = int(math.floor(value % 100 / 10))
        self.memory[self.I + 2] = value % 10

    def load_mem_to_registers(self):
        """
        Fx65 - Read registers V0 through Vx from memory starting at location I.
        The interpreter reads values from memory starting at location I into
        registers V0 through Vx.
        """
        # Don't forget to add this to the lookup table after finishing it tomorrow.
        pass
