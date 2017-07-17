import unittest
import mock

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

    def test_branch_if_equal_true(self):
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

    def test_branch_if_equal_false(self):
        """
            0x3xkk -  Skip next instruction if Vx = kk.
            Tests if the interpreter doesn't skip an instruction iv Vx != kk
        """
        self.cpu.pc = 0
        self.cpu.opcode = 0x3C20
        self.cpu.branch_if_equal_val()
        self.assertNotEqual(self.cpu.pc, 2)


if __name__ == '__main__':
    unittest.main()
