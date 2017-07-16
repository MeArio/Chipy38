import unittest
import mock

from cpu import CPU
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
            self.cpu.opcode = 0x1FFF & (address | 0xF000)  # here be bug
            self.cpu.decode_opcode()
            print(self.cpu.opcode)
            self.assertEqual(self.cpu.pc, (address & 0x0FFF))


if __name__ == '__main__':
    unittest.main()
