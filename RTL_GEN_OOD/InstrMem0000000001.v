 module InstrMem0000000001 (
     input [7:0] addr,
     output [31:0] data_out
 );
 reg [31:0] mem [255:0];
 assign data_out = mem[addr[7:1]];
 endmodule
