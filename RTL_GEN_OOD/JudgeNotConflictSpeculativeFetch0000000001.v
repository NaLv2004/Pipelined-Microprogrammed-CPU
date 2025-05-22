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
