#include

public class IsaSim {
    
    static int pc;
    static int reg[] = new int[32]; // 定义32个寄存器，真实模拟RISC-V架构
    static int progr[] = {
            // 示例指令
            0x00200093, // addi x1, x0, 2
            0x00300113, // addi x2, x0, 3
            0x002081b3, // add x3, x1, x2
    };

    public static void main(String[] args) {
        System.out.println("Hello RISC-V World!");
        pc = 0;
        
        while (pc < progr.length * 4) {  // 使用pc来控制循环
            int instr = progr[pc >> 2];
            int opcode = instr & 0x7F; // 取操作码，最低7位

            switch (opcode) {
                case 0x33: // R类型指令
                    executeRType(instr);
                    break;
                case 0x13: // I类型指令（如addi）
                    executeIType(instr);
                    break;
                // 更多指令类型
                default:
                    System.out.println("Opcode " + opcode + " not yet implemented");
                    break;
            }

            pc += 4; // 下一条指令
            printRegisters(); // 打印寄存器状态
        }

        System.out.println("Program exit");
    }

    // R类型指令：如add、sub
    public static void executeRType(int instr) {
        int rd = (instr >> 7) & 0x1F;
        int funct3 = (instr >> 12) & 0x7;
        int rs1 = (instr >> 15) & 0x1F;
        int rs2 = (instr >> 20) & 0x1F;
        int funct7 = (instr >> 25) & 0x7F;

        switch (funct3) {
            case 0x0: // ADD
                if (funct7 == 0x00) {
                    reg[rd] = reg[rs1] + reg[rs2];
                } else if (funct7 == 0x20) { // SUB
                    reg[rd] = reg[rs1] - reg[rs2];
                }
                break;
            case 0x7: // AND
                reg[rd] = reg[rs1] & reg[rs2];
                break;
            // 其他R类型指令...
        }
    }

    // I类型指令：如addi, load
    public static void executeIType(int instr) {
        int rd = (instr >> 7) & 0x1F;
        int funct3 = (instr >> 12) & 0x7;
        int rs1 = (instr >> 15) & 0x1F;
        int imm = instr >> 20; // 立即数

        switch (funct3) {
            case 0x0: // ADDI
                reg[rd] = reg[rs1] + imm;
                break;
            // 其他I类型指令...
        }
    }

    // 打印寄存器的值
    public static void printRegisters() {
        for (int i = 0; i < reg.length; ++i) {
            System.out.print("x" + i + ": " + reg[i] + " ");
        }
        System.out.println();
    }
}
