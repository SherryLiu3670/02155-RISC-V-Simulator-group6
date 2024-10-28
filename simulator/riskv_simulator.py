class RiscvSimulator:
    def __init__(self, memory_size = 1024):
        self.registers = [0]*32
        self.pc = 0
        self.memory = [0] * memory_size

    def load_program(self, program: list):
        for i in range(len(program)):
            self.memory[i] = program[i]

    def decode_inst(self, instruction):
        opcode = instruction & 0x7f

        if (opcode == 0b0110011): # R-type
            rd = instruction & 0xf80
            funct3 = instruction & 0x7000
            rs1 = instruction & 0xf8000
            rs2 = instruction & 0x1f00000
            funct7 = instruction & 0xfe000000
            self.R_instruction(rd, funct3, rs1, rs2, funct7)

        elif (opcode == 0b0000011): # I-type
            rd = instruction & 0xf80
            size = instruction & 0x3000 # 00: byte 01: half-word 11: word 
            signed = instruction & 0x4000 # 0: signed, 1: unsigned
            rs1 = instruction & 0xf8000
            imm0_11 = instruction & 0xfff00000
            self.I_instruction(rd, size, signed, rs1, imm0_11)

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
    
    def R_instruction(self, rd, funct3, rs1, rs2, funct7):
        if funct3 == 0x0:
        
        

    def I_instruction(self, rd, size, signed, rs1, imm0_11):

    def S_instruction(self, imm0_4, size, rs1, rs2, imm5_11):

    def B_instruction(self, imm_11, imm1_4, funct3, rs1, rs2, imm5_10, imm12):

        

        




