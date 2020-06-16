"""CPU functionality."""

import sys
import glob
import os


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # 256 bytes of memory
        self.reg = [0] * 8  # 8 general purpose registers
        self.pc = 0  # program counter, index of the current instruction
        # Instruction definitions
        self.HLT = 0b00000001
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.MUL = 0b10100010

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
            print(self.reg[reg_a])
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
        running = True

        while running:
            ir = self.ram[self.pc]  # Instruction Register
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == self.HLT:  # end the loop
                running = False
            elif ir == self.LDI:  # sets a specified register to a specified value
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif ir == self.PRN:  # print numeric value stored in the given register.
                print(self.reg[operand_a])
                self.pc += 2
            elif ir == self.MUL:
                return self.alu('MUL', operand_a, operand_b)
            else:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit(1)

    def ram_read(self, mar):
        # MAR: Memory Address Register contains the address that is being read or written to
        return self.ram[mar]

    def ram_write(self, mdr, address):
        # MDR: Memory Data Register contains the data that was read or the data to write
        self.ram[address] = mdr
