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
     if (rst==0) begin
     if ((micro_code_cnt_reg == 0 | exec_combined_reg) && (!flush_pipeline))  // prev: o_exec_ready_combined
     begin
         micro_code_addr_reg <= micro_code_addr_in;
         micro_code_cnt_reg <= micro_code_cnt_in;
         cu_instruction_reg <= instr_cu_in;
         instr_address_not_taken_reg <= instr_address_not_taken_de_cu;
         branch_instr_address_reg <= branch_instr_address_de_cu;
         branch_prediction_result_reg <= branch_prediction_result_de_cu;
         micro_code_addr_speculative_fetch_reg <= 8'b1111_1111;
      end
      if (micro_code_cnt_reg == 0 && (!flush_pipeline))
      begin
         instruction_normal_reg <= instr_cu_in;
      end
      if (micro_code_cnt_reg > 0)
      begin
         micro_code_cnt_reg <= micro_code_cnt_reg - 1;
         micro_code_addr_reg <= micro_code_addr_reg + 1;
         micro_code_addr_speculative_fetch_reg <= micro_code_addr_in;
      end
      end
 end
 endmodule
