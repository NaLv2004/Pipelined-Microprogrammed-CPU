def int_to_8bit_binary(num):
    return "{0:08b}".format(num)


# ======================================== INSTRUCTION SET CONFIGURATIONS ==========================================
# instruction_set_dict = {
#     "add": "00000000",
#     "sub": "00000001",
#     "slt": "00000010",
#     "and": "00000011",
#     "or": "00000100",
#     "xor": "00000101",
#     "sll": "00000110",
#     "srl": "00000111",
#     "addi": "00100000",
#     "slti": "00100001",
#     "andi": "00100010",
#     "ori": "00100011",
#     "xori": "00100100",
#     "slli": "00100101",
#     "srli": "00100110",
#     "jal": "01000000",
#     "beq": "01100000",
#     "bne": "01100001",
#     "blt": "01100010",
#     "bltu": "01100011",
#     "load": "10000000",
#     "store": "10000001"
# }




# 1. register , register operations
# Assembly format: op, rs1[i], rs2[j], rd[k]
# machine code: [31:24],opcode  [23:16], i(binary)  [15:8], j(binary)  [7:0], k(binary)
# opcode : 00000+func_code, func_code=001~111, respectively for add, sub, and, or, xor, sll, srl
# 2. register , memory operations
# 2.1  operand 1 is in memory, operand 2 is in register file
# Assembly format: op, rs1[i], mem[j], rd[k]
# machine code: [31:24],opcode  [23:16], i(binary)  [15:8], j(binary)  [7:0], k(binary)
# opcode : 00010+func_code, func_code=001~111, respectively for add, sub, and, or, xor, sll, srl
# 2.2  operand 1 is in register file, operand 2 is in memory
# Assembly format: op, rs1[i], mem[j], rd[k]
# machine code: [31:24],opcode  [23:16], i(binary)  [15:8], j(binary)  [7:0], k(binary)
# opcode : 00001+func_code, func_code=001~111, respectively for add, sub, and, or, xor, sll, srl
# 3. register , immediate operations
# Assembly format: op, rs1[i], imm, rd[k]
# machine code: [31:24],opcode  [23:16], i(binary)  [15:8], imm(binary)  [7:0], k(binary)
# opcode : 00100+func_code, func_code=001~111, respectively for add, sub, and, or, xor, sll, srl
# 4. unconditional branch
# Assembly format: jump, imm
# machine code: [31:24],opcode  [23:16], imm(binary), [15:0], 00000000
# opcode : 01000000 (only 1 unconditional branch instruction)
# 5. conditional branch
# Assembly format: beq, rs1[i], rs2[j], imm
# machine code: [31:24],opcode  [23:16], i(binary)  [15:8], j(binary)  [7:0], imm(binary)
# opcode : 01100000 (only 1 conditional branch instruction)
# 6. load
# Assembly format: load, mem[i], rd[k]
# machine code: [31:24],opcode  [23:16], i(binary)  [15:8], 00000000  [7:0], k(binary)
# opcode : 10000000 (only 1 load instruction)
# 7. store 
# Assembly format: store, rs1[i], mem[k]
# machine code: [31:24],opcode  [23:16], i(binary)  [15:8], k(binary)  [7:0], 00000000
# 8. store immediate value
# Assembly format: store, imm, mem[k]
# machine code: [31:24],opcode  [23:16], imm(binary)  [15:8], k(binary)  [7:0], 00000000
# opcode : 10010001
operation_list = ['add','sub','and','or','xor','sll','srl']
instruction_type_list = ['TWO_REGS','REG_MEM','REG_IMM','UNCOND_BRANCH','COND_BRANCH','LOAD','STORE']

# micro_code_addr_dict = {}
# micro_code_len_dict = {}
def construct_micro_code_addr_list():
    instruction_set_dict = {
        "add": "00000001",
        "sub": "00000010",
        "and": "00000011",
        "or": "00000100",
        "xor": "00000101",
        "sll": "00000110",
        "srl": "00000111",
        "addi": "00100000",
        "slti": "00100001",
        "andi": "00100010",
        "ori": "00100011",
        "xori": "00100100",
        "slli": "00100101",
        "srli": "00100110",
        "jal": "01000000",
        "beq": "01100000",
        "bne": "01100001",
        "blt": "01100010",
        "bltu": "01100011",
        "load": "10000000",
        "store": "10000001"
    }
    micro_code_addr_list = [None]*500
    micro_code_list = [None] * 500
    micro_code_addr_dict = [None] * 500
    opcode_list = [None] * 500
    comments_list = [None] * 500
    micro_code_len_dict = [None] * 500
    curr_addr = 0
    i_micro_code_group = 0
    for instruction_type in instruction_type_list:
        if instruction_type == 'TWO_REGS':    
            for operation in operation_list:
                micro_code = '16\'b'+instruction_set_dict[operation][4:8]+'0000'+'1100'+'0001'
                opcode = '8\'b000'+'00'+instruction_set_dict[operation][5:8]
                micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
                opcode_list [i_micro_code_group] = opcode
                micro_code_len_dict [i_micro_code_group] = '3\'b000'
                micro_code_list [i_micro_code_group] = [micro_code]
                comments_list [i_micro_code_group] = [operation+' rd, rs1, rs2']
                i_micro_code_group += 1
                curr_addr += 1
        elif instruction_type == 'REG_MEM':
            for operation in operation_list:
                micro_code = '16\'b'+instruction_set_dict[operation][4:8]+'0000'+'1100'+'0001'
                # operand 1 in memory, operand 2 in register file
                micro_code_1 = '20\'b0010'+'0000'+'1000'+'0001'+'0000'
                micro_code_2 = '20\'b0000'+'0000'+'0000'+'0000'+'1000'
                micro_code_3 = '20\'b0001'+'0'+instruction_set_dict[operation][5:8]+'0010'+'0100'+'0001'
                opcode = '8\'b000'+'10'+instruction_set_dict[operation][5:8]
                micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
                opcode_list [i_micro_code_group] = opcode
                micro_code_len_dict [i_micro_code_group] = '3\'b010'
                micro_code_list [i_micro_code_group] = [micro_code_1, micro_code_2, micro_code_3]
                comments_list [i_micro_code_group] = [operation+' rd, [mem1], rs2']
                i_micro_code_group += 1
                curr_addr += 3
                
                # operand 1 in register file, operand 2 in memory
                micro_code_1 = '20\'b0010' + '0000' + '0100' + '0001' + '0000'
                micro_code_2 = '20\'b0000' + '0000' + '0000' + '0000' + '1000'
                micro_code_3 = '20\'b0001' + '0'+instruction_set_dict[operation][5:8]+'0001'+'1000'+'0001'
                opcode = '8\'b000'+'01'+instruction_set_dict[operation][5:8]
                micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
                opcode_list [i_micro_code_group] = opcode
                micro_code_len_dict [i_micro_code_group] = '3\'b010'
                micro_code_list [i_micro_code_group] = [micro_code_1, micro_code_2, micro_code_3]
                comments_list [i_micro_code_group] = [operation+' rd, rs1, [mem2]']
                i_micro_code_group += 1
                curr_addr += 3      
        elif instruction_type == 'REG_IMM':
             # operand 1 in register file, operand 2 is an immediate value
             for operation in operation_list:
                micro_code = '21\'b' + '1' + '0000' + instruction_set_dict[operation][4:8] + '0000' + '1000' + '0001'
                opcode = '8\'b001'+'00'+instruction_set_dict[operation][5:8]
                micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
                opcode_list [i_micro_code_group] = opcode
                micro_code_len_dict [i_micro_code_group] = '3\'b000'
                micro_code_list [i_micro_code_group] = [micro_code]
                comments_list [i_micro_code_group] = [operation+' rd, rs1, imm']
                i_micro_code_group += 1
                curr_addr += 1    
        elif instruction_type == 'UNCOND_BRANCH':
            micro_code = '16\'b0000000000000000'
            opcode = '8\'b010'+'00'+'000'
            micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
            opcode_list [i_micro_code_group] = opcode
            micro_code_len_dict [i_micro_code_group] = '3\'b000'
            micro_code_list [i_micro_code_group] = [micro_code]
            comments_list [i_micro_code_group] = ['jump imm']
            i_micro_code_group += 1
            curr_addr += 1
        elif instruction_type == 'COND_BRANCH':
            micro_code = '16\'b1100000011000000'
            opcode = '8\'b'+'01100000'
            micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
            opcode_list [i_micro_code_group] = opcode
            micro_code_len_dict [i_micro_code_group] = '3\'b000'
            micro_code_list [i_micro_code_group] = [micro_code]
            comments_list [i_micro_code_group] = ['beq rs1, rs2, imm']
            i_micro_code_group += 1
            curr_addr += 1
        elif instruction_type == 'LOAD':
            micro_code_1 = '20\'b0010'+'0000'+'1000'+'0001'+'0000'
            micro_code_2 = '20\'b0000'+'0000'+'1000'
            micro_code_3 = '20\'b0001'+'0000'+'0010'+'0000'+'0001'
            opcode = '8\'b1000'+'0000'
            micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
            opcode_list [i_micro_code_group] = opcode
            micro_code_len_dict [i_micro_code_group] = '3\'b010'
            micro_code_list [i_micro_code_group] = [micro_code_1, micro_code_2, micro_code_3]
            comments_list [i_micro_code_group] = ['load rd, [mem1]']
            i_micro_code_group += 1
            curr_addr += 3
            
            # micro_code_1 = '20\'b0010'+'0000'+'1000'+'0001'+'0000'
            # micro_code_2 = '20\'b0000'+'0000'+'1000'
            # micro_code_4 = '24\'b1000_0000_0000_0000_0000_0000'
            # micro_code_5 = '24\'b1100_0000_0000_0000_0000_0000'
            # micro_code_3 = '20\'b0001'+'0000'+'0010'+'0000'+'0001'
            # opcode = '8\'b1000'+'0000'
            # micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
            # opcode_list [i_micro_code_group] = opcode
            # micro_code_len_dict [i_micro_code_group] = '3\'b100'
            # micro_code_list [i_micro_code_group] = [micro_code_1, micro_code_2, micro_code_3, micro_code_4, micro_code_5]
            # comments_list [i_micro_code_group] = ['load rd, [mem1]']
            # i_micro_code_group += 1
            # curr_addr += 5
            
            
        elif instruction_type == 'STORE':
            micro_code_1 = '16\'b0000_0100_1001_0100'
            micro_code_2 = '16\'b0000_0000_0000_0010'
            opcode = '8\'b10000001'
            micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
            opcode_list [i_micro_code_group] = opcode
            micro_code_len_dict [i_micro_code_group] = '3\'b001'
            micro_code_list [i_micro_code_group] = [micro_code_1, micro_code_2]
            comments_list [i_micro_code_group] = ['store [mem1], rs1']
            i_micro_code_group += 1
            curr_addr += 2
            
            micro_code_1 = '22\'b10_0000_0000_0100_0001_0100'
            micro_code_2 = '16\'b0000_0000_0000_0010'
            opcode = '8\'b10010001'
            micro_code_addr_list [i_micro_code_group] = '8\'b'+int_to_8bit_binary(curr_addr)
            opcode_list [i_micro_code_group] = opcode
            micro_code_len_dict [i_micro_code_group] = '3\'b001'
            micro_code_list [i_micro_code_group] = [micro_code_1, micro_code_2]
            comments_list [i_micro_code_group] = ['store [mem1], imm']
            i_micro_code_group += 1
            curr_addr += 2
    
    micro_code_addr_list[i_micro_code_group] = '8\'b'+int_to_8bit_binary(255)
    micro_code_len_dict [i_micro_code_group] = '3\'b000'
    micro_code_list [i_micro_code_group] = ['16\'b0000000000000000']
    comments_list [i_micro_code_group] = ['NO-OP(Used when flushing pipeline)']
    opcode_list[i_micro_code_group]= '8\'b11111111'
    i_micro_code_group += 1
    return micro_code_addr_list, opcode_list, micro_code_len_dict, micro_code_list, comments_list, i_micro_code_group