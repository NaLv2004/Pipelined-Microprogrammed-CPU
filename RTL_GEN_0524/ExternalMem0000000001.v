 module ExternalMem0000000001 (
     input clk,
     input [31:0] micro_code,
     input [7:0] addr,
     input [15:0] data_in,
     output [15:0] data_out,
     output [15:0] data_test
     );
 reg [15:0] mem [255:0];
 reg [7:0] MAR;
 reg [15:0] MBR;
 wire [15:0] data_out_instant;
 wire [15:0] read_en;
 assign data_out = MBR;
 assign data_test = mem[0];


 always @(posedge clk)
 begin
     case (micro_code[4:4])
         1'b1: MAR <= addr;
     endcase
 end

 always @(posedge clk)
 begin
     case (micro_code[3:3])
         1'b1: MBR <= mem[MAR];
     endcase
     case (micro_code[2:2])
         1'b1: MBR <= data_in;
     endcase
     case (micro_code[1:1])
         1'b1: mem[MAR] <= MBR;
     endcase
 end
 endmodule
