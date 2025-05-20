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
 assign opcode = instr[2:0];  // 假设操作码在低3位
 assign rs1 = instr[7:3];     // 源寄存器1
 assign rs2 = instr[12:8];    // 源寄存器2
 assign rd = instr[15:13];    // 目的寄存器（示例位置）
 assign micro_code = micro_code_reg;
 assign instr_address_not_taken_de_cu = instr_address_not_taken_fe_de;
 assign branch_prediction_result_de_cu = branch_prediction_result_fe_de;
 assign branch_instr_address_de_cu = branch_instr_address_fe_de;
 assign micro_code_addr_out =
     (flush_pipeline==1'b1) ? 8'b1111_1111 : // flush pipeline (no operations)
     (instr[31:24] == 8'b00000000) ? 8'b1111_1111 : // addi)
     (instr[31:24] == 8'b00000001) ? 8'b0000_0000 : // add
     (instr[31:24]== 8'b00010001) ? 8'b0000_1000 : // add, first source operand is from memory
    // (instr[31:24] == 8'b10000000) ? 8'b0000_0001 : // load
     (instr[31:24] == 8'b00000011) ? 8'b0000_0010 : // add
     (instr[31:24] == 8'b00000010) ? 8'b0000_0001 : // sub
     (instr[31:24] == 8'b00000101) ? 8'b0000_0100 : // jmpgez
     (instr[31:24] == 8'b10000000) ? 8'b0001_1101 :  // load
     (instr[31:24] == 8'b10000001) ? 8'b0010_0000 : // store
     (instr[31:24] == 8'b01000000) ? 8'b0010_0010 : // jal (unconditional branch)
     (instr[31:24] == 8'b01100000) ? 8'b0010_0100 : // beq
     8'b1111_1111;  // default
 //assign micro_code_addr_out = instr[31:24];
 // counter: n of micro codes following this address
 assign micro_code_cnt_out =
     (flush_pipeline==1'b1) ? 3'b000 : // flush pipeline (no operations)
     (instr[31:24] == 8'b0000_0000) ? 3'b000 : // addi)
     (instr[31:24] == 8'b0000_0011) ? 3'b010 :
     (instr[31:24] == 8'b0001_0001) ? 3'b010 : // add, first source operand is from memory
     (instr[31:24] == 8'b1000_0000) ? 3'b010 : // load
     (instr[31:24] == 8'b1000_0001) ? 3'b001 : // store
     3'b000;
 // 控制信号寄存器
 always @(posedge clk or posedge rst) begin
     if (rst) begin
         ready_reg <= 1'b0;
     end else begin
         // 简单示例：始终准备接收指令
         ready_reg <= 1'b1;
         // instr_out_reg <= instr;
         // 更复杂的控制示例：
         // if (pipeline_stall_condition)
         //     ready_reg <= 1'b0;
         // else
         //     ready_reg <= 1'b1;
     end
 end
 always @(posedge clk) begin
     micro_code_reg <= 32'b0;
 end
 endmodule
