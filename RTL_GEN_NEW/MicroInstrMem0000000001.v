 module MicroInstrMem0000000001 (
        input [7:0] micro_code_addr_in,
        output [31:0] micro_code_data_out,
        input [7:0] micro_code_addr_speculative_fetch_in,
        output [31:0] micro_code_data_speculative_fetch_out
        );
 reg [31:0] mem [255:0];
 assign micro_code_data_out = mem[micro_code_addr_in];
 assign micro_code_data_speculative_fetch_out = mem[micro_code_addr_speculative_fetch_in];
 endmodule
