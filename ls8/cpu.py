"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # 256 bytes of memory
        self.reg = [0] * 8  # 8 general purpose registers
        self.pc = 0  # program counter, index of the current instruction
        # stack pointer, index of the top of the stack (most recently pushed)
        self.sp = self.reg[7]  # R7 is reserved as the stack pointer (SP)
        self.reg[7] = 0xF4  # sp points to F4 if the stack is empty
        self.running = False
        self.operand_a = 0
        self.operand_b = 0
        # Flags
        self.e = 0  # Equal flag
        self.l = 0  # Less than flag
        self.g = 0  # Greater than flag
        # dictionary of functions that you can index by opcode value
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
            0b10000100: self.ST,
            0b01010100: self.JMP,
            0b10100111: self.CMP,
            0b01010110: self.JNE,
            0b01010101: self.JEQ,
            0b10000011: self.LD,
            0b01001000: self.PRA,
            0b01100101: self.INC,
            0b01100110: self.DEC,
        }

    def test(self):
        print(self.reg[7])

    def DEC(self):  # This is an instruction handled by the ALU
        self.alu('DEC', self.operand_a)
        self.pc += 2

    def INC(self):  # This is an instruction handled by the ALU
        self.alu('INC', self.operand_a)
        self.pc += 2

    # Loads registerA with the value at the memory address stored in registerB.
    def LD(self):
        value = self.reg[self.operand_b]
        self.reg[self.operand_a] = self.ram[value]
        self.pc += 3

    def JEQ(self):  # If E flag is true, jump to address stored in given register
        # If E flag is true, 1
        if self.e:
            # get address stored in given register
            address = self.reg[self.operand_a]
            # Set PC to the address
            self.pc = address
        else:
            self.pc += 2

    def JNE(self):  # If E flag is false, jump to address stored in given register
        # If E flag is false, 0
        if not self.e:
            # get address stored in given register
            address = self.reg[self.operand_a]
            # Set PC to the address
            self.pc = address
        else:
            self.pc += 2

    def CMP(self):  # Compare the values in two registers
        # This is an instruction handled by the ALU
        self.alu('CMP', self.operand_a, self.operand_b)
        self.pc += 3

    def JMP(self):  # Jump to the address stored in the given register.
        # Get address stored in the given register
        address = self.reg[self.operand_a]
        # Set PC to the address
        self.pc = address

    def ST(self):  # Store value in registerB in the address stored in registerA.
        # Value in registerB
        val = self.reg[self.operand_b]
        # Address stored in registerA
        address = self.reg[self.operand_a]
        # write to memory
        self.ram[address] = val

    def ADD(self):  # Add two registers and store result in registerA.
        self.alu('ADD', self.operand_a, self.operand_b)
        self.pc += 3

    def RET(self):  # Return from subroutine CALL
        # Get value from the top of the stack
        next_inst = self.ram[self.sp]
        self.sp += 1
        # store it in the PC
        self.pc = next_inst

    def CALL(self):  # Calls a function at the address stored in the register
        # Get address of the instruction directly after CALL
        next_inst = self.pc + 2
        self.sp -= 1
        # Push it on the stack
        self.ram[self.sp] = next_inst
        # PC is set to the address stored in the given reg
        self.pc = self.reg[self.operand_a]

    def POP(self):  # Pop value at top of stack into given register.
        # Get value from the address pointed to by SP
        val = self.ram[self.sp]
        # Set value to the given register
        self.reg[self.operand_a] = val
        self.sp += 1
        self.pc += 2
        # print("POP")

    def PUSH(self):  # Push the value in the given register on the stack.
        # Decrement sp
        self.sp -= 1
        # Get the value in the given register
        val = self.reg[self.operand_a]
        # Push the value on the stack.
        self.ram[self.sp] = val
        self.pc += 2
        # print('PUSH')

    def HLT(self):  # Stop run loop
        self.running = False
        # print("HLT")

    def LDI(self):  # Set the value of a register to an integer.
        self.reg[self.operand_a] = self.operand_b
        self.pc += 3
        # print("LDI")

    def PRN(self):  # Print numeric value stored in the given register
        print(self.reg[self.operand_a])
        self.pc += 2
        # print("PRN")

    def PRA(self):  # Print alpha character value stored in the given register
        value = self.reg[self.operand_a]
        print(chr(value))
        self.pc += 2

    def MUL(self):  # Multiply two registers and store result in registerA.
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
                    for word in line_arr:
                        # if a binary string, store in ram
                        try:
                            instruction = int(word, 2)
                            self.ram[address] = instruction
                            address += 1
                        except ValueError:
                            continue
        except IOError:
            print('Please specify a valid file name, thank you :)')

    def alu(self, op, reg_a=None, reg_b=None):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            # If they are equal
            self.e = 0
            self.l = 0
            self.g = 0

            if self.reg[reg_a] == self.reg[reg_b]:
                # Set the Equal E flag to 1, otherwise set it to 0
                self.e = 1
            # If registerA is less than registerB
            elif self.reg[reg_a] < self.reg[reg_b]:
                # Set Less-than L flag to 1, otherwise set it to 0
                self.l = 1
            # If registerA is greater than registerB
            elif self.reg[reg_a] > self.reg[reg_b]:
                # Set the Greater-than G flag to 1, otherwise set it to 0
                self.g = 1
        elif op == 'INC':  # Increment the value in the given register by 1
            self.reg[reg_a] += 1
        elif op == 'DEC':  # Decrement the value in the given register by 1
            self.reg[reg_a] -= 1
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

        while self.running:
            # Instruction Register contains a copy of the currently executing instruction
            ir = self.ram[self.pc]
            # Grab the next two bytes of data after the PC
            self.operand_a = self.ram_read(self.pc + 1)
            self.operand_b = self.ram_read(self.pc + 2)

            self.branchtable[ir]()

    def ram_read(self, mar):
        # MAR: Memory Address Register contains the address that is being read or written to
        return self.ram[mar]

    def ram_write(self, mdr, address):
        # MDR: Memory Data Register contains the data that was read or the data to write
        self.ram[address] = mdr
