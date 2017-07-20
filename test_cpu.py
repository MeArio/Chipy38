import unittest
import mock
import bit_utils

from cpu import CPU, UnknownOpcodeException
import ram


class TestCPU(unittest.TestCase):
    """
        Testing sounded like a nice idea.
    """
    def setUp(self):
        self.MEM_SIZE = 4096
        self.OFFSET = 0x200
        self.display = mock.MagicMock()
        self.ram = ram.RAM(self.MEM_SIZE, self.OFFSET)
        self.cpu = CPU(self.ram, self.display)

    def test_ret_from_subroutine(self):
        """
            0x00EE - Return from subroutine
            Tests if the program can return from subroutines in the range 0x200
            - 0xFFFF
        """
        for address in (0x200, 0xFFFF, 0x10):
            self.cpu.stack.append(address)
            self.cpu.stack_pointer += 1
            self.cpu.pc = 0
            self.cpu.opcode = 0x00EE
            self.cpu.decode_opcode()
            self.assertEqual(self.cpu.pc, address)

    def test_jump_to_address(self):
        """
            1nnn - Jump to address
            Tests that the program can correctly jump to addresses between
            0x200 and 0xFFF
        """
        for address in (0x200, 0xFFF, 0x10):
            self.cpu.pc = 0
            self.cpu.opcode = 0x1FFF & (address | 0xF000)
            self.cpu.decode_opcode()
            print(self.cpu.opcode)
            self.assertEqual(self.cpu.pc, (address & 0x0FFF))

    def test_unknown_opcode(self):
        self.opcode = 0x7FFF
        self.assertRaises(UnknownOpcodeException)

    def test_call_subroutine(self):
        """
            2nnn - Call subroutine
            Tests that the program can correctly call subroutines between 0x200
             and 0xFFF
        """
        for address in range(0x200, 0xFFF, 0x10):
            self.cpu.pc = 0
            self.cpu.opcode = 0x2FFF & (address | 0xF000)
            self.cpu.call_subroutine()
            self.assertEqual(self.cpu.stack_pointer, 0)
            self.assertEqual(self.cpu.stack[self.cpu.stack_pointer], 0)
            self.assertEqual(self.cpu.pc, address)
            self.cpu.stack.pop()
            self.cpu.stack_pointer -= 1

    def test_branch_if_equal_true_val(self):
        """
            0x3xkk -  Skip next instruction if Vx = kk.
            Tests if the interpreter skips instructions for all values of VX
        """
        for value in range(0x00, 0xFF, 1):
            self.cpu.pc = 0
            self.cpu.registers[0xC] = value
            self.cpu.opcode = value | 0x3C00
            self.cpu.branch_if_equal_val()
            self.assertEqual(self.cpu.pc, 2)

    def test_branch_if_equal_false_val(self):
        """
            0x3xkk -  Skip next instruction if Vx = kk.
            Tests if the interpreter doesn't skip an instruction iv Vx != kk
        """
        self.cpu.pc = 0
        self.cpu.opcode = 0x3C20
        self.cpu.branch_if_equal_val()
        self.assertNotEqual(self.cpu.pc, 2)

    def test_branch_if_equal_reg(self):
        """
            5xy0 - Skip next instruction if Vx = Vy.
            Tests if it skips for every register combionation,
            yes I know I'm testing too many values
        """
        for register_combination in range(0x00, 0xFF, 1):
            self.cpu.pc = 0
            register_x = register_combination & 0x0F
            register_y = (register_combination & 0xF0) >> 4
            self.cpu.opcode = ((register_combination | 0xF00) & 0x5FF) << 4
            self.cpu.registers[register_x] = register_combination
            self.cpu.registers[register_y] = register_combination
            self.cpu.branch_if_equal_reg()
            self.assertEqual(self.cpu.pc, 2)

    def test_set_register_to_value(self):
        """
            6xkk - Set Vx = kk.
            Tests all the possible values Vx can be set to
        """
        for register in self.cpu.registers:
            for value in range(0, 0xFF, 1):
                self.cpu.opcode = ((0x60 | register) << 8) | value
                self.cpu.set_reg_to_val()
                self.assertEqual(self.cpu.registers[register], value)

    def test_set_register_register(self):
        """
            8xy0 - Set Vx = Vy.
            Tests all the possible register combinations.
        """
        for register_combination in range(0, 0xFF, 0x1):
            register_x = register_combination & 0x0F
            register_y = (register_combination & 0xF0) >> 4
            self.cpu.opcode = ((register_combination | 0xF00) & 0x8FF) << 4
            self.cpu.registers[register_y] = register_combination
            self.cpu.set_reg_to_reg()
            self.assertEqual(
                self.cpu.registers[register_x],
                self.cpu.registers[register_y])
            self.cpu.registers[register_x] = 0
            self.cpu.registers[register_y] = 0

        def test_logical_operations_decoding(self):
            self.cpu.opcode = 0x8231
            self.cpu.registers[2] = 4
            self.cpu.decode_opcode()
            self.assertEqual(self.cpu.registers[3], 4)

        def test_add_flag(self):
            """
                8xy4 - Set Vx = Vx + Vy, set VF = carry.
                Tests if the operations sets the carry flag to 1 correctly and
                that the sum is right.
            """
            for sum in range(0xFF, 0xFFF, 0x10):
                rightsum = (0x1 + sum) & 0xFF
                self.cpu.opcode = 0x8124
                self.cpu.registers[1] = 0x1
                self.cpu.registers[2] = sum
                self.cpu.registers[0xf] = 0
                self.cpu.add_reg_to_reg()
                self.assertEqual(self.cpu.registers[0xf], 1)
                self.assertEqual(self.cpu.registers[1], rightsum)

        def test_bitutils_wrap_around(self):
            for number in range(0, 64 * 4):
                x = bit_utils.wrap_around(number, 64)
                self.assertTrue(x < 64)


if __name__ == '__main__':
    unittest.main()
