 module CPUTop0000000001 ;
 reg clk;
 reg rst;
 wire [15:0] imem_addr;
 wire [31:0] imem_data;
 wire [7:0] register_file_addr_1;
 wire [7:0] register_file_addr_2;
 wire [15:0] register_data_out_1;
 wire [15:0] register_data_out_2;
 wire [31:0] micro_code;
 wire [7:0] micro_code_addr;
 wire [31:0] micro_code_speculative_fetch;  // REASSIGN!
 wire [7:0] micro_code_addr_speculative_fetch;  // REASSIGN!
 wire [15:0] alu_result;
 wire [15:0] data_memory_alu;
 wire [7:0] address_memory_alu;
 wire [0:0] write_en_memory;
 wire [0:0] write_en_regfile;
 wire [7:0] register_file_addr_dest;
 wire [15:0] mem_regfile_test;
 wire [15:0] mem_external_test;
 wire [15:0] mem_regfile_test1;
 wire [15:0] mem_external_test1;
 wire [0:0] flush_pipeline; // flush pipeline when branch prediction fails
 wire dec_ready;
 wire exec_ready; // connects CU and Fetch
 // fe-de; de-cu; cu-alu; alu-fe interfaces
 wire [49:0] fetch_idecode_interface;
 wire [91:0] idecode_cu_interface;
 wire [112:0] cu_alu_interface;
 wire [18:0] alu_fetch_interface;
Fetch0000000001  u_0000000001_Fetch0000000001(.clk(clk), .rst(rst), .imem_addr(imem_addr), .imem_data(imem_data), .dec_ready(dec_ready), .exec_ready(exec_ready), .flush_pipeline(flush_pipeline), .fetch_idecode_interface(fetch_idecode_interface), .alu_fetch_interface(alu_fetch_interface));
InstrMem0000000001  u_0000000001_InstrMem0000000001(.addr(imem_addr), .data_out(imem_data));
Decode0000000001  u_0000000001_Decode0000000001(.clk(clk), .rst(rst), .dec_ready(dec_ready), .flush_pipeline(flush_pipeline), .fetch_idecode_interface(fetch_idecode_interface), .idecode_cu_interface(idecode_cu_interface));
CU0000000001  u_0000000001_CU0000000001(.clk(clk), .rst(rst), .micro_code_in_normal(micro_code), .micro_code_in_speculative(micro_code_speculative_fetch), .micro_code_addr_out(micro_code_addr), .micro_code_addr_speculative_fetch(micro_code_addr_speculative_fetch), .o_exec_ready_combined(exec_ready), .flush_pipeline(flush_pipeline), .idecode_cu_interface(idecode_cu_interface), .cu_alu_interface(cu_alu_interface));
RegisterFile0000000001  u_0000000001_RegisterFile0000000001(.clk(clk), .reg_addr_1(register_file_addr_1), .reg_addr_2(register_file_addr_2), .data_out_1(register_data_out_1), .data_out_2(register_data_out_2), .write_en(write_en_regfile), .reg_addr_in(register_file_addr_dest), .data_in(alu_result), .mem_test(mem_regfile_test));
MicroInstrMem0000000001  u_0000000001_MicroInstrMem0000000001(.micro_code_addr_in(micro_code_addr), .micro_code_data_out(micro_code), .micro_code_addr_speculative_fetch_in(micro_code_addr_speculative_fetch), .micro_code_data_speculative_fetch_out(micro_code_speculative_fetch));
ExternalMem0000000001  u_0000000001_ExternalMem0000000001(.clk(clk), .micro_code(micro_code), .addr(address_memory_alu), .data_in(alu_result), .data_out(data_memory_alu), .data_test(mem_external_test));
ALU0000000001  u_0000000001_ALU0000000001(.clk(clk), .alu_regfile_in_1(register_data_out_1), .alu_regfile_in_2(register_data_out_2), .alu_memory_in(data_memory_alu), .alu_result(alu_result), .alu_regfile_address_out_1(register_file_addr_1), .alu_regfile_address_out_2(register_file_addr_2), .alu_memory_address_out(address_memory_alu), .alu_memory_write_en_out(write_en_memory), .alu_regfile_write_en_out(write_en_regfile), .alu_regfile_address_out(register_file_addr_dest), .cu_alu_interface(cu_alu_interface), .alu_fetch_interface(alu_fetch_interface));
 always #5 clk = ~clk;
 initial begin
   clk = 0;
   rst = 1;
   #10 rst = 0;
 end
 initial begin
 u_0000000001_InstrMem0000000001.mem[0] = 32'b1000_0000_0000_1000_0000_0000_0000_0000;
 u_0000000001_InstrMem0000000001.mem[1] = 32'b0000_0001_0000_0000_0000_0001_0000_0000;
 u_0000000001_InstrMem0000000001.mem[2] = 32'b0000_0010_0000_0010_0000_0000_0000_0000;
 u_0000000001_InstrMem0000000001.mem[3] = 32'b0000_0001_0000_1000_0000_0000_0000_0001;
 u_0000000001_InstrMem0000000001.mem[4] = 32'b0100_0000_0001_0000_0000_0000_0000_0000;
 u_0000000001_InstrMem0000000001.mem[5] = 32'b0000_0001_0000_0000_0000_0010_0000_0000;
 u_0000000001_InstrMem0000000001.mem[6] = 32'b0000_0001_0000_0000_0000_0001_0000_0000;
 u_0000000001_InstrMem0000000001.mem[7] = 32'b0000_0001_0000_0000_0000_0010_0000_0000;
 u_0000000001_InstrMem0000000001.mem[8] = 32'b1000_0001_0000_0000_0000_0000_0000_0000;
 u_0000000001_InstrMem0000000001.mem[9] = 32'b0110_0000_0000_0011_0000_0011_0000_0100;
 u_0000000001_InstrMem0000000001.mem[10] = 32'b0000_0001_0000_0000_0000_0001_0000_0000;
 u_0000000001_InstrMem0000000001.mem[11] = 32'b0000_0001_0000_0000_0000_0010_0000_0000;
 u_0000000001_InstrMem0000000001.mem[12] = 32'b0000_0001_0000_0000_0000_0001_0000_0000;
 u_0000000001_InstrMem0000000001.mem[13] = 32'b0000_0001_0000_0000_0000_0010_0000_0000;
 u_0000000001_MicroInstrMem0000000001.mem[0] = 16'b0001_0000_1100_0001;
 u_0000000001_MicroInstrMem0000000001.mem[1] = 16'b0010_0000_1100_0001;
 u_0000000001_MicroInstrMem0000000001.mem[2] = 16'b0011_0000_1100_0000;
 u_0000000001_MicroInstrMem0000000001.mem[3] = 16'b0100_0000_1100_0000;
 u_0000000001_MicroInstrMem0000000001.mem[4] = 16'b0101_0000_1100_0000;
 u_0000000001_MicroInstrMem0000000001.mem[5] = 16'b0110_0000_1100_0000;
 u_0000000001_MicroInstrMem0000000001.mem[6] = 16'b0111_0000_1100_0000;
 u_0000000001_MicroInstrMem0000000001.mem[7] = 16'b1000_0000_1100_0000;
 u_0000000001_MicroInstrMem0000000001.mem[8] = 16'b0000_1000_0001_0001;
 u_0000000001_MicroInstrMem0000000001.mem[9] = 16'b0000_0000_0000_1001;
 u_0000000001_MicroInstrMem0000000001.mem[10] = 16'b0001_0010_0100_0001;
 u_0000000001_MicroInstrMem0000000001.mem[11] = 16'b0000_1000_0001_0001;
 u_0000000001_MicroInstrMem0000000001.mem[12] = 16'b0000_0000_0000_1001;
 u_0000000001_MicroInstrMem0000000001.mem[13] = 16'b0010_0010_0100_0001;
 u_0000000001_MicroInstrMem0000000001.mem[14] = 16'b0000_1000_0001_0001;
 u_0000000001_MicroInstrMem0000000001.mem[15] = 16'b0000_0000_0000_1001;
 u_0000000001_MicroInstrMem0000000001.mem[16] = 16'b0011_0010_0100_0001;
 u_0000000001_MicroInstrMem0000000001.mem[17] = 16'b0000_1000_0001_0001;
 u_0000000001_MicroInstrMem0000000001.mem[18] = 16'b0000_0000_0000_1001;
 u_0000000001_MicroInstrMem0000000001.mem[19] = 16'b0100_0010_0100_0001;
 u_0000000001_MicroInstrMem0000000001.mem[20] = 16'b0000_1000_0001_0001;
 u_0000000001_MicroInstrMem0000000001.mem[21] = 16'b0000_0000_0000_1001;
 u_0000000001_MicroInstrMem0000000001.mem[22] = 16'b0101_0010_0100_0001;
 u_0000000001_MicroInstrMem0000000001.mem[23] = 16'b0000_1000_0001_0001;
 u_0000000001_MicroInstrMem0000000001.mem[24] = 16'b0000_0000_0000_1001;
 u_0000000001_MicroInstrMem0000000001.mem[25] = 16'b0110_0010_0100_0001;
 u_0000000001_MicroInstrMem0000000001.mem[26] = 16'b0000_1000_0001_0001;
 u_0000000001_MicroInstrMem0000000001.mem[27] = 16'b0000_0000_0000_1001;
 u_0000000001_MicroInstrMem0000000001.mem[28] = 16'b0111_0010_0100_0001;
 u_0000000001_MicroInstrMem0000000001.mem[29] = 20'b0010_0000_1000_0001_0000;
 u_0000000001_MicroInstrMem0000000001.mem[30] = 20'b0000_0000_0000_0000_1000;
 u_0000000001_MicroInstrMem0000000001.mem[31] = 20'b0001_0000_0010_0000_0001;
 u_0000000001_MicroInstrMem0000000001.mem[32] = 16'b0000_0100_1001_0100;
 u_0000000001_MicroInstrMem0000000001.mem[33] = 16'b0000_0000_0000_0010;
 u_0000000001_MicroInstrMem0000000001.mem[34] = 16'b0000_0000_0000_0000;
 u_0000000001_MicroInstrMem0000000001.mem[36] = 16'b1100_0000_1100_0000;
 u_0000000001_MicroInstrMem0000000001.mem[255] = 16'b0000_0000_0000_0000;
 u_0000000001_ExternalMem0000000001.mem[0] = 16'b0000_0001;
 u_0000000001_ExternalMem0000000001.mem[1] = 16'b0001_0010;
 u_0000000001_ExternalMem0000000001.mem[2] = 16'b0010_0000;
 u_0000000001_ExternalMem0000000001.mem[3] = 16'b0000_0100;
 u_0000000001_ExternalMem0000000001.mem[4] = 16'b0000_0101;
 u_0000000001_ExternalMem0000000001.mem[5] = 16'b0000_0110;
 u_0000000001_ExternalMem0000000001.mem[6] = 16'b0000_0111;
 u_0000000001_ExternalMem0000000001.mem[7] = 16'b0000_1000;
 u_0000000001_ExternalMem0000000001.mem[8] = 16'b0000_1111;
 u_0000000001_ExternalMem0000000001.mem[9] = 16'b0000_1010;
 u_0000000001_ExternalMem0000000001.mem[10] = 16'b0000_1011;
 u_0000000001_RegisterFile0000000001.mem[0] = 16'b0000_0000_0000_0001;
 u_0000000001_RegisterFile0000000001.mem[1] = 16'b0000_0000_0000_0010;
 u_0000000001_RegisterFile0000000001.mem[2] = 16'b0000_0000_0000_0011;
 u_0000000001_RegisterFile0000000001.mem[3] = 16'b0000_0000_0000_0101;
 u_0000000001_RegisterFile0000000001.mem[4] = 16'b0000_0000_0000_0110;
 u_0000000001_RegisterFile0000000001.mem[5] = 16'b0000_0000_0000_0111;
 u_0000000001_RegisterFile0000000001.mem[6] = 16'b0000_0000_0000_1000;
 u_0000000001_RegisterFile0000000001.mem[7] = 16'b0000_0000_0000_1001;
 u_0000000001_RegisterFile0000000001.mem[8] = 16'b0000_0000_0000_1010;
 u_0000000001_RegisterFile0000000001.mem[9] = 16'b0000_0000_0000_1011;
 u_0000000001_RegisterFile0000000001.mem[10] = 16'b0000_0000_0000_1100;
 u_0000000001_RegisterFile0000000001.mem[11] = 16'b0000_0000_0000_1101;
 u_0000000001_RegisterFile0000000001.mem[12] = 16'b0000_0000_0000_1110;
 u_0000000001_RegisterFile0000000001.mem[13] = 16'b0000_0000_0000_1111;
 u_0000000001_RegisterFile0000000001.mem[14] = 16'b0000_0000_0001_0000;
 u_0000000001_RegisterFile0000000001.mem[15] = 16'b0000_0000_0001_0001;
 u_0000000001_RegisterFile0000000001.mem[16] = 16'b0000_0000_0001_0010;
 u_0000000001_RegisterFile0000000001.mem[17] = 16'b0000_0000_0001_0011;
 end
 initial begin
     $dumpfile("wave.vcd");
     $dumpvars(0, CPUTop0000000001);
     #2500
     $finish;
 end
 endmodule
