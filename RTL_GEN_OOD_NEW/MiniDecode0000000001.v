 module MiniDecode0000000001 (
     input  [31:0] instr,
     output is_unconditional_branch,
     output is_conditional_branch
 );
 assign is_unconditional_branch = (instr[31:28]==4'b0100) ? 1'b1 : 1'b0;
 assign is_conditional_branch = (instr[31:28]==4'b0110) ? 1'b1 : 1'b0;
 endmodule
