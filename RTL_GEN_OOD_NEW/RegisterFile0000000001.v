 module RegisterFile0000000001 (
     input clk,
     input  [7:0] reg_addr_1,
     input  [7:0] reg_addr_2,
     input  [0:0] write_en,
     input  [7:0] reg_addr_in,
     input  [15:0] data_in,
     output [15:0] data_out_1,
     output [15:0] data_out_2,
     output [15:0] mem_test
     );
 reg [15:0] mem [255:0];
 assign data_out_1 = mem[reg_addr_1];
 assign data_out_2 = mem[reg_addr_2];
 assign mem_test = mem[0];
 always @(posedge clk)
 begin
     if (write_en)
     begin
         mem[reg_addr_in] <= data_in;
     end
 end
 endmodule
