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
