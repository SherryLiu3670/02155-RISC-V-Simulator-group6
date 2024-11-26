class RiscvSimulator:
    def __init__(self, program, memory_size = 8*1e6):
        self.registers = [0x00000000]*32
        self.pc = 0
        self.memory = [0] * memory_size
        self.program = program

    def load_program(self):
        for i in range(len(self.program)):
            self.memory[i] = self.program[i]

    def decode_inst(self):
        while (self.pc <= len(self.program)):
            instruction = self.memory[8*self.pc:9*self.pc-1]
            opcode = instruction & 0x7f

            if (opcode == 0b0110011): # R-type
                rd = instruction & 0xf80
                funct3 = instruction & 0x7000
                rs1 = instruction & 0xf8000
                rs2 = instruction & 0x1f00000
                funct7 = instruction & 0xfe000000
                self.R_instruction(rd, funct3, rs1, rs2, funct7)

            elif (opcode == 0b0010011 or opcode == 0b0000011 or opcode == 0b1100111): # I-type
                rd = (instruction & 0xf80) >> 7
                func3 = (instruction & 0x7000) >> 11 # 00: byte 01: half-word 11: word 
                # signed = instruction & 0x4000 # 0: signed, 1: unsigned
                rs1 = (instruction & 0xf8000) >> 15
                imm0_11 = (instruction & 0xfff00000) >> 20
                if (opcode == 0b0010011):
                    self.I_instruction(rd, func3, rs1, imm0_11)
                elif (opcode == 0b0000011):
                    self.I_L_instruction(rd, func3, rs1, imm0_11)
                elif (opcode == 1100111):
                    self.I_R_instruction(rd, func3, rs1, imm0_11)
                elif (opcode == 1110011):
                    self.I_E_instruction(rd, func3, rs1, imm0_11)


            elif (opcode == 0b0100011): # S-type
                imm0_4 = instruction & 0xf80
                size = instruction & 0x3000 # 00: byte 01: half-word 11: word 
                rs1 = instruction & 0xf8000
                rs2 = instruction & 0x1f00000
                imm5_11 = instruction & 0xfe000000
                self.S_instruction(imm0_4, size, rs1, rs2, imm5_11)

            elif (opcode == 0b1100011): # B-type
                imm_11 = (instruction & 0x80) >> 7
                imm1_4 = (instruction & 0xf00) >> 8
                func3 = (instruction & 0x7000) >> 12
                rs1 = (instruction & 0xf8000) >> 15
                rs2 = (instruction & 0x1f00000) >> 20
                imm5_10 = (instruction & 0x7e000000) >> 25
                imm_12 = (instruction & 0x80000000) >> 31

                imm1_4_shift = (imm1_4 << 1)
                imm5_10_shift = (imm5_10 << 5)
                imm_11_shifted = (imm_11 << 11)
                imm_12_shift = (imm_12 << 12)
                imm = imm_12_shift | imm_11_shifted | imm5_10_shift | imm1_4_shift | 0

                self.B_instruction(imm_11, imm1_4, func3, rs1, rs2, imm5_10, imm_12, imm)

            elif (opcode == 0b1101111): # J-type
                rd = (instruction & 0xf80) >> 7
                imm_20 = (instruction & 0x80000000) >> 11
                imm10_1 = (instruction & 0x7fe00000) >> 20
                imm_11 = (instruction & 0x100000) >> 9
                imm19_12 = (instruction & 0xff000)
                imm = imm_20 | imm19_12 | imm_11 | imm10_1 | 0
                self.J_instruction(rd, imm)

            elif (opcode == 0b0110111 or opcode ==0b0010111): # U-type
                rd = (instruction & 0xf80) >> 7
                imm31_12 = instruction & 0xfffff000
                if (opcode == 0b0110111):
                    self.U_L_instruction(rd, imm31_12)
                elif (opcode == 0b0010111):
                    self.U_A_instruction(rd, imm31_12)

            
        
        for i in range(32):
            print("register %d equals to" %i + self.registers[i])
            

    
    def R_instruction(self, rd, funct3, rs1, rs2, funct7):
        if funct3 == 0x0:
        
        

    def I_instruction(self, rd, func3, rs1, imm0_11):
        if func3 == 0x0:
            self.registers[rd] =  self.registers[rs1] + self.msb_extend(imm0_11, 32)
            self.pc += 4
            print("addi register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x4:
            self.registers[rd] = self.registers[rs1]^self.zero_extend(imm0_11,32)
            self.pc += 4
            print("xori register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x6:
            self.registers[rd] = self.registers[rs1] | self.zero_extend(imm0_11,32)
            self.pc += 4
            print("ori register[%d], register[%d], %d" %(rd, rs1, imm0_11)) 
        elif func3 == 0x7:
            self.registers[rd] = self.registers[rs1] & self.zero_extend(imm0_11, 32)
            self.pc += 4
            print("ANDi register[%d], register[%d], %d" %(rd, rs1, imm0_11))   
        elif func3 == 0x1:
            self.registers[rd] = (self.registers[rs1] << (imm0_11 & 0b11111)) & 0xffffffff
            self.pc += 4
            print("slli register[%d], register[%d], %d" %(rd, rs1, (imm0_11 & 0b11111))) 
        elif func3 == 0x5:
            if (imm0_11 & 0xfe0) == 0x00:
                self.registers[rd] = self.zero_extend(self.registers[rs1] >> (imm0_11 & 0b11111), 32)          
                self.pc += 4
                print("srli register[%d], register[%d], %d" %(rd, rs1, (imm0_11 & 0b11111))) 
            elif  (imm0_11 & 0xfe0) == 0x20:
                imm0_4 = imm0_11 & 0b11111
                self.registers[rd] = self.msb_extend(self.registers[rs1] >> imm0_4, 32)   
                self.pc += 4
                print("srai register[%d], register[%d], %d" %(rd, rs1, (imm0_11 & 0b11111))) 
        elif func3 == 0x2:
            rs1 = self.registers[rs1]
            sign_imm0_11 = self.to_signed(imm0_11, 12)
            self.registers[rd] = lambda: 1 if rs1 < sign_imm0_11 else 0
            self.pc += 4
            print("slti register[%d], register[%d], %d" %(rd, rs1, imm0_11)) 
        elif func3 == 0x3:
            rs1 = self.registers[rs1]
            self.registers[rd] = lambda rs1, imm0_11: 1 if rs1 < imm0_11 else 0
            self.pc += 4
            print("sltiu register[%d], register[%d], %d" %(rd, rs1, imm0_11)) 

        self.decode_inst(self)

    def I_L_instruction(self, rd, func3, rs1, imm0_11):
        if func3 == 0x0:
            self.registers[rd] = self.msb_extend(self.memory[rs1 + imm0_11] & 0xff)
            self.pc += 4
            print("lb register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x1:
            self.registers[rd] = self.msb_extend(self.memory[rs1 + imm0_11] & 0xffff)
            self.pc += 4
            print("lh register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x2:
            self.registers[rd] = self.msb_extend(self.memory[rs1 + imm0_11] & 0xffffffff)
            self.pc += 4
            print("lw register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x4:
            self.registers[rd] = self.zero_extend(self.memory[rs1 + imm0_11] & 0xff)
            self.pc += 4
            print("lbu register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x5:
            self.registers[rd] = self.zero_extend(self.memory[rs1 + imm0_11] & 0xffff)
            self.pc += 4
            print("lhu register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        
        self.decode_inst(self)

    def S_instruction(self, imm0_4, size, rs1, rs2, imm5_11):

    def B_instruction(self, imm_11, imm1_4, func3, rs1, rs2, imm5_10, imm12, imm):
        if func3 == 0x0:
            if self.registers[rs1] = self.registers[rs2]:
                self.pc += self.to_signed(imm, 13) * 4
            else:
                self.pc += 4
            print("beq register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x1:
            if self.registers[rs1] != self.registers[rs2]:
                self.pc += self.to_signed(imm, 13) * 4
            else:
                self.pc += 4
            print("bne register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x4:
            if self.to_signed(self.registers[rs1], 32) < self.to_signed(self.registers[rs2], 32):
                self.pc += self.to_signed(imm, 13) * 4
            else:
                self.pc += 4
            print("blt register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x5:
            if self.to_signed(self.registers[rs1], 32) >= self.to_signed(self.registers[rs2], 32):
                self.pc += self.to_signed(imm, 13) * 4
            else:
                self.pc += 4
            print("bge register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x6:
            if self.zero_extend(self.registers[rs1], 32) < self.zero_extend(self.registers[rs2], 32):
                self.pc += self.to_signed(imm, 13) * 4
            else:
                self.pc += 4
            print("bltu register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x7:
            if self.zero_extend(self.registers[rs1], 32) >= self.zero_extend(self.registers[rs2], 32):
                self.pc += self.to_signed(imm, 13) * 4
            else:
                self.pc += 4
            print("bgeu register[%d], register[%d], %d" %(rs1, rs2, imm))
        
        self.decode_inst(self)


    def J_instruction(self, rd, imm):
        self.registers[rd] = self.pc + 4
        self.pc += self.to_signed(imm, 21) * 4  
        print("jal register[%d], %d" %(rd, imm))
        self.decode_inst(self)

    def I_R_instruction(self, rd, func3, rs1, imm0_11):
        if func3 == 0x0:
            self.registers[rd] = self.pc + 4
            self.pc = self.registers[rs1] + self.to_signed(imm0_11, 12) 
        print("jalr register[%d], register[%d], %d" %(rd, rs1, imm0_11))

        self.decode_inst(self)

    def U_L_instruction(self, rd, imm31_12):
        self.registers[rd] = self.to_signed(imm31_12, 20)
        print("lui register[%d], %d" %(rd, imm31_12))
        self.decode_inst(self)

    def U_A_instruction(self, rd, imm31_12):
        self.registers[rd] = self.pc + self.to_signed(imm31_12, 20)
        print("auipc register[%d], %d" %(rd, imm31_12))
        self.decode_inst(self)

    def I_E_instruction(self, rd, func3, rs1, imm0_11):
        if func3 == 0x0 and imm0_11 == 0x0:
            print("ecall Transfer control to OS")
            syscall_number = self.registers[17]  # a7 is registers[17]
        
            if syscall_number == 1: 
                print("System Call: Print Integer")
                print("Value:", self.registers[11]) 

            elif syscall_number == 10:  # exit program
                print("System Call: Exit Program")

            else:
                print(f"Unknown System Call: {syscall_number}")

        else:
            print("Unhandled I-type instruction")




    def msb_extend(value, bits):
        mask = 1 << (bits - 1)  
        extended_value = (value & ((1 << bits) - 1))  
        if extended_value & mask:
            extended_value -= (1 << bits)
        return extended_value
    
    def zero_extend(value, bits):
        extended_value = value & ((1 << bits) - 1)
        return extended_value
    
    def to_signed(value, bits):
        if value & (1 << (bits - 1)):
            return value - (1 << bits)
        return value


def read_binary_to_instruction_list(file_path):
    try:
        with open(file_path, "rb") as binary_file:
            binary_data = binary_file.read()

        instruction_size = 4 
        instructions = []

        for i in range(0, len(binary_data), instruction_size):
            instruction = binary_data[i:i + instruction_size]
            instructions.append(instruction.hex()) 

        return instructions
    except Exception as e:
        print(f"error: {e}")

def main():
    instructions = read_binary_to_instruction_list("")
    riskv = RiscvSimulator(instructions)
    riskv.load_program()
    riskv.decode_inst()
    
 
if __name__ == "__main__":
    main()

    






