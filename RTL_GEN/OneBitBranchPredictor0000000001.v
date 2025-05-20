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
