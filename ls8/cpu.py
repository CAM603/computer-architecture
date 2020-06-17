"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # 256 bytes of memory
        self.reg = [0] * 8  # 8 general purpose registers
        self.pc = 0  # program counter, index of the current instruction
        # stack pointer points at the value at the top of the stack (most recently pushed), or at address F4 (244) if the stack is empty
        self.sp = 244
        self.running = False
        self.operand_a = 0
        self.operand_b = 0

        self.branchtable = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100000: self.ADD,
            0b10000100: self.ST
        }

    def test(self):
        print(self.reg[7])

    def ST(self):
        # Store value in registerB in the address stored in registerA.
        # Value in registerB
        val = self.reg[self.operand_b]
        # Address stored in registerA
        address = self.reg[self.operand_a]
        # write to memory
        self.ram[address] = val

    def ADD(self):
        self.alu('ADD', self.operand_a, self.operand_b)
        self.pc += 3

    def RET(self):
        # Pop the value from the top of the stack and store it in the PC
        next_inst = self.ram[self.sp]
        self.sp += 1
        self.pc = next_inst

    def CALL(self):
        # Get address of the instruction directly after CALL
        next_inst = self.pc + 2
        # Push it on the stack
        self.sp -= 1
        self.ram[self.sp] = next_inst
        # PC is set to the address stored in the given reg
        self.pc = self.reg[self.operand_a]

    def POP(self):
        val = self.ram[self.sp]

        self.reg[self.operand_a] = val
        self.sp += 1
        self.pc += 2
        # print("POP")

    def PUSH(self):
        # decrement sp
        self.sp -= 1
        # Push the value in the given register on the stack.
        val = self.reg[self.operand_a]
        self.ram[self.sp] = val
        self.pc += 2
        # print('PUSH')

    def HLT(self):
        self.running = False
        # print("HLT")

    def LDI(self):
        self.reg[self.operand_a] = self.operand_b
        self.pc += 3
        # print("LDI")

    def PRN(self):
        print(self.reg[self.operand_a])
        self.pc += 2
        # print("PRN")

    def MUL(self):
        self.alu('MUL', self.operand_a, self.operand_b)
        self.pc += 3
        # print("MUL")

    def load(self, file):
        """Load a program into memory."""
        address = 0

        try:
            with open(file, 'r') as reader:
                # read and print the entire file line by line
                for line in reader:
                    line_arr = line.split()
                    # if a binary string, store in ram
                    for word in line_arr:
                        try:
                            instruction = int(word, 2)
                            self.ram[address] = instruction
                            address += 1
                        except ValueError:
                            continue
        except IOError:
            print('Please specify a valid file name, thank you :)')

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        ir = self.ram[self.pc]

        while self.running:
            ir = self.ram[self.pc]  # Instruction Register
            self.operand_a = self.ram_read(self.pc + 1)
            self.operand_b = self.ram_read(self.pc + 2)

            self.branchtable[ir]()

    def ram_read(self, mar):
        # MAR: Memory Address Register contains the address that is being read or written to
        return self.ram[mar]

    def ram_write(self, mdr, address):
        # MDR: Memory Data Register contains the data that was read or the data to write
        self.ram[address] = mdr
