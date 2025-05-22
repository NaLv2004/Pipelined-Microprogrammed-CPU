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
      (instr[31:24]==8'b10000000) ? 8'b00111010: // decimal: 58
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
      (instr[31:24]==8'b10000000) ? 3'b100: // 010
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
