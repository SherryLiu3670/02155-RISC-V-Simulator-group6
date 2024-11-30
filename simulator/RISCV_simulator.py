import os

class RiscvSimulator:
    def __init__(self, program, memory_size = int(1e6)):
        self.registers = [0x00000000]*32
        self.registers[2] = 0
        self.memory = [0x00] * memory_size
        self.program = program

    def load_program(self):
        for i in range(len(self.program)):
            instruction = self.program[i] 
            instruction_bytes = instruction.to_bytes(4, 'little')  
            self.memory[i * 4:(i + 1) * 4] = instruction_bytes 

    def decode_inst(self):
        while self.registers[2] < len(self.memory):
            instruction = self.memory[self.registers[2]:self.registers[2]+4]
            if len(instruction) < 4:
                print(f"Incomplete instruction at PC={self.registers[2]}")
                break 
            instruction = int.from_bytes(bytes(instruction), 'little')  # Small endian
            opcode = instruction & 0x7f

            if (opcode == 0b0110011): # R-type
                rd = (instruction & 0xf80) >> 7
                funct3 = (instruction & 0x7000) >> 12
                rs1 = (instruction & 0xf8000) >> 15
                rs2 = (instruction & 0x1f00000) >> 20
                funct7 = (instruction & 0xfe000000) >> 25
                self.R_instruction(rd, funct3, rs1, rs2, funct7)

            elif (opcode == 0b0010011 or opcode == 0b0000011 or opcode == 0b1100111): # I-type
                rd = (instruction & 0xf80) >> 7
                func3 = (instruction & 0x7000) >> 12 # 00: byte 01: half-word 11: word 
                # signed = instruction & 0x4000 # 0: signed, 1: unsigned
                rs1 = (instruction & 0xf8000) >> 15
                imm0_11 = (instruction & 0xfff00000) >> 20
                if (opcode == 0b0010011):
                    self.I_instruction(rd, func3, rs1, imm0_11)
                elif (opcode == 0b0000011):
                    self.I_L_instruction(rd, func3, rs1, imm0_11)
                elif (opcode == 0b1100111):
                    self.I_R_instruction(rd, func3, rs1, imm0_11)
                elif (opcode == 0b1110011):
                    print("enter ecall")
                    self.I_E_instruction(rd, func3, rs1, imm0_11)


            elif (opcode == 0b0100011): # S-type
                imm0_4 = (instruction & 0xf80) >> 7
                size = (instruction & 0x3000) >> 12 # 00: byte 01: half-word 11: word 
                rs1 = (instruction & 0xf8000) >> 15
                rs2 = (instruction & 0x1f00000) >> 20
                imm5_11 = (instruction & 0xfe000000) >> 25 
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

            else:
                for i in range(32):
                    print("register %d equals to: %d " %(i,int(self.registers[i])))
                print("Finished")
                break
        
        
            

    
    def R_instruction(self, rd, funct3, rs1, rs2, funct7):
        if funct3 == 0x0:  # ADD or SUB
            if funct7 == 0x00:
                self.registers[rd] = self.to_signed(self.registers[rs1],32) + self.to_signed(self.registers[rs2],32)
                print(f"add x{rd}, x{rs1}, x{rs2}")
            elif funct7 == 0x20:
                self.registers[rd] = self.to_signed(self.registers[rs1],32) - self.to_signed(self.registers[rs2],32)
                print(f"sub x{rd}, x{rs1}, x{rs2}")
        elif funct3 == 0x7:  # AND
            self.registers[rd] = self.registers[rs1] & self.registers[rs2]
            print(f"and x{rd}, x{rs1}, x{rs2}")
        elif funct3 == 0x6:  # OR
            self.registers[rd] = self.registers[rs1] | self.registers[rs2]
            print(f"or x{rd}, x{rs1}, x{rs2}")
        elif funct3 == 0x4:  # XOR
            self.registers[rd] = self.registers[rs1] ^ self.registers[rs2]
            print(f"xor x{rd}, x{rs1}, x{rs2}")
        elif funct3 == 0x1:  # SLL (Shift Left Logical)
#           self.registers[rd] = (self.registers[rs1] << (self.registers[rs2] & 0x1F)) & 0xFFFFFFFF
            self.registers[rd] = (self.registers[rs1] << (self.registers[rs2])) & 0xFFFFFFFF
            print(f"sll x{rd}, x{rs1}, x{rs2}")
        elif funct3 == 0x5:  # SRL or SRA
            if funct7 == 0x00:  # SRL (Shift Right Logical)
#               self.registers[rd] = (self.registers[rs1] >> (self.registers[rs2] & 0x1F)) & 0xFFFFFFFF
                if self.registers[rs1] < 0:
                    self.registers[rd] = self.zero_extend((self.registers[rs1] + (1 << 32)) >> (self.registers[rs2] & 0x1F), 32)  
                else:
                    self.registers[rd] = (self.registers[rs1] >> (self.registers[rs2] & 0x1F)) & 0xFFFFFFFF
                print(f"srl x{rd}, x{rs1}, x{rs2}")
            elif funct7 == 0x20:  # SRA (Shift Right Arithmetic)
                self.registers[rd] = self.msb_extend(self.registers[rs1] >> (self.registers[rs2] & 0x1F), 32, 32)
                print(f"sra x{rd}, x{rs1}, x{rs2}")
        elif funct3 == 0x2:  # SLT (Set Less Than)
            self.registers[rd] = 1 if self.to_signed(self.registers[rs1], 32) < self.to_signed(self.registers[rs2], 32) else 0
            print(f"slt x{rd}, x{rs1}, x{rs2}")
        elif funct3 == 0x3:  # SLTU (Set Less Than Unsigned)
            self.registers[rd] = 1 if self.registers[rs1] < self.registers[rs2] else 0
            print(f"sltu x{rd}, x{rs1}, x{rs2}")
        self.registers[2] += 4  
        
        

    def I_instruction(self, rd, func3, rs1, imm0_11):
        if func3 == 0x0:
            self.registers[rd] =  self.msb_extend(self.to_signed(self.registers[rs1],32) + self.to_signed(imm0_11, 12), 32,32)
            self.registers[2] += 4
            print("addi register[%d], register[%d], %d" %(rd, rs1, self.to_signed(imm0_11,12)))
        elif func3 == 0x4:
            print("xori")
            self.registers[rd] = self.zero_extend(self.registers[rs1]^self.zero_extend(imm0_11,32),32)
            self.registers[2] += 4
            print("xori register[%d], register[%d], %d" %(rd, rs1, imm0_11))
        elif func3 == 0x6:
            self.registers[rd] = self.zero_extend(self.registers[rs1] | self.zero_extend(imm0_11,32),32)
            self.registers[2] += 4
            print("ori register[%d], register[%d], %d" %(rd, rs1, imm0_11)) 
        elif func3 == 0x7:
            self.registers[rd] = self.zero_extend(self.registers[rs1] & self.zero_extend(imm0_11, 32),32)
            self.registers[2] += 4
            print("ANDi register[%d], register[%d], %d" %(rd, rs1, imm0_11))   
        elif func3 == 0x1:
            self.registers[rd] = (self.registers[rs1] << (imm0_11 & 0b11111)) & 0xffffffff
            self.registers[2] += 4
            print("slli register[%d], register[%d], %d" %(rd, rs1, (imm0_11 & 0b11111))) 
        elif func3 == 0x5:
            if ((imm0_11 & 0xfe0) >> 5) == 0x00:
                if self.registers[rs1] < 0:
                    self.registers[rd] = self.zero_extend((self.registers[rs1] + (1 << 32)) >> (imm0_11 & 0b11111), 32)  
                else:
                    self.registers[rd] = self.zero_extend(self.registers[rs1] >> (imm0_11 & 0b11111), 32)      
                self.registers[2] += 4
                print("srli register[%d], register[%d], %d" %(rd, rs1, (imm0_11 & 0b11111))) 
            elif  ((imm0_11 & 0xfe0) >> 5) == 0x20:
                imm0_4 = imm0_11 & 0b11111
                # if self.registers[rs1] < 0:
                #     self.registers[rd] = self.msb_extend((self.registers[rs1] >> imm0_4) | ((1 << 32) - 1) << (32 - imm0_4), 32, 32) 
                # else:
                self.registers[rd] = self.msb_extend(self.registers[rs1] >> imm0_4, 32, 32)
                self.registers[2] += 4
                print("srai register[%d], register[%d], %d" %(rd, rs1, (imm0_11 & 0b11111))) 
        elif func3 == 0x2:
            rs1 = self.to_signed(self.registers[rs1],32)
            sign_imm0_11 = self.to_signed(imm0_11, 12)
            if rs1 < sign_imm0_11:
                self.registers[rd] = 1
            else:
                self.registers[rd] = 0
            self.registers[2] += 4
            print("slti register[%d], register[%d], %d" %(rd, rs1, imm0_11)) 
        elif func3 == 0x3:
            rs1 = self.registers[rs1]
            if rs1 < imm0_11:
                self.registers[rd] = 1
            else: 
                self.registers[rd] = 0
            self.registers[2] += 4
            print("sltiu register[%d], register[%d], %d" %(rd, rs1, imm0_11)) 


    def I_L_instruction(self, rd, func3, rs1, imm0_11):
        if func3 == 0x0:
            self.registers[rd] = self.msb_extend(self.memory[self.registers[rs1] + self.to_signed(imm0_11,12)], 32, 32)
            # print(rd)
            # print(self.registers[rd])
            # print("address of memory", rs1 + self.to_signed(imm0_11,12))
            self.registers[2] += 4
            print("lb register[%d], register[%d], %d" %(rd, rs1, self.to_signed(imm0_11,12)))
        elif func3 == 0x1:
            load_hw = self.zero_extend(self.memory[self.registers[rs1] + self.to_signed(imm0_11, 12)],8) | (self.memory[self.registers[rs1] + self.to_signed(imm0_11,12) + 1] << 8)
            self.registers[rd] = self.msb_extend(load_hw, 32, 32)
            self.registers[2] += 4
            print("lh register[%d], register[%d], %d" %(rd, rs1, self.to_signed(imm0_11,12)))
            # print(self.registers[rd])
        elif func3 == 0x2:
            load_w = self.zero_extend(self.memory[self.registers[rs1] + self.to_signed(imm0_11,12)],8) | self.zero_extend(self.memory[self.registers[rs1] + self.to_signed(imm0_11,12) + 1] << 8,16) | self.zero_extend(self.memory[self.registers[rs1] + self.to_signed(imm0_11,12) + 2] << 16, 24) | self.memory[self.registers[rs1] + self.to_signed(imm0_11,12) + 3] << 24  
            self.registers[rd] = self.msb_extend(load_w, 32, 32)
            self.registers[2] += 4
            print("lw register[%d], register[%d], %d" %(rd, rs1, self.to_signed(imm0_11,12)))
            # print(self.registers[rd])
        elif func3 == 0x4:
            self.registers[rd] = self.zero_extend(self.memory[self.registers[rs1] + self.to_signed(imm0_11,12)], 32)
            self.registers[2] += 4
            print("lbu register[%d], register[%d], %d" %(rd, rs1, self.to_signed(imm0_11,12)))
        elif func3 == 0x5:
            load_uhw = self.memory[self.registers[rs1] + self.to_signed(imm0_11,12)] | (self.memory[self.registers[rs1] + self.to_signed(imm0_11,12) + 1] << 8)
            self.registers[rd] = self.zero_extend(load_uhw, 32)
            self.registers[2] += 4
            print("lhu register[%d], register[%d], %d" %(rd, rs1, self.to_signed(imm0_11,12)))


    def S_instruction(self, imm0_4, size, rs1, rs2, imm5_11):
        imm = self.to_signed(((imm5_11 << 5) | imm0_4),12)  # Combine the immediate parts
        address = self.zero_extend(self.registers[rs1] + imm, 32)
        if size == 0x0:  # SB (Store Byte)
            self.memory[address] = self.msb_extend(self.registers[rs2] & 0x000000FF, 8, 8)
            print(f"sb x{rs2}, {imm}(x{rs1})")
            print(address, self.memory[address:address+1])
        elif size == 0x1:  # SH (Store Half-Word)
            self.memory[address] = self.msb_extend(self.registers[rs2] & 0x000000FF, 8, 8)
            self.memory[address+1] = self.msb_extend(((self.registers[rs2] & 0x0000FF00) >> 8),8, 8)
            print(f"sh x{rs2}, {imm}(x{rs1})")
            print(address, self.memory[address:address+2])
        elif size == 0x2:  # SW (Store Word)
            self.memory[address]= self.msb_extend(self.to_signed(self.registers[rs2] & 0x000000FF,8), 8, 8)
            self.memory[address+1] = self.msb_extend(self.to_signed(((self.registers[rs2] & 0x0000FF00) >> 8), 8),8 ,8)
            self.memory[address+2] = self.msb_extend(self.to_signed(((self.registers[rs2] & 0x00FF0000) >> 16),8),8, 8)
            self.memory[address+3] = self.msb_extend(self.to_signed(((self.registers[rs2] & 0xFF000000) >> 24),8),8, 8)
            print(f"sw x{rs2}, {imm}(x{rs1})")
            print(address, self.memory[address:address+4])
        self.registers[2] += 4

    def B_instruction(self, imm_11, imm1_4, func3, rs1, rs2, imm5_10, imm12, imm):
        if func3 == 0x0:
            if self.registers[rs1] == self.registers[rs2]:
                self.registers[2] += self.to_signed(imm, 13)
            else:
                self.registers[2] += 4
            print("beq register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x1:
            if self.registers[rs1] != self.registers[rs2]:
                self.registers[2] += self.to_signed(imm, 13)
            else:
                self.registers[2] += 4
            print("bne register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x4:
            if self.to_signed(self.registers[rs1], 32) < self.to_signed(self.registers[rs2], 32):
                self.registers[2] += self.to_signed(imm, 13)
            else:
                self.registers[2] += 4
            print("blt register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x5:
            if self.to_signed(self.registers[rs1], 32) >= self.to_signed(self.registers[rs2], 32):
                self.registers[2] += self.to_signed(imm, 13)
            else:
                self.registers[2] += 4
            print("bge register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x6:
            if self.to_unsigned(self.registers[rs1], 32) < self.to_unsigned(self.registers[rs2], 32):
                self.registers[2] += self.to_signed(imm, 13)
            else:
                self.registers[2] += 4
            print("bltu register[%d], register[%d], %d" %(rs1, rs2, imm))
        elif func3 == 0x7:
            if self.to_unsigned(self.registers[rs1], 32) >= self.to_unsigned(self.registers[rs2], 32):
                self.registers[2] += self.to_signed(imm, 13)
            else:
                self.registers[2] += 4
            print("bgeu register[%d], register[%d], %d" %(rs1, rs2, imm))
        


    def J_instruction(self, rd, imm):
        self.registers[rd] = self.registers[2] + 4
        self.registers[2] += self.to_signed(imm, 21)
        print("jal register[%d], %d" %(rd, imm))


    def I_R_instruction(self, rd, func3, rs1, imm0_11):
        if func3 == 0x0:
            self.registers[rd] = self.registers[2] + 4
            self.registers[2] = self.zero_extend(self.zero_extend(self.registers[rs1],32) + self.to_signed(imm0_11, 12),32) 
        print("jalr register[%d], register[%d], %d" %(rd, rs1, self.to_signed(imm0_11,12)))

    def U_L_instruction(self, rd, imm31_12):
        self.registers[rd] = self.to_signed(imm31_12, 32)
        self.registers[2] += 4
        print("lui register[%d], %d" %(rd, self.to_signed(imm31_12,32)))

    def U_A_instruction(self, rd, imm31_12):
        self.registers[rd] = self.zero_extend(self.registers[2] + self.to_signed(imm31_12, 32),32)
        self.registers[2] += 4
        print("auipc register[%d], %d" %(rd, self.to_signed(imm31_12,32)))

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


    def msb_extend(self,value,original_bits, target_bits):
        if value & (1 << (original_bits - 1)):
            original_bits += 1  
        sign_bit = 1 << (original_bits - 1)
        if value & sign_bit: # negative
            extend_value = value | ((-1) << target_bits -1)
        else: # positive
            extend_value = value & ((1 << target_bits) - 1)
        return extend_value
    
    def zero_extend(self,value, bits):
        extended_value = value & ((1 << bits) - 1)
        return extended_value
    
    def to_signed(self, value, bits):
        mask = (1 << bits) - 1
        value &= mask
        if value & (1 << (bits - 1)):
            return value - (1 << bits)
        return value
    
    def to_unsigned(self, value, bits):
        mask = (1 << bits) - 1
        return value & mask
    

def read_binary_to_instruction_list(file_path):
    print('-->>',os.getcwd())
    try:
        with open(file_path, "rb") as binary_file:
            binary_data = binary_file.read()

        instruction_size = 4 
        instructions = []

        for i in range(0, len(binary_data), instruction_size):
            if len(binary_data[i:i + instruction_size]) < instruction_size:
                print(f"Incomplete instruction at offset {i}")
                break
            instruction = int.from_bytes(binary_data[i:i + instruction_size], 'little')
            instructions.append(instruction) 

        return instructions
    except Exception as e:
        print(f"error: {e}")

def main():
    path = os.path.join(os.getcwd(), "test_sh.bin")
    instructions = read_binary_to_instruction_list(path)
    riskv = RiscvSimulator(instructions)
    riskv.load_program()
    riskv.decode_inst()
    

 
if __name__ == "__main__":
    main()

    






