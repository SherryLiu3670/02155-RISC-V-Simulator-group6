class RiscvSimulator:
    def __init__(self, memory_size = 1024):
        self.registers = [0x00000000]*32
        self.pc = 0
        self.memory = [0] * memory_size
        self.program = [0x00200093, # addi x1, x0, 2
                        0x00300113, # addi x2, x0, 3
                        0x002081b3 ]# add x3, x1, x2

    def load_program(self):
        for i in range(len(self.program)):
            self.memory[i] = self.program[i]

    def decode_inst(self):
        while (self.pc <= len(self.program)):
            instruction = self.memory[32*self.pc]
            opcode = instruction & 0x7f

            if (opcode == 0b0110011): # R-type
                rd = instruction & 0xf80
                funct3 = instruction & 0x7000
                rs1 = instruction & 0xf8000
                rs2 = instruction & 0x1f00000
                funct7 = instruction & 0xfe000000
                self.R_instruction(rd, funct3, rs1, rs2, funct7)

            elif (opcode == 0b0000011 or opcode == 0b0000011): # I-type
                rd = (instruction & 0xf80) >> 7
                func3 = (instruction & 0x7000) >> 11 # 00: byte 01: half-word 11: word 
                # signed = instruction & 0x4000 # 0: signed, 1: unsigned
                rs1 = (instruction & 0xf8000) >> 15
                imm0_11 = (instruction & 0xfff00000) >> 20
                if (opcode == 0b0000011):
                    self.I_instruction(rd, func3, rs1, imm0_11)
                elif (opcode == 0b0000011):
                    self.I_L_instruction(rd, func3, rs1, imm0_11)


            elif (opcode == 0b0100011): # S-type
                imm0_4 = instruction & 0xf80
                size = instruction & 0x3000 # 00: byte 01: half-word 11: word 
                rs1 = instruction & 0xf8000
                rs2 = instruction & 0x1f00000
                imm5_11 = instruction & 0xfe000000
                self.S_instruction(imm0_4, size, rs1, rs2, imm5_11)

            elif (opcode == 0b1100011): # B-type
                imm_11 = instruction & 0x80
                imm1_4 = instruction & 0xf00
                funct3 = instruction & 0x7000
                rs1 = instruction & 0xf8000
                rs2 = instruction & 0x1f00000
                imm5_10 =  instruction & 0x7e000000
                imm12 = instruction & 0x80000000
                self.B_instruction(self, imm_11, imm1_4, funct3, rs1, rs2, imm5_10, imm12)
        
        for i in range(32):
            print("register %d equals to" %i + self.registers[i])
            

    
    def R_instruction(self, rd, funct3, rs1, rs2, funct7):
        if funct3 == 0x0:
            if funct7 == 0x00:
                self.registers[rd] = self.registers[rs1] + self.registers[rs2]
                pc += 1
            elif funct7 == 0x20 and rd == rs1 - rs2:
                return "sub"
        
        

    def I_instruction(self, rd, func3, rs1, imm0_11):
        if func3 == 0x0:
            self.registers[rd] =  self.registers[rs1] + self.msb_extend(imm0_11, 32)
            self.pc += 1
            print("addi register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x4:
            self.registers[rd] = self.registers[rs1]^self.zero_extend(imm0_11,32)
            self.pc += 1
            print("xori register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x6:
            self.registers[rd] = self.registers[rs1] | self.zero_extend(imm0_11,32)
            self.pc += 1
            print("ori register[%d], register[%d], %d" %(rd, rs1, imm0_11)) 
        elif func3 == 0x7:
            self.registers[rd] = self.registers[rs1] & self.zero_extend(imm0_11, 32)
            self.pc += 1
            print("ANDi register[%d], register[%d], %d" %(rd, rs1, imm0_11))   
        elif func3 == 0x1:
            self.registers[rd] = (self.registers[rs1] << (imm0_11 & 0b11111)) & 0xffffffff
            self.pc += 1
            print("slli register[%d], register[%d], %d" %(rd, rs1, (imm0_11 & 0b11111))) 
        elif func3 == 0x5:
            if (imm0_11 & 0xfe0) == 0x00:
                self.registers[rd] = self.zero_extend(self.registers[rs1] >> (imm0_11 & 0b11111), 32)          
                self.pc += 1
                print("srli register[%d], register[%d], %d" %(rd, rs1, (imm0_11 & 0b11111))) 
            elif  (imm0_11 & 0xfe0) == 0x20:
                imm0_4 = imm0_11 & 0b11111
                self.registers[rd] = self.msb_extend(self.registers[rs1] >> imm0_4, 32)   
                self.pc += 1
                print("srai register[%d], register[%d], %d" %(rd, rs1, (imm0_11 & 0b11111))) 
        elif func3 == 0x2:
            rs1 = self.registers[rs1]
            sign_imm0_11 = self.to_signed(imm0_11, 12)
            self.registers[rd] = lambda: 1 if rs1 < sign_imm0_11 else 0
            self.pc += 1
            print("slti register[%d], register[%d], %d" %(rd, rs1, imm0_11)) 
        elif func3 == 0x3:
            rs1 = self.registers[rs1]
            self.registers[rd] = lambda rs1, imm0_11: 1 if rs1 < imm0_11 else 0
            self.pc += 1
            print("sltiu register[%d], register[%d], %d" %(rd, rs1, imm0_11)) 

        self.decode_inst(self)

    def I_L_instruction(self, rd, func3, rs1, imm0_11):
        if func3 == 0x0:
            self.registers[rd] = self.msb_extend(self.memory[rs1 + imm0_11] & 0xff)
            self.pc += 1
            print("lb register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x1:
            self.registers[rd] = self.msb_extend(self.memory[rs1 + imm0_11] & 0xffff)
            self.pc += 1
            print("lh register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x2:
            self.registers[rd] = self.msb_extend(self.memory[rs1 + imm0_11] & 0xffffffff)
            self.pc += 1
            print("lw register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x4:
            self.registers[rd] = self.zero_extend(self.memory[rs1 + imm0_11] & 0xff)
            pc += 1
            print("lbu register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x5:
            self.registers[rd] = self.zero_extend(self.memory[rs1 + imm0_11] & 0xffff)
            self.pc += 1
            print("lhu register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        
        self.decode_inst(self)

    def S_instruction(self, imm0_4, size, rs1, rs2, imm5_11):

    def B_instruction(self, imm_11, imm1_4, funct3, rs1, rs2, imm5_10, imm12):

        

        




