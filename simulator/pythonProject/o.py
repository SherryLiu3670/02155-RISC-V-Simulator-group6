# instruction = 0b100011100011
# imm_11 = (instruction & 0x80) >> 7
# imm1_4 = (instruction & 0xf00) >> 8
# print(f"imm: {bin(imm1_4)}")
# print(f"imm_11: {imm_11}")

# instruction = 0b11100010101010011000100001100011
# imm_11 = (instruction & 0x80) >> 7
# imm1_4 = (instruction & 0xf00) >> 8
# imm5_10 = (instruction & 0x7e000000) >> 25
# imm_12 = (instruction & 0x80000000) >> 31
#
# imm1_4_shift = (imm1_4 << 1)
# imm5_10_shift = (imm5_10 << 5)
# imm_11_shifted = (imm_11 << 11)
# imm_12_shift = (imm_12 << 12)
# imm = imm_12_shift | imm_11_shifted | imm5_10_shift | imm1_4_shift | 0
# print(f"imm11: {bin(imm_11)}")
# print(f"imm1-4: {bin(imm1_4)}")
# print(f"imm5: {bin(imm5_10)}")
# print(f"imm12: {bin(imm_12)}")
# print(f"imm: {bin(imm)}")

a = 0b11111  # 5 位二进制，十进制是 -1（有符号）
b = 0b00001  # 5 位二进制，十进制是 1（有符号）
print(f"a: {a}")
# if a < b:
#     print("yes")
# else:
#     print("No")