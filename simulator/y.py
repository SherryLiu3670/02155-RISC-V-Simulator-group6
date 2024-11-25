
# imm_11 = 0b1       # imm[11] 位
# imm4_1 = 0b1000    # imm[4:1] 位
# imm10_5 = 0b101010 # imm[10:5] 位
# imm12 = 0b0        # imm[12] 位

# # 将每个字段移位到合适的位置
# imm_11_shifted = (imm_11 << 11)  # imm[11] 位移到第 7 位
# imm4_1_shifted = (imm4_1 << 1)  # imm[4:1] 位移到第 1 位
# imm10_5_shifted = (imm10_5 << 5)  # imm[10:5] 位移到第 20 位
# imm12_shifted = (imm12 << 12)   # imm[12] 位移到第 31 位

# # 将这些部分组合起来
# final_binary = imm12_shifted | imm10_5_shifted | imm_11_shifted | imm4_1_shifted | 0
# print("组合后的二进制：", bin(final_binary))
