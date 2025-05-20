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
 assign alu_operand_1 = (micro_code[9:9] == 1'b1) ?  alu_memory_in:
                        (micro_code[7:7] == 1'b1) ? alu_regfile_in_1: 16'b0;
 assign alu_operand_2 = (micro_code[8:8] == 1'b1) ?  alu_memory_in:
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
