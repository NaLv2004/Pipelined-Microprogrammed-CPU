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
