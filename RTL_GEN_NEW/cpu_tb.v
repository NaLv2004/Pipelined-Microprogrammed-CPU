// === Contents from: ALU0000000001.v ===
 module ALU0000000001 (
     input  clk,
     input  [15:0] alu_regfile_in_1,
     input  [15:0] alu_regfile_in_2,
     input  [15:0] alu_memory_in,
     output [15:0] alu_result,
     output [7:0] alu_regfile_address_out_1,
     output [7:0] alu_regfile_address_out_2,
     output [7:0] alu_memory_address_out,
     output alu_memory_write_en_out,
     output [7:0] alu_regfile_address_out,
     output alu_regfile_write_en_out,
     input  [112:0] cu_alu_interface,
     output [18:0] alu_fetch_interface
     );
 wire [31:0] micro_code;
 assign micro_code = cu_alu_interface[31:0];
 wire [31:0] instruction;
 assign instruction = cu_alu_interface[95:64];
 wire [7:0] instr_address_not_taken_cu_alu;
 assign instr_address_not_taken_cu_alu = cu_alu_interface[103:96];
 wire [0:0] branch_prediction_result_cu_alu;
 assign branch_prediction_result_cu_alu = cu_alu_interface[112:112];
 wire [7:0] branch_instr_address_cu_alu;
 assign branch_instr_address_cu_alu = cu_alu_interface[111:104];
 // assign inner wires to alu_fetch_interface ports (output)
 wire [0:0] flush_pipeline_out;
 assign alu_fetch_interface[0:0] = flush_pipeline_out;
 wire [7:0] instr_address_not_taken_alu_fe;
 assign alu_fetch_interface[16:9] = instr_address_not_taken_alu_fe;
 wire [7:0] branch_instr_address_alu_fe;
 assign alu_fetch_interface[8:1] = branch_instr_address_alu_fe;
 wire [0:0] is_conditional_branch_alu_fe;
 assign alu_fetch_interface[17:17] = is_conditional_branch_alu_fe;
 wire [0:0] branch_taken_alu_fe;
 assign alu_fetch_interface[18:18] = branch_taken_alu_fe;
 wire clk;
 wire [15:0] alu_result;
 wire [15:0] alu_regfile_in_1;
 wire [15:0] alu_regfile_in_2;
 wire [7:0] alu_regfile_address_out_1;
 wire [7:0] alu_regfile_address_out_2;
 wire [15:0] alu_operand_1;
 wire [15:0] alu_operand_2;
 wire [15:0] alu_add_result;
 wire [15:0] alu_sub_result;
 wire [15:0] alu_and_result;
 wire [15:0] alu_or_result;
 wire [15:0] alu_xor_result;
 wire judge_equal_result;
 reg [15:0] alu_result_reg;
 reg [31:0] instruction_pipeline;
 wire [31:0] instruction_choosed;
 assign instruction_choosed = (micro_code[16:16])? instruction_pipeline :instruction;
 assign alu_regfile_address_out_1 = instruction_choosed[23:16];
 assign alu_regfile_address_out_2 = instruction_choosed[15:8];
 assign alu_memory_address_out = (micro_code[11:11] == 1'b1) ?  instruction_choosed[23:16]:
                                 (micro_code[10:10] == 1'b1) ? instruction_choosed[15:8]: 8'b0000_0000;
 assign alu_operand_1 =  (micro_code[21:21] == 1'b1) ? instruction_choosed[23:16]: // first operand is an immediate value
                        (micro_code[9:9] == 1'b1) ?  alu_memory_in:
                        (micro_code[7:7] == 1'b1) ? alu_regfile_in_1: 16'b0;
 assign alu_operand_2 = (micro_code[20:20] == 1'b1) ? instruction_choosed[15:8]: // second operand is an immediate value
                        (micro_code[8:8] == 1'b1) ?  alu_memory_in:
                        (micro_code[6:6] == 1'b1) ? alu_regfile_in_2:
                        (micro_code[5:5] == 1'b1) ? instruction_choosed[7:0] : 16'b0;
 assign alu_regfile_write_en_out = (micro_code[0:0]==1'b1) ? 1'b1: 1'b0;
 assign alu_regfile_address_out = instruction_choosed[7:0];
 assign alu_memory_write_en_out = (micro_code[1:1]==1'b1) ? 1'b1: 1'b0;
Adder0000000001  u_0000000001_Adder0000000001(.op_1(alu_operand_1), .op_2(alu_operand_2), .result(alu_add_result));
Substractor0000000001  u_0000000001_Substractor0000000001(.op_1(alu_operand_1), .op_2(alu_operand_2), .result(alu_sub_result));
Ander0000000001  u_0000000001_Ander0000000001(.op_1(alu_operand_1), .op_2(alu_operand_2), .result(alu_and_result));
Orer0000000001  u_0000000001_Orer0000000001(.op_1(alu_operand_1), .op_2(alu_operand_2), .result(alu_or_result));
Xorer0000000001  u_0000000001_Xorer0000000001(.op_1(alu_operand_1), .op_2(alu_operand_2), .result(alu_xor_result));
JudgeEqual0000000001  u_0000000001_JudgeEqual0000000001(.op_1(alu_operand_1), .op_2(alu_operand_2), .result(alu_judge_equal_result));
 assign alu_result = (micro_code[15:12] == 4'b0001) ? alu_add_result:
                     (micro_code[15:12] == 4'b0010) ? alu_sub_result:
                     (micro_code[15:12] == 4'b0011) ? alu_xor_result:
                     (micro_code[15:12] == 4'b0100) ? alu_and_result:
                     (micro_code[15:12] == 4'b0101) ? alu_or_result:
                     (micro_code[15:12] == 4'b0000) ? alu_operand_1:
                     (micro_code[15:12] == 4'b1100) ? alu_judge_equal_result:
                     16'b0;
 assign is_conditional_branch_alu_fe = (instruction_choosed[31:28]==4'b0110) ? 1'b1: 1'b0;
 assign flush_pipeline_out = (!(instruction_choosed[31:28]==4'b0110)) ? 1'b0:
                             (alu_result == branch_prediction_result_cu_alu) ? 1'b0: 1'b1;
 assign instr_address_not_taken_alu_fe = instr_address_not_taken_cu_alu;
 assign branch_instr_address_alu_fe = branch_instr_address_cu_alu;
 assign branch_taken_alu_fe = (!(instruction_choosed[31:28]==4'b0110)) ? 1'b0:
                              (alu_result) ? 1'b1: 1'b0;
 // inner registers
 reg [31:0] micro_code_reg;
 always @ (posedge clk)
 begin
     micro_code_reg <= micro_code;
     if (micro_code[17:17])
     begin
         instruction_pipeline <= instruction;
     end
 end
 // behaviour according to micro-code
 always @ (posedge clk)
 begin
     if (micro_code_reg == 16'b0)
     begin
         alu_result_reg <= alu_regfile_in_1 + alu_regfile_in_2;
     end
 end
 endmodule


// === Contents from: Adder0000000001.v ===
 module Adder0000000001 (
     input  [15:0] op_1,
     input  [15:0] op_2,
     output [15:0] result
     );
 wire [15:0] result;
 wire [15:0] op_1;
 wire [15:0] op_2;
 assign result = op_1 + op_2;
 endmodule


// === Contents from: Ander0000000001.v ===
 module Ander0000000001 (
     input  [15:0] op_1,
     input  [15:0] op_2,
     output [15:0] result
     );
 wire [15:0] result;
 wire [15:0] op_1;
 wire [15:0] op_2;
 assign result = op_1 & op_2;
 endmodule


// === Contents from: CPUTop0000000001.v ===
 module CPUTop0000000001 ;
 reg clk;
 reg rst;
 wire [15:0] imem_addr;
 wire [31:0] imem_data;
 wire [7:0] register_file_addr_1;
 wire [7:0] register_file_addr_2;
 wire [15:0] register_data_out_1;
 wire [15:0] register_data_out_2;
 wire [31:0] micro_code;
 wire [7:0] micro_code_addr;
 wire [31:0] micro_code_speculative_fetch;  // REASSIGN!
 wire [7:0] micro_code_addr_speculative_fetch;  // REASSIGN!
 wire [15:0] alu_result;
 wire [15:0] data_memory_alu;
 wire [7:0] address_memory_alu;
 wire [0:0] write_en_memory;
 wire [0:0] write_en_regfile;
 wire [7:0] register_file_addr_dest;
 wire [15:0] mem_regfile_test;
 wire [15:0] mem_external_test;
 wire [15:0] mem_regfile_test1;
 wire [15:0] mem_external_test1;
 wire [0:0] flush_pipeline; // flush pipeline when branch prediction fails
 wire dec_ready;
 wire exec_ready; // connects CU and Fetch
 // fe-de; de-cu; cu-alu; alu-fe interfaces
 wire [49:0] fetch_idecode_interface;
 wire [91:0] idecode_cu_interface;
 wire [112:0] cu_alu_interface;
 wire [18:0] alu_fetch_interface;

 assign mem_external_test1 = u_0000000001_RegisterFile0000000001.mem[1];
Fetch0000000001  u_0000000001_Fetch0000000001(.clk(clk), .rst(rst), .imem_addr(imem_addr), .imem_data(imem_data), .dec_ready(dec_ready), .exec_ready(exec_ready), .flush_pipeline(flush_pipeline), .fetch_idecode_interface(fetch_idecode_interface), .alu_fetch_interface(alu_fetch_interface));
InstrMem0000000001  u_0000000001_InstrMem0000000001(.addr(imem_addr), .data_out(imem_data));
Decode0000000001  u_0000000001_Decode0000000001(.clk(clk), .rst(rst), .dec_ready(dec_ready), .flush_pipeline(flush_pipeline), .fetch_idecode_interface(fetch_idecode_interface), .idecode_cu_interface(idecode_cu_interface));
CU0000000001  u_0000000001_CU0000000001(.clk(clk), .rst(rst), .micro_code_in_normal(micro_code), .micro_code_in_speculative(micro_code_speculative_fetch), .micro_code_addr_out(micro_code_addr), .micro_code_addr_speculative_fetch(micro_code_addr_speculative_fetch), .o_exec_ready_combined(exec_ready), .flush_pipeline(flush_pipeline), .idecode_cu_interface(idecode_cu_interface), .cu_alu_interface(cu_alu_interface));
RegisterFile0000000001  u_0000000001_RegisterFile0000000001(.clk(clk), .reg_addr_1(register_file_addr_1), .reg_addr_2(register_file_addr_2), .data_out_1(register_data_out_1), .data_out_2(register_data_out_2), .write_en(write_en_regfile), .reg_addr_in(register_file_addr_dest), .data_in(alu_result), .mem_test(mem_regfile_test));
MicroInstrMem0000000001  u_0000000001_MicroInstrMem0000000001(.micro_code_addr_in(micro_code_addr), .micro_code_data_out(micro_code), .micro_code_addr_speculative_fetch_in(micro_code_addr_speculative_fetch), .micro_code_data_speculative_fetch_out(micro_code_speculative_fetch));
ExternalMem0000000001  u_0000000001_ExternalMem0000000001(.clk(clk), .micro_code(micro_code), .addr(address_memory_alu), .data_in(alu_result), .data_out(data_memory_alu), .data_test(mem_external_test));
ALU0000000001  u_0000000001_ALU0000000001(.clk(clk), .alu_regfile_in_1(register_data_out_1), .alu_regfile_in_2(register_data_out_2), .alu_memory_in(data_memory_alu), .alu_result(alu_result), .alu_regfile_address_out_1(register_file_addr_1), .alu_regfile_address_out_2(register_file_addr_2), .alu_memory_address_out(address_memory_alu), .alu_memory_write_en_out(write_en_memory), .alu_regfile_write_en_out(write_en_regfile), .alu_regfile_address_out(register_file_addr_dest), .cu_alu_interface(cu_alu_interface), .alu_fetch_interface(alu_fetch_interface));
 always #5 clk = ~clk;
 initial begin
   clk = 0;
   rst = 1;
   #10 rst = 0;
 end
 initial begin
 u_0000000001_InstrMem0000000001.mem[0] = 32'b1000_0000_0000_1000_0000_0000_0000_0010;
 u_0000000001_InstrMem0000000001.mem[1] = 32'b0000_0001_0000_0000_0000_0001_0000_0000;
 u_0000000001_InstrMem0000000001.mem[2] = 32'b0000_0010_0000_0010_0000_0000_0000_0000;
 u_0000000001_InstrMem0000000001.mem[3] = 32'b0000_0001_0000_1000_0000_0000_0000_0001;
 u_0000000001_InstrMem0000000001.mem[4] = 32'b0100_0000_0001_0000_0000_0000_0000_0000;
 u_0000000001_InstrMem0000000001.mem[5] = 32'b0000_0001_0000_0000_0000_0010_0000_0000;
 u_0000000001_InstrMem0000000001.mem[6] = 32'b0000_0001_0000_0000_0000_0001_0000_0000;
 u_0000000001_InstrMem0000000001.mem[7] = 32'b0000_0001_0000_0000_0000_0010_0000_0000;
 u_0000000001_InstrMem0000000001.mem[8] = 32'b1000_0001_0000_0000_0000_0000_0000_0000;
 u_0000000001_InstrMem0000000001.mem[9] = 32'b0110_0000_0000_0011_0000_0011_0000_0100;
 u_0000000001_InstrMem0000000001.mem[10] = 32'b0000_0001_0000_0000_0000_0001_0000_0000;
 u_0000000001_InstrMem0000000001.mem[11] = 32'b0000_0001_0000_0000_0000_0010_0000_0000;
 u_0000000001_InstrMem0000000001.mem[12] = 32'b0000_0001_0000_0000_0000_0001_0000_0000;
 u_0000000001_InstrMem0000000001.mem[13] = 32'b0000_0001_0000_0000_0000_0010_0000_0000;
 // ['add rd, rs1, rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[0] = 16'b0001000011000001;
 // ['sub rd, rs1, rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[1] = 16'b0010000011000001;
 // ['and rd, rs1, rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[2] = 16'b0011000011000001;
 // ['or rd, rs1, rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[3] = 16'b0100000011000001;
 // ['xor rd, rs1, rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[4] = 16'b0101000011000001;
 // ['sll rd, rs1, rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[5] = 16'b0110000011000001;
 // ['srl rd, rs1, rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[6] = 16'b0111000011000001;
 // ['add rd, [mem1], rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[7] = 20'b00100000100000010000;
 u_0000000001_MicroInstrMem0000000001.mem[8] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[9] = 20'b00010001001001000001;
 // ['add rd, rs1, [mem2]'];
 u_0000000001_MicroInstrMem0000000001.mem[10] = 20'b00100000010000010000;
 u_0000000001_MicroInstrMem0000000001.mem[11] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[12] = 20'b00010001000110000001;
 // ['sub rd, [mem1], rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[13] = 20'b00100000100000010000;
 u_0000000001_MicroInstrMem0000000001.mem[14] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[15] = 20'b00010010001001000001;
 // ['sub rd, rs1, [mem2]'];
 u_0000000001_MicroInstrMem0000000001.mem[16] = 20'b00100000010000010000;
 u_0000000001_MicroInstrMem0000000001.mem[17] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[18] = 20'b00010010000110000001;
 // ['and rd, [mem1], rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[19] = 20'b00100000100000010000;
 u_0000000001_MicroInstrMem0000000001.mem[20] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[21] = 20'b00010011001001000001;
 // ['and rd, rs1, [mem2]'];
 u_0000000001_MicroInstrMem0000000001.mem[22] = 20'b00100000010000010000;
 u_0000000001_MicroInstrMem0000000001.mem[23] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[24] = 20'b00010011000110000001;
 // ['or rd, [mem1], rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[25] = 20'b00100000100000010000;
 u_0000000001_MicroInstrMem0000000001.mem[26] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[27] = 20'b00010100001001000001;
 // ['or rd, rs1, [mem2]'];
 u_0000000001_MicroInstrMem0000000001.mem[28] = 20'b00100000010000010000;
 u_0000000001_MicroInstrMem0000000001.mem[29] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[30] = 20'b00010100000110000001;
 // ['xor rd, [mem1], rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[31] = 20'b00100000100000010000;
 u_0000000001_MicroInstrMem0000000001.mem[32] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[33] = 20'b00010101001001000001;
 // ['xor rd, rs1, [mem2]'];
 u_0000000001_MicroInstrMem0000000001.mem[34] = 20'b00100000010000010000;
 u_0000000001_MicroInstrMem0000000001.mem[35] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[36] = 20'b00010101000110000001;
 // ['sll rd, [mem1], rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[37] = 20'b00100000100000010000;
 u_0000000001_MicroInstrMem0000000001.mem[38] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[39] = 20'b00010110001001000001;
 // ['sll rd, rs1, [mem2]'];
 u_0000000001_MicroInstrMem0000000001.mem[40] = 20'b00100000010000010000;
 u_0000000001_MicroInstrMem0000000001.mem[41] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[42] = 20'b00010110000110000001;
 // ['srl rd, [mem1], rs2'];
 u_0000000001_MicroInstrMem0000000001.mem[43] = 20'b00100000100000010000;
 u_0000000001_MicroInstrMem0000000001.mem[44] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[45] = 20'b00010111001001000001;
 // ['srl rd, rs1, [mem2]'];
 u_0000000001_MicroInstrMem0000000001.mem[46] = 20'b00100000010000010000;
 u_0000000001_MicroInstrMem0000000001.mem[47] = 20'b00000000000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[48] = 20'b00010111000110000001;
 // ['add rd, rs1, imm'];
 u_0000000001_MicroInstrMem0000000001.mem[49] = 21'b100000001000010000001;
 // ['sub rd, rs1, imm'];
 u_0000000001_MicroInstrMem0000000001.mem[50] = 21'b100000010000010000001;
 // ['and rd, rs1, imm'];
 u_0000000001_MicroInstrMem0000000001.mem[51] = 21'b100000011000010000001;
 // ['or rd, rs1, imm'];
 u_0000000001_MicroInstrMem0000000001.mem[52] = 21'b100000100000010000001;
 // ['xor rd, rs1, imm'];
 u_0000000001_MicroInstrMem0000000001.mem[53] = 21'b100000101000010000001;
 // ['sll rd, rs1, imm'];
 u_0000000001_MicroInstrMem0000000001.mem[54] = 21'b100000110000010000001;
 // ['srl rd, rs1, imm'];
 u_0000000001_MicroInstrMem0000000001.mem[55] = 21'b100000111000010000001;
 // ['jump imm'];
 u_0000000001_MicroInstrMem0000000001.mem[56] = 16'b0000000000000000;
 // ['beq rs1, rs2, imm'];
 u_0000000001_MicroInstrMem0000000001.mem[57] = 16'b1100000011000000;
 // ['load rd, [mem1]'];
 u_0000000001_MicroInstrMem0000000001.mem[58] = 20'b00100000100000010000;
 u_0000000001_MicroInstrMem0000000001.mem[59] = 20'b000000001000;
 u_0000000001_MicroInstrMem0000000001.mem[60] = 20'b00010000001000000001;
 // ['store [mem1], rs1'];
 u_0000000001_MicroInstrMem0000000001.mem[61] = 16'b0;
 u_0000000001_MicroInstrMem0000000001.mem[62] = 16'b0;
 // ['store [mem1], imm'];
 u_0000000001_MicroInstrMem0000000001.mem[63] = 22'b10_0000_0000_0100_0001_0100;
 u_0000000001_MicroInstrMem0000000001.mem[64] = 16'b0000_0000_0000_0010;
 // ['NO-OP(Used when flushing pipeline)'];
 u_0000000001_MicroInstrMem0000000001.mem[65] = 16'b0000000000000000;
 u_0000000001_MicroInstrMem0000000001.mem[255] = 16'b0000_0000;
 u_0000000001_ExternalMem0000000001.mem[0] = 16'b0000_0001;
 u_0000000001_ExternalMem0000000001.mem[1] = 16'b0001_0010;
 u_0000000001_ExternalMem0000000001.mem[2] = 16'b0010_0000;
 u_0000000001_ExternalMem0000000001.mem[3] = 16'b0000_0100;
 u_0000000001_ExternalMem0000000001.mem[4] = 16'b0000_0101;
 u_0000000001_ExternalMem0000000001.mem[5] = 16'b0000_0110;
 u_0000000001_ExternalMem0000000001.mem[6] = 16'b0000_0111;
 u_0000000001_ExternalMem0000000001.mem[7] = 16'b0000_1000;
 u_0000000001_ExternalMem0000000001.mem[8] = 16'b0000_1111;
 u_0000000001_ExternalMem0000000001.mem[9] = 16'b0000_1010;
 u_0000000001_ExternalMem0000000001.mem[10] = 16'b0000_1011;
 u_0000000001_RegisterFile0000000001.mem[0] = 16'b0000_0000_0000_0001;
 u_0000000001_RegisterFile0000000001.mem[1] = 16'b0000_0000_0000_0010;
 u_0000000001_RegisterFile0000000001.mem[2] = 16'b0000_0000_0000_0011;
 u_0000000001_RegisterFile0000000001.mem[3] = 16'b0000_0000_0000_0101;
 u_0000000001_RegisterFile0000000001.mem[4] = 16'b0000_0000_0000_0110;
 u_0000000001_RegisterFile0000000001.mem[5] = 16'b0000_0000_0000_0111;
 u_0000000001_RegisterFile0000000001.mem[6] = 16'b0000_0000_0000_1000;
 u_0000000001_RegisterFile0000000001.mem[7] = 16'b0000_0000_0000_1001;
 u_0000000001_RegisterFile0000000001.mem[8] = 16'b0000_0000_0000_1010;
 u_0000000001_RegisterFile0000000001.mem[9] = 16'b0000_0000_0000_1011;
 u_0000000001_RegisterFile0000000001.mem[10] = 16'b0000_0000_0000_1100;
 u_0000000001_RegisterFile0000000001.mem[11] = 16'b0000_0000_0000_1101;
 u_0000000001_RegisterFile0000000001.mem[12] = 16'b0000_0000_0000_1110;
 u_0000000001_RegisterFile0000000001.mem[13] = 16'b0000_0000_0000_1111;
 u_0000000001_RegisterFile0000000001.mem[14] = 16'b0000_0000_0001_0000;
 u_0000000001_RegisterFile0000000001.mem[15] = 16'b0000_0000_0001_0001;
 u_0000000001_RegisterFile0000000001.mem[16] = 16'b0000_0000_0001_0010;
 u_0000000001_RegisterFile0000000001.mem[17] = 16'b0000_0000_0001_0011;
 end
 initial begin
     $dumpfile("wave.vcd");
     $dumpvars(0, CPUTop0000000001);
     #2500
     $finish;
 end
 endmodule


// === Contents from: CU0000000001.v ===
 module CU0000000001 (
     input  clk,
     input  rst,
     input  flush_pipeline,
     input  [31:0] micro_code_in_normal,
     input  [31:0] micro_code_in_speculative,
     input  [91:0] idecode_cu_interface,
     output [112:0] cu_alu_interface,
     output o_exec_ready_combined,
     output o_exec_ready_normal,
     output [7:0] micro_code_addr_out,
     output [7:0] micro_code_addr_speculative_fetch
     );
 wire clk;
 wire rst;
 wire flush_pipeline;
 wire o_exec_ready_combined;
 wire o_exec_ready_normal;
 wire [31:0] micro_code_in_normal;
 wire [31:0] micro_code_in_speculative;
 wire [91:0] idecode_cu_interface;
 wire [112:0] cu_alu_interface;
 // assign inner wires to de_cu_interface ports (input)
 wire [31:0] instr_cu_in;
 assign instr_cu_in = idecode_cu_interface[31:0];
 wire [7:0] micro_code_addr_in;
 assign micro_code_addr_in = idecode_cu_interface[39:32];
 wire [2:0] micro_code_cnt_in;
 assign micro_code_cnt_in = idecode_cu_interface[42:40];
 wire [7:0] instr_address_not_taken_de_cu;
 assign instr_address_not_taken_de_cu = idecode_cu_interface[82:75];
 wire [0:0] branch_prediction_result_de_cu;
 assign branch_prediction_result_de_cu = idecode_cu_interface[91:91];
 wire [7:0] branch_instr_address_de_cu;
 assign branch_instr_address_de_cu = idecode_cu_interface[90:83];
 // assign inner wires to cu_alu_interface ports (output)
 wire [31:0] micro_code_out;
 assign cu_alu_interface[31:0] = micro_code_out;
 wire [31:0] micro_code_speculative_fetch;
 assign cu_alu_interface[63:32] = micro_code_speculative_fetch;
 wire [31:0] instr_cu_out;
 assign cu_alu_interface[95:64] = instr_cu_out;
 wire [7:0] instr_address_not_taken_cu_alu;
 assign cu_alu_interface[103:96] = instr_address_not_taken_cu_alu;
 wire [7:0] branch_instr_address_cu_alu;
 assign cu_alu_interface[111:104] = branch_instr_address_cu_alu;
 wire [0:0] branch_prediction_result_cu_alu;
 assign cu_alu_interface[112:112] = branch_prediction_result_cu_alu;
 wire [31:0]  instruction_normal;
 reg [7:0] micro_code_addr_reg;
 reg [2:0] micro_code_cnt_reg;
 reg [7:0] micro_code_addr_speculative_fetch_reg;
 reg [31:0] micro_code_speculative_fetch_reg;
 reg [31:0] cu_instruction_reg;
 reg [7:0] instr_address_not_taken_reg;
 reg [7:0] branch_instr_address_reg;
 reg branch_prediction_result_reg;
 reg exec_combined_reg;
 reg [31:0] instruction_normal_reg;
 assign instr_address_not_taken_cu_alu = instr_address_not_taken_reg;
 assign micro_code_addr_out = micro_code_addr_reg;
 assign micro_code_addr_speculative_fetch = micro_code_addr_speculative_fetch_reg;
 assign branch_instr_address_cu_alu = branch_instr_address_reg;
 assign branch_prediction_result_cu_alu = branch_prediction_result_reg;
 assign instr_cu_out = cu_instruction_reg;
 assign instruction_normal = instruction_normal_reg;
 assign o_exec_ready_normal = (micro_code_cnt_reg==3'b0) ? 1'b1 : 1'b0;
JudgeNotConflictSpeculativeFetch0000000001  u_0000000001_JudgeNotConflictSpeculativeFetch0000000001(.micro_code_normal(micro_code_in_normal), .micro_code_speculative(micro_code_in_speculative), .instruction_normal(instruction_normal), .instruction_speculative(instr_cu_out), .is_micro_code_not_conflict(o_exec_ready_speculative_fetch), .micro_instruction_cnt_speculative(micro_code_cnt_in));
 assign o_exec_ready_combined = o_exec_ready_normal | o_exec_ready_speculative_fetch;
 // fused micro-code
 assign micro_code_out = (o_exec_ready_speculative_fetch)? (micro_code_in_normal ^ micro_code_in_speculative): micro_code_in_normal;
 // CU is ready to receive new micro-code address when micro-code-reg == 0 (all the micro-codes executed)
 // revised micro-instruction logic
 always @ (posedge clk or negedge rst)
 begin
     exec_combined_reg <= o_exec_ready_combined;
     if (rst || flush_pipeline) begin
         micro_code_cnt_reg <= 3'b0;
         micro_code_addr_reg <= 8'b1111_1111;
         cu_instruction_reg <= 32'b0;
         instruction_normal_reg <= 32'b0;
         instr_address_not_taken_reg <= 8'b0;
         branch_instr_address_reg <= 8'b0;
         branch_prediction_result_reg <= 1'b0;
         micro_code_addr_speculative_fetch_reg <= 8'b1111_1111;
     end
     if ((rst==0) && (!flush_pipeline)) begin    // if no reset signal or pipeline flush
         if (o_exec_ready_combined) begin
            if (micro_code_cnt_reg == 3'b0) begin    // if micro_code_cnt_reg == 0, renew the register (fetch a novel normal instruction)
                instruction_normal_reg <= instr_cu_in;           
                micro_code_cnt_reg <= micro_code_cnt_in;
                micro_code_addr_reg <= micro_code_addr_in;
            end
            else if (micro_code_cnt_reg > 0) begin    
                micro_code_cnt_reg <= micro_code_cnt_reg - 1;
                micro_code_addr_reg <= micro_code_addr_reg + 1;
                micro_code_addr_speculative_fetch_reg <= micro_code_addr_in;
            end
            cu_instruction_reg <= instr_cu_in;
            instr_address_not_taken_reg <= instr_address_not_taken_de_cu;
            branch_instr_address_reg <= branch_instr_address_de_cu;
            branch_prediction_result_reg <= branch_prediction_result_de_cu;
           
         end else begin
            if (micro_code_cnt_reg > 3'b0)
            begin
                micro_code_cnt_reg <= micro_code_cnt_reg-1;
                micro_code_addr_reg <= micro_code_addr_reg+1;
                micro_code_addr_speculative_fetch_reg <= 8'b1111_1111;
            end
         end

     end
 end
//  always @ (posedge clk or negedge rst)
//  begin
//      exec_combined_reg <= o_exec_ready_combined;
//      if (rst || flush_pipeline) begin
//          micro_code_cnt_reg <= 3'b0;
//          micro_code_addr_reg <= 8'b1111_1111;
//          cu_instruction_reg <= 32'b0;
//          instruction_normal_reg <= 32'b0;
//          instr_address_not_taken_reg <= 8'b0;
//          branch_instr_address_reg <= 8'b0;
//          branch_prediction_result_reg <= 1'b0;
//          micro_code_addr_speculative_fetch_reg <= 8'b1111_1111;
//      end
//      if (rst==0) begin
//      if (((micro_code_cnt_reg == 3'b0) || exec_combined_reg) && (!flush_pipeline))  // prev: o_exec_ready_combined
//      begin
//          micro_code_addr_reg <= micro_code_addr_in;
//          // micro_code_cnt_reg <= micro_code_cnt_in;

//          cu_instruction_reg <= instr_cu_in;
//          instr_address_not_taken_reg <= instr_address_not_taken_de_cu;
//          branch_instr_address_reg <= branch_instr_address_de_cu;
//          branch_prediction_result_reg <= branch_prediction_result_de_cu;
//          // micro_code_addr_speculative_fetch_reg <= 8'b1111_1111;
//       end
//       if (micro_code_cnt_reg == 0 && (!flush_pipeline))
//       begin
//          instruction_normal_reg <= instr_cu_in;
//          micro_code_cnt_reg <= micro_code_cnt_in;
//       end
//       if (micro_code_cnt_reg > 0)
//       begin
//          micro_code_cnt_reg <= micro_code_cnt_reg - 1;
//          micro_code_addr_reg <= micro_code_addr_reg + 1;
//          micro_code_addr_speculative_fetch_reg <= micro_code_addr_in;
//       end
//       end
//  end
 endmodule


// === Contents from: Decode0000000001.v ===
 module Decode0000000001 (
     input  clk,
     input  rst,
     input  flush_pipeline,
     input  [49:0] fetch_idecode_interface,
     output [2:0] opcode,
     output [4:0] rs1,
     output [4:0] rs2,
     output [4:0] rd,
     output dec_ready,
     output [91:0] idecode_cu_interface
     );
 wire [0:0] instr_valid;
 assign instr_valid = fetch_idecode_interface[0:0];
 wire [7:0] instr_address_not_taken_fe_de;
 assign instr_address_not_taken_fe_de = fetch_idecode_interface[8:1];
 wire [7:0] branch_instr_address_fe_de;
 assign branch_instr_address_fe_de = fetch_idecode_interface[16:9];
 wire [0:0] branch_prediction_result_fe_de;
 assign branch_prediction_result_fe_de = fetch_idecode_interface[17:17];
 wire [31:0] instr;
 assign instr = fetch_idecode_interface[49:18];
 wire [31:0] instr_out;
 assign idecode_cu_interface[31:0] = instr_out;
 wire [7:0] micro_code_addr_out;
 assign idecode_cu_interface[39:32] = micro_code_addr_out;
 wire [2:0] micro_code_cnt_out;
 assign idecode_cu_interface[42:40] = micro_code_cnt_out;
 wire [31:0] micro_code;
 assign idecode_cu_interface[74:43] = micro_code;
 wire [7:0] instr_address_not_taken_de_cu;
 assign idecode_cu_interface[82:75] = instr_address_not_taken_de_cu;
 wire [7:0] branch_instr_address_de_cu;
 assign idecode_cu_interface[90:83] = branch_instr_address_de_cu;
 wire [0:0] branch_prediction_result_de_cu;
 assign idecode_cu_interface[91:91] = branch_prediction_result_de_cu;
 reg ready_reg;
 reg micro_code_reg;
 reg [7:0] micro_code_addr_reg;
 reg [31:0] instr_out_reg;
 reg [2:0] micro_code_cnt_reg;
 // assign instr_out = instr_out_reg;
 assign instr_out = instr;
 assign dec_ready = ready_reg;
 wire [7:0] micro_code_cnt_in;
 assign opcode = instr[2:0];
 assign rs1 = instr[7:3];
 assign rs2 = instr[12:8];
 assign rd = instr[15:13];
 assign micro_code = micro_code_reg;
 assign instr_address_not_taken_de_cu = instr_address_not_taken_fe_de;
 assign branch_prediction_result_de_cu = branch_prediction_result_fe_de;
 assign branch_instr_address_de_cu = branch_instr_address_fe_de;
 assign micro_code_addr_out =
      (flush_pipeline==1'b1) ? 8'b1111_1111 : // flush pipeline (no operations))   8'b1111_1111;
      (instr[31:24]==8'b00000001) ? 8'b00000000:
      (instr[31:24]==8'b00000010) ? 8'b00000001:
      (instr[31:24]==8'b00000011) ? 8'b00000010:
      (instr[31:24]==8'b00000100) ? 8'b00000011:
      (instr[31:24]==8'b00000101) ? 8'b00000100:
      (instr[31:24]==8'b00000110) ? 8'b00000101:
      (instr[31:24]==8'b00000111) ? 8'b00000110:
      (instr[31:24]==8'b00010001) ? 8'b00000111:
      (instr[31:24]==8'b00001001) ? 8'b00001010:
      (instr[31:24]==8'b00010010) ? 8'b00001101:
      (instr[31:24]==8'b00001010) ? 8'b00010000:
      (instr[31:24]==8'b00010011) ? 8'b00010011:
      (instr[31:24]==8'b00001011) ? 8'b00010110:
      (instr[31:24]==8'b00010100) ? 8'b00011001:
      (instr[31:24]==8'b00001100) ? 8'b00011100:
      (instr[31:24]==8'b00010101) ? 8'b00011111:
      (instr[31:24]==8'b00001101) ? 8'b00100010:
      (instr[31:24]==8'b00010110) ? 8'b00100101:
      (instr[31:24]==8'b00001110) ? 8'b00101000:
      (instr[31:24]==8'b00010111) ? 8'b00101011:
      (instr[31:24]==8'b00001111) ? 8'b00101110:
      (instr[31:24]==8'b00100001) ? 8'b00110001:
      (instr[31:24]==8'b00100010) ? 8'b00110010:
      (instr[31:24]==8'b00100011) ? 8'b00110011:
      (instr[31:24]==8'b00100100) ? 8'b00110100:
      (instr[31:24]==8'b00100101) ? 8'b00110101:
      (instr[31:24]==8'b00100110) ? 8'b00110110:
      (instr[31:24]==8'b00100111) ? 8'b00110111:
      (instr[31:24]==8'b01000000) ? 8'b00111000:
      (instr[31:24]==8'b01100000) ? 8'b00111001:
      (instr[31:24]==8'b10000000) ? 8'b00111010:
      (instr[31:24]==8'b10000001) ? 8'b00111101:
      (instr[31:24]==8'b10010001) ? 8'b00111111:
      (instr[31:24]==8'b11111111) ? 8'b11111111:
      8'b1111_1111;
 //assign micro_code_addr_out = instr[31:24];
 // counter: n of micro codes following this address
 assign micro_code_cnt_out =
      (flush_pipeline==1'b1) ? 3'b000 : // flush pipeline (no operations))   3'b000;
      (instr[31:24]==8'b00000001) ? 3'b000:
      (instr[31:24]==8'b00000010) ? 3'b000:
      (instr[31:24]==8'b00000011) ? 3'b000:
      (instr[31:24]==8'b00000100) ? 3'b000:
      (instr[31:24]==8'b00000101) ? 3'b000:
      (instr[31:24]==8'b00000110) ? 3'b000:
      (instr[31:24]==8'b00000111) ? 3'b000:
      (instr[31:24]==8'b00010001) ? 3'b010:
      (instr[31:24]==8'b00001001) ? 3'b010:
      (instr[31:24]==8'b00010010) ? 3'b010:
      (instr[31:24]==8'b00001010) ? 3'b010:
      (instr[31:24]==8'b00010011) ? 3'b010:
      (instr[31:24]==8'b00001011) ? 3'b010:
      (instr[31:24]==8'b00010100) ? 3'b010:
      (instr[31:24]==8'b00001100) ? 3'b010:
      (instr[31:24]==8'b00010101) ? 3'b010:
      (instr[31:24]==8'b00001101) ? 3'b010:
      (instr[31:24]==8'b00010110) ? 3'b010:
      (instr[31:24]==8'b00001110) ? 3'b010:
      (instr[31:24]==8'b00010111) ? 3'b010:
      (instr[31:24]==8'b00001111) ? 3'b010:
      (instr[31:24]==8'b00100001) ? 3'b000:
      (instr[31:24]==8'b00100010) ? 3'b000:
      (instr[31:24]==8'b00100011) ? 3'b000:
      (instr[31:24]==8'b00100100) ? 3'b000:
      (instr[31:24]==8'b00100101) ? 3'b000:
      (instr[31:24]==8'b00100110) ? 3'b000:
      (instr[31:24]==8'b00100111) ? 3'b000:
      (instr[31:24]==8'b01000000) ? 3'b000:
      (instr[31:24]==8'b01100000) ? 3'b000:
      (instr[31:24]==8'b10000000) ? 3'b100:
      (instr[31:24]==8'b10000001) ? 3'b001:
      (instr[31:24]==8'b10010001) ? 3'b001:
      (instr[31:24]==8'b11111111) ? 3'b000:
      3'b000;
 always @(posedge clk or posedge rst) begin
     if (rst) begin
         ready_reg <= 1'b0;
     end else begin
         ready_reg <= 1'b1;
     end
 end
 always @(posedge clk) begin
     micro_code_reg <= 32'b0;
 end
 endmodule


// === Contents from: ExternalMem0000000001.v ===
 module ExternalMem0000000001 (
     input clk,
     input [31:0] micro_code,
     input [7:0] addr,
     input [15:0] data_in,
     output [15:0] data_out,
     output [15:0] data_test
     );
 reg [15:0] mem [255:0];
 reg [7:0] MAR;
 reg [15:0] MBR;
 wire [15:0] data_out_instant;
 wire [15:0] read_en;
 assign data_out = MBR;
 assign data_test = mem[0];


 always @(posedge clk)
 begin
     case (micro_code[4:4])
         1'b1: MAR <= addr;
     endcase
 end

 always @(posedge clk)
 begin
     case (micro_code[3:3])
         1'b1: MBR <= mem[MAR];
     endcase
     case (micro_code[2:2])
         1'b1: MBR <= data_in;
     endcase
     case (micro_code[1:1])
         1'b1: mem[MAR] <= MBR;
     endcase
 end
 endmodule


// === Contents from: Fetch0000000001.v ===
 module Fetch0000000001 (
     input  clk,
     input  rst,
     input  dec_ready,
     input  exec_ready,
     output flush_pipeline,
     input [31:0] imem_data,
     output [7:0] imem_addr,
     input  [18:0] alu_fetch_interface,
     output [49:0] fetch_idecode_interface
     );
 wire [7:0] branch_instr_address_alu_fe;
 wire is_conditional_branch_alu_fe;
 wire branch_taken_in;
 wire branch_prediction_failed;
 wire [7:0] instr_address_not_taken_alu_fe;
 assign branch_instr_address_alu_fe = alu_fetch_interface[8:1];
 assign is_conditional_branch_alu_fe = alu_fetch_interface[17:17];
 assign branch_taken_in = alu_fetch_interface[18:18];
 assign instr_address_not_taken_alu_fe = alu_fetch_interface[16:9];
 assign branch_prediction_failed = alu_fetch_interface[0:0];
 reg [15:0] pc;
 reg [31:0] instruction_reg;
 reg valid_reg;
 reg [7:0] branch_target_buffer; // target instruction address if the branch is taken
 reg [7:0] pc_delayed;
 reg [0:0] branch_prediction_failed_buffer; // branch prediction failed flag
 wire [7:0] branch_target_address_wire;
 wire branch_taken_one_bit_predict;
 wire branch_prediction_result_in_fe;
 reg branch_prediction_result_reg;
 assign fetch_idecode_interface[8:1] = branch_target_buffer;
 wire [7:0]  curr_instr_address;
 assign curr_instr_address = pc[7:0];
 wire is_conditional_branch;
 wire is_unconditional_branch;
MiniDecode0000000001  u_0000000001_MiniDecode0000000001(.instr(imem_data), .is_unconditional_branch(is_unconditional_branch), .is_conditional_branch(is_conditional_branch));
 wire [15:0] branch_predict;
 assign branch_predict = (is_unconditional_branch)? imem_data[23:16]:
                         (is_conditional_branch && branch_taken_one_bit_predict)? imem_data[7:0]:
                         (pc+16'h2);
 assign branch_target_address_wire = (is_conditional_branch)? imem_data[7:0] : branch_target_buffer;
 assign flush_pipeline = branch_prediction_failed;
 assign fetch_idecode_interface[16:9] = pc_delayed;
 assign fetch_idecode_interface[17:17] = branch_prediction_result_reg;
 assign branch_prediction_result_in_fe = (is_conditional_branch && branch_taken_one_bit_predict)? 1'b1 : 1'b0;
OneBitBranchPredictor0000000001  u_0000000001_OneBitBranchPredictor0000000001(.clk(clk), .rst(rst), .instr_address_fe(curr_instr_address), .instr_address_alu(branch_instr_address_alu_fe), .branch_taken_in(branch_taken_in), .is_conditional_branch_fe(is_conditional_branch), .is_conditional_branch_alu(is_conditional_branch_alu_fe), .branch_taken_out(branch_taken_one_bit_predict));
 always @(posedge clk or posedge rst) begin
     if (rst) begin
         branch_target_buffer <= 8'b0;
         pc_delayed <= 8'b0;
         branch_prediction_result_reg <= 1'b0;
     end else begin
         branch_target_buffer <= branch_target_address_wire;
     end
 end

 always @(posedge clk or posedge rst) begin
     if (rst) begin
         pc <= 16'h0;
     end else if (valid_reg && dec_ready && exec_ready) begin
         pc_delayed <= pc[7:0];
         branch_prediction_result_reg <= branch_prediction_result_in_fe;
         if (branch_prediction_failed) begin
             instruction_reg <= 32'b0;
             // prev:pc <= branch_target_buffer;
             pc <= instr_address_not_taken_alu_fe;
         end else begin
             instruction_reg <= imem_data;
             // prev: pc <= pc + 16'h2;
             pc <= branch_predict;
         end
     end
 end

 always @(posedge clk or posedge rst) begin
     if (rst) begin
         valid_reg <= 1'b0;
         instruction_reg <= 32'b0;
     end else begin
         valid_reg <= 1'b1;
     end
 end

 assign imem_addr = pc;
 assign fetch_idecode_interface[0:0] = valid_reg;
 assign fetch_idecode_interface[49:18] = instruction_reg;
 endmodule


// === Contents from: InstrMem0000000001.v ===
 module InstrMem0000000001 (
     input [7:0] addr,
     output [31:0] data_out
 );
 reg [31:0] mem [255:0];
 assign data_out = mem[addr[7:1]];
 endmodule


// === Contents from: JudgeEqual0000000001.v ===
 module JudgeEqual0000000001 (
     input  [15:0] op_1,
     input  [15:0] op_2,
     output result
     );
 wire result;
 wire [15:0] op_1;
 wire [15:0] op_2;
 assign result = (op_1 == op_2);
 endmodule


// === Contents from: JudgeNotConflictSpeculativeFetch0000000001.v ===
 module JudgeNotConflictSpeculativeFetch0000000001 (
     input [31:0] micro_code_normal,
     input [31:0] micro_code_speculative,
     input [31:0] instruction_normal,
     input [31:0] instruction_speculative,
     input [2:0] micro_instruction_cnt_speculative,
     output is_micro_code_not_conflict
     );
 wire is_micro_code_conflict;
 wire is_micro_code_dependent;
 wire is_micro_code_multi_cycle;
 assign is_micro_code_conflict = (| (micro_code_speculative[31:0] & micro_code_normal[31:0])) ? 1'b1:
                               (| micro_code_normal[11:5]) ? 1'b1 : 1'b0;
 assign is_micro_code_dependent = (instruction_speculative[23:16]==instruction_normal[7:0])|(instruction_speculative[15:8]==instruction_normal[7:0]);
 // assign is_micro_code_multi_cycle = // micro_instruction_cnt_speculative == 2b0 ? 1'b0 : 1'b1;
 assign is_micro_code_not_conflict = ~(is_micro_code_conflict|is_micro_code_dependent);
 endmodule


// === Contents from: MicroInstrMem0000000001.v ===
 module MicroInstrMem0000000001 (
        input [7:0] micro_code_addr_in,
        output [31:0] micro_code_data_out,
        input [7:0] micro_code_addr_speculative_fetch_in,
        output [31:0] micro_code_data_speculative_fetch_out
        );
 reg [31:0] mem [255:0];
 assign micro_code_data_out = mem[micro_code_addr_in];
 assign micro_code_data_speculative_fetch_out = mem[micro_code_addr_speculative_fetch_in];
 endmodule


// === Contents from: MiniDecode0000000001.v ===
 module MiniDecode0000000001 (
     input  [31:0] instr,
     output is_unconditional_branch,
     output is_conditional_branch
 );
 assign is_unconditional_branch = (instr[31:28]==4'b0100) ? 1'b1 : 1'b0;
 assign is_conditional_branch = (instr[31:28]==4'b0110) ? 1'b1 : 1'b0;
 endmodule


// === Contents from: OneBitBranchPredictor0000000001.v ===
 module OneBitBranchPredictor0000000001 (
     input clk,
     input rst,
     input [7:0] instr_address_fe,
     input [7:0] instr_address_alu,
     input branch_taken_in,
     input is_conditional_branch_fe,
     input is_conditional_branch_alu,
     output branch_taken_out,
     output [7:0] mem_one_bit_predictor_test
     );
 wire [7:0] instr_address_fe;
 wire [7:0] instr_address_alu;
 reg [10:0] counters_and_address [7:0];
 assign mem_one_bit_predictor_test[0] = counters_and_address[0][10];
 assign mem_one_bit_predictor_test[1] = counters_and_address[1][10];
 assign mem_one_bit_predictor_test[2] = counters_and_address[2][10];
 assign mem_one_bit_predictor_test[3] = counters_and_address[3][10];
 assign mem_one_bit_predictor_test[4] = counters_and_address[4][10];
 assign mem_one_bit_predictor_test[5] = counters_and_address[5][10];
 assign mem_one_bit_predictor_test[6] = counters_and_address[6][10];
 assign mem_one_bit_predictor_test[7] = counters_and_address[7][10];
 wire [2:0] idx_slot_fe;
 wire  slot_hit_fe;
 wire  slot_not_occupied_fe;
 assign idx_slot_fe = instr_address_fe[2:0];
 assign slot_hit_fe = (slot_not_occupied_fe) ? 1'b0 :
                      (counters_and_address[idx_slot_fe][7:0]==instr_address_fe[7:0]) ?
                      1'b1 : 1'b0;
 assign slot_not_occupied_fe = (counters_and_address[idx_slot_fe][8:8]==1'b0) ? 1'b1 : 1'b0;

 wire [2:0] idx_slot_alu;
 wire  slot_hit_alu;
 wire  slot_not_occupied_alu;
 wire  slot_occupied_alu;
 assign idx_slot_alu = instr_address_alu[2:0];
 assign slot_hit_alu = (counters_and_address[idx_slot_alu][7:0]==instr_address_alu[7:0]) ?
                      1'b1 : 1'b0;
 assign slot_not_occupied_alu = (counters_and_address[idx_slot_alu][8:8]==1'b0) ? 1'b1 : 1'b0;
 assign slot_occupied_alu = ! slot_not_occupied_alu;

 // output logic:
 assign branch_taken_out = (slot_hit_fe) ? counters_and_address[idx_slot_fe][10:10] : 1'b0;

 always @(posedge clk or posedge rst) begin
     if (rst) begin
         counters_and_address [0] <= 11'b000_0000_0000;
         counters_and_address [1] <= 11'b000_0000_0000;
         counters_and_address [2] <= 11'b000_0000_0000;
         counters_and_address [3] <= 11'b000_0000_0000;
         counters_and_address [4] <= 11'b000_0000_0000;
         counters_and_address [5] <= 11'b000_0000_0000;
         counters_and_address [6] <= 11'b000_0000_0000;
         counters_and_address [7] <= 11'b000_0000_0000;
     end else begin
         if (is_conditional_branch_fe) begin
             if (slot_not_occupied_fe) begin
                 counters_and_address [idx_slot_fe] [7:0] <= instr_address_fe[7:0];
                 counters_and_address [idx_slot_fe] [8:8] <= 1'b1;
                 counters_and_address [idx_slot_fe] [10:10] <= 1'b0; // or branch taken ?
             end else begin
                 if (slot_hit_fe) begin
                     counters_and_address [idx_slot_fe] [10:10] <= counters_and_address [idx_slot_fe] [10:10] ;
                 end else begin
                     // if slot hit fails, drive the current slot with the new address and reset the counter
                     counters_and_address [idx_slot_fe] [7:0] <= instr_address_fe[7:0];
                     counters_and_address [idx_slot_fe] [8:8] <= 1'b1;
                     counters_and_address [idx_slot_fe] [10:10] <= 1'b0; // or branch_taken_in ?
                 end
             end
         end
         if (is_conditional_branch_alu) begin
             if (slot_occupied_alu) begin
                 if (slot_hit_alu) begin
                     counters_and_address [idx_slot_alu] [10:10] <= branch_taken_in;
                 end
             end
         end
     end
 end
 endmodule


// === Contents from: Orer0000000001.v ===
 module Orer0000000001 (
     input  [15:0] op_1,
     input  [15:0] op_2,
     output [15:0] result
     );
 wire [15:0] result;
 wire [15:0] op_1;
 wire [15:0] op_2;
 assign result = op_1 | op_2;
 endmodule


// === Contents from: RegisterFile0000000001.v ===
 module RegisterFile0000000001 (
     input clk,
     input  [7:0] reg_addr_1,
     input  [7:0] reg_addr_2,
     input  [0:0] write_en,
     input  [7:0] reg_addr_in,
     input  [15:0] data_in,
     output [15:0] data_out_1,
     output [15:0] data_out_2,
     output [15:0] mem_test
     );
 reg [15:0] mem [255:0];
 assign data_out_1 = mem[reg_addr_1];
 assign data_out_2 = mem[reg_addr_2];
 assign mem_test = mem[0];
 always @(posedge clk)
 begin
     if (write_en)
     begin
         mem[reg_addr_in] <= data_in;
     end
 end
 endmodule


// === Contents from: Substractor0000000001.v ===
 module Substractor0000000001 (
     input  [15:0] op_1,
     input  [15:0] op_2,
     output [15:0] result
     );
 wire [15:0] result;
 wire [15:0] op_1;
 wire [15:0] op_2;
 assign result = op_1 - op_2;
 endmodule


// === Contents from: Xorer0000000001.v ===
 module Xorer0000000001 (
     input  [15:0] op_1,
     input  [15:0] op_2,
     output [15:0] result
     );
 wire [15:0] result;
 wire [15:0] op_1;
 wire [15:0] op_2;
 assign result = op_1 ^ op_2;
 endmodule


