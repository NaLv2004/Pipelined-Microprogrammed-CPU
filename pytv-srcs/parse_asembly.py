def parse_operand(operand):
    operand = operand.strip()
    if operand.startswith('rs[') or operand.startswith('rd['):
        num = operand.split('[')[1].split(']')[0]
        return ('reg', int(num))
    elif operand.startswith('mem['):
        num = operand.split('[')[1].split(']')[0]
        return ('mem', int(num))
    else:
        try:
            return ('imm', int(operand))
        except ValueError:
            raise ValueError(f"Invalid operand: {operand}")

def format_machine_code(bin_str):
    bin_str = bin_str.ljust(32, '0')[:32]
    parts = [bin_str[i*8:(i+1)*8] for i in range(4)]
    return '_'.join(parts)

op_func_code = {
    'add': '001',
    'sub': '010',
    'and': '011',
    'or': '100',
    'xor': '101',
    'sll': '110',
    'srl': '111'
}

def assemble(assembly):
    machine_codes = []
    for instr in assembly:
        parts = [p.strip() for p in instr.split(',')]
        if not parts:
            continue
        op = parts[0]
        operands = parts[1:]
        parsed_operands = [parse_operand(o) for o in operands]
        
        # Determine instruction type
        if op in op_func_code:
            if len(parsed_operands) == 3:
                src1_type, src1_val = parsed_operands[0]
                src2_type, src2_val = parsed_operands[1]
                dest_type, dest_val = parsed_operands[2]
                if dest_type != 'reg':
                    raise ValueError(f"Destination must be a register in instruction: {instr}")
                
                # Check for type 3 (immediate)
                if src2_type == 'imm':
                    func = op_func_code[op]
                    opcode = '00100' + func
                    opcode_bin = opcode.ljust(8, '0')[:8]
                    i = src1_val
                    imm = src2_val
                    k = dest_val
                    i_bin = format(i, '08b')
                    imm_bin = format(imm & 0xff, '08b')
                    k_bin = format(k, '08b')
                    machine = opcode_bin + i_bin + imm_bin + k_bin
                    machine_codes.append(format_machine_code(machine))
                else:
                    # Check for type 1 or type 2
                    if src1_type == 'reg' and src2_type == 'reg':
                        func = op_func_code[op]
                        opcode = '00000' + func
                        opcode_bin = opcode.ljust(8, '0')[:8]
                        i = src1_val
                        j = src2_val
                        k = dest_val
                        i_bin = format(i, '08b')
                        j_bin = format(j, '08b')
                        k_bin = format(k, '08b')
                        machine = opcode_bin + i_bin + j_bin + k_bin
                        machine_codes.append(format_machine_code(machine))
                    else:
                        # Type 2.1 or 2.2 based on operand types order
                        if (src1_type, src2_type) == ('mem', 'reg'):
                            func = op_func_code[op]
                            opcode = '00010' + func
                            opcode_bin = opcode.ljust(8, '0')[:8]
                            i = src1_val
                            j = src2_val
                            k = dest_val
                        elif (src1_type, src2_type) == ('reg', 'mem'):
                            func = op_func_code[op]
                            opcode = '00001' + func
                            opcode_bin = opcode.ljust(8, '0')[:8]
                            i = src1_val
                            j = src2_val
                            k = dest_val
                        else:
                            raise ValueError(f"Invalid operands for instruction: {instr}")
                        i_bin = format(i, '08b')
                        j_bin = format(j, '08b')
                        k_bin = format(k, '08b')
                        machine = opcode_bin + i_bin + j_bin + k_bin
                        machine_codes.append(format_machine_code(machine))
            else:
                raise ValueError(f"Invalid operand count for {op}: {instr}")
        elif op == 'jump':
            if len(parsed_operands) != 1:
                raise ValueError(f"Jump instruction format error: {instr}")
            imm_type, imm_val = parsed_operands[0]
            if imm_type != 'imm':
                raise ValueError(f"Jump operand must be immediate: {instr}")
            opcode_bin = '01000000'
            imm_bin = format(imm_val & 0xff, '08b')
            machine = opcode_bin + imm_bin + '0000000000000000'
            machine_codes.append(format_machine_code(machine))
        elif op == 'beq':
            if len(parsed_operands) != 3:
                raise ValueError(f"beq instruction format error: {instr}")
            rs1_type, rs1_val = parsed_operands[0]
            rs2_type, rs2_val = parsed_operands[1]
            imm_type, imm_val = parsed_operands[2]
            if rs1_type != 'reg' or rs2_type != 'reg' or imm_type != 'imm':
                raise ValueError(f"Invalid operands for beq: {instr}")
            opcode_bin = '01100000'
            rs1_bin = format(rs1_val, '08b')
            rs2_bin = format(rs2_val, '08b')
            imm_bin = format(imm_val & 0xff, '08b')
            machine = opcode_bin + rs1_bin + rs2_bin + imm_bin
            machine_codes.append(format_machine_code(machine))
        elif op == 'load':
            if len(parsed_operands) != 2:
                raise ValueError(f"load instruction format error: {instr}")
            mem_type, mem_val = parsed_operands[0]
            rd_type, rd_val = parsed_operands[1]
            if mem_type != 'mem' or rd_type != 'reg':
                raise ValueError(f"Invalid operands for load: {instr}")
            opcode_bin = '10000000'
            mem_bin = format(mem_val, '08b')
            rd_bin = format(rd_val, '08b')
            machine = opcode_bin + mem_bin + '00000000' + rd_bin
            machine_codes.append(format_machine_code(machine))
        elif op == 'store':
            if len(parsed_operands) != 2:
                raise ValueError(f"store instruction format error: {instr}")
            rs_type, rs_val = parsed_operands[0]
            mem_type, mem_val = parsed_operands[1]
            if rs_type != 'reg' or mem_type != 'mem':
                raise ValueError(f"Invalid operands for store: {instr}")
            opcode_bin = '10000001'
            rs_bin = format(rs_val, '08b')
            mem_bin = format(mem_val, '08b')
            machine = opcode_bin + rs_bin + mem_bin + '00000000'
            machine_codes.append(format_machine_code(machine))
        else:
            raise ValueError(f"Unknown operation: {op}")
    return machine_codes

# 示例测试
if __name__ == "__main__":
    input_assembly = ['add, rs[1], rs[2], rd[3]']
    output = assemble(input_assembly)
    print(output)