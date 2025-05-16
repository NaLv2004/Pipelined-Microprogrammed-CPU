// Fetch instruction
module fetch (
    input         clk,
    input         rst,
    output [15:0] imem_addr,
    input  [31:0] imem_data,
    output [31:0] instr,
    output        instr_valid,
    output        flush_pipeline,  // stall the entire pipeline when branch prediction fails
    output  [7:0] instr_address_not_taken,  // The address of instruction not taken in branch prediction
    output  [7:0] branch_instr_address,
    output        branch_prediction_result,
    input         dec_ready,
    input         exec_ready,
    input         branch_prediction_failed,
    input   [7:0] instr_address_not_taken_alu_fe,
    input   [7:0] branch_instr_address_alu_fe,
    input         is_conditional_branch_alu_fe,
    input         branch_taken_in
);

reg [15:0] pc;
reg [31:0] instruction_reg;
reg        valid_reg;
reg [7:0]  branch_target_buffer; // target instruction address if the branch is taken
reg [7:0]  pc_delayed;
reg [0:0]  branch_prediction_failed_buffer; // branch prediction failed flag
wire [7:0] branch_target_address_wire;
wire [7:0] instr_address_not_taken;
wire [7:0] instr_address_not_taken_alu_fe;
wire branch_taken_one_bit_predict;
wire branch_prediction_result_in_fe;
reg branch_prediction_result_reg;
assign instr_address_not_taken = branch_target_buffer;

wire [7:0] curr_instr_address;
assign curr_instr_address = pc[7:0];

// instruction mini-decode: decide whether the instruction is a branch instruction
wire is_conditional_branch;
wire is_unconditional_branch;
i_mini_decode u_i_mini_decode (.instr(imem_data),
                               .is_unconditional_branch(is_unconditional_branch),
                               .is_conditional_branch(is_conditional_branch));


// branch predictor
wire [15:0] branch_predict;
assign branch_predict = (is_unconditional_branch)? imem_data[23:16]:
                        (is_conditional_branch && branch_taken_one_bit_predict)? imem_data[7:0]:
                        (pc+16'h2);
assign branch_target_address_wire = (is_conditional_branch)? imem_data[7:0] : branch_target_buffer;
assign flush_pipeline = branch_prediction_failed;

assign branch_instr_address = pc_delayed;
assign branch_prediction_result = branch_prediction_result_reg;
assign branch_prediction_result_in_fe = (is_conditional_branch && branch_taken_one_bit_predict)? 1'b1 : 1'b0;

// one bit branch predictor
one_bit_branch_predictor u_one_bit_branch_predictor (
   .clk(clk),
   .rst(rst),
   .instr_address_fe(curr_instr_address),
   .instr_address_alu(branch_instr_address_alu_fe),
   .branch_taken_in(branch_taken_in),
   .is_conditional_branch_fe(is_conditional_branch),
   .is_conditional_branch_alu(is_conditional_branch_alu_fe),
   .branch_taken_out(branch_taken_one_bit_predict)
);


always @(posedge clk or posedge rst) begin
    if (rst) begin
        branch_target_buffer <= 8'b0;
        pc_delayed <= 8'b0;
        branch_prediction_result_reg <= 1'b0;
    end else begin
        branch_target_buffer <= branch_target_address_wire;
    end
end


always @(posedge clk or posedge rst) begin
    if (rst) begin
        pc <= 16'h0;
    end else if (valid_reg && dec_ready && exec_ready) begin
        pc_delayed <= pc[7:0];
        branch_prediction_result_reg <= branch_prediction_result_in_fe;
        if (branch_prediction_failed) begin
            instruction_reg <= 32'b0;
            // prev:pc <= branch_target_buffer;
            pc <= instr_address_not_taken_alu_fe;
        end else begin
            instruction_reg <= imem_data;
            // prev: pc <= pc + 16'h2;
            pc <= branch_predict;
        end
    end
end

always @(posedge clk or posedge rst) begin
    if (rst) begin
        valid_reg <= 1'b0;
        instruction_reg <= 31'b0;
    end else begin
        valid_reg <= 1'b1;
    end
end

assign imem_addr = pc;
assign instr_valid = valid_reg;
// assign instr = imem_data;
assign instr = instruction_reg;


endmodule

// decide whether the instruction is a branch instruction
module i_mini_decode(
    input  [31:0] instr,
    output        is_unconditional_branch,
    output        is_conditional_branch
);
assign is_unconditional_branch = (instr[31:28]==4'b0100) ? 1'b1 : 1'b0;
assign is_conditional_branch = (instr[31:28]==4'b0110) ? 1'b1 : 1'b0;
endmodule


// branch predictor (using 1-bit counter)
// instr_address_fe : the address of branch instruction in fetch stage
// instr_address_alu : the address of executed branch instruction

module one_bit_branch_predictor(
    input         clk,
    input         rst,
    input [7:0]   instr_address_fe,
    input [7:0]   instr_address_alu,
    input         branch_taken_in,
    input         is_conditional_branch_fe,
    input         is_conditional_branch_alu,
    output        branch_taken_out,
    output [7:0]  mem_one_bit_predictor_test
);
wire [7:0] instr_address_fe;
wire [7:0] instr_address_alu;

// 8 counters and their corresponding addresses 
// [10:10] is counter; 
// [8:8] indicates whether the slot is currently in use (1: in use, 0: not in use)
// [7:0] is address
reg [10:0] counters_and_address[7:0] ; 

// for branch predictor test
assign mem_one_bit_predictor_test[0] = counters_and_address[0][10];
assign mem_one_bit_predictor_test[1] = counters_and_address[1][10];
assign mem_one_bit_predictor_test[2] = counters_and_address[2][10];
assign mem_one_bit_predictor_test[3] = counters_and_address[3][10];
assign mem_one_bit_predictor_test[4] = counters_and_address[4][10];
assign mem_one_bit_predictor_test[5] = counters_and_address[5][10];
assign mem_one_bit_predictor_test[6] = counters_and_address[6][10];
assign mem_one_bit_predictor_test[7] = counters_and_address[7][10];

wire [2:0] idx_slot_fe;
wire slot_hit_fe;
wire slot_not_occupied_fe;
assign idx_slot_fe = instr_address_fe[2:0];
assign slot_hit_fe = (slot_not_occupied_fe) ? 1'b0 :
                     (counters_and_address[idx_slot_fe][7:0]==instr_address_fe[7:0]) ? 1'b1 : 1'b0;
assign slot_not_occupied_fe = (counters_and_address[idx_slot_fe][8:8]==1'b0) ? 1'b1 : 1'b0;

wire [2:0] idx_slot_alu;
wire slot_hit_alu;
wire slot_not_occupied_alu;
wire slot_occupied_alu;
assign idx_slot_alu = instr_address_alu[2:0];
assign slot_hit_alu = (counters_and_address[idx_slot_alu][7:0]==instr_address_alu[7:0]) ? 1'b1 : 1'b0;
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


// decoder
module idecode (
    input         clk,
    input         rst,
    input  [31:0] instr,
    input         instr_valid,
    input         flush_pipeline,
    input   [7:0]      instr_address_not_taken_fe_de,
    input   [7:0]  branch_instr_address_fe_de,
    input         branch_prediction_result_fe_de,
    output        dec_ready,
    output [15:0]  micro_code,
    
    // 象征性译码输出
    output [2:0]  opcode,
    output [4:0]  rs1,
    output [4:0]  rs2,
    output [4:0]  rd,
    output [31:0]  instr_out,
    output [7:0]  micro_code_addr_out,
    output [2:0]  micro_code_cnt_out,
    output  [7:0]      instr_address_not_taken_de_cu,
    output  [7:0]  branch_instr_address_de_cu,
    output        branch_prediction_result_de_cu
);

// Ready信号生成逻辑
reg ready_reg;
reg micro_code_reg;
reg [7:0] micro_code_addr_reg;
reg [31:0] instr_out_reg;
reg [2:0] micro_code_cnt_reg;
// assign instr_out = instr_out_reg;
assign instr_out = instr;
assign dec_ready = ready_reg;
wire [7:0] micro_code_addr_out;
wire [7:0] micro_code_cnt_in;
wire [7:0] instr_address_not_taken_de_cu;
wire [7:0] instr_address_not_taken_fe_de;
// wire [31:0] instr;

// 象征性译码逻辑
assign opcode = instr[2:0];  // 假设操作码在低3位
assign rs1 = instr[7:3];     // 源寄存器1
assign rs2 = instr[12:8];    // 源寄存器2
assign rd = instr[15:13];    // 目的寄存器（示例位置）
assign micro_code = micro_code_reg;
assign instr_address_not_taken_de_cu = instr_address_not_taken_fe_de;
assign branch_prediction_result_de_cu = branch_prediction_result_fe_de;
assign branch_instr_address_de_cu = branch_instr_address_fe_de;
//assign micro_code_addr_out = micro_code_addr_reg;
//assign micro_code_cnt_out = micro_code_cnt_reg;

// micro code address generation
assign micro_code_addr_out = 
    (flush_pipeline==1'b1) ? 8'b1111_1111 : // flush pipeline (no operations)
    (instr[31:24] == 8'b00000000) ? 8'b1111_1111 : // addi)
    (instr[31:24] == 8'b00000001) ? 8'b0000_0000 : // add
    (instr[31:24]== 8'b00010001) ? 8'b0000_1000 : // add, first source operand is from memory
   // (instr[31:24] == 8'b10000000) ? 8'b0000_0001 : // load
    (instr[31:24] == 8'b00000011) ? 8'b0000_0010 : // add
    (instr[31:24] == 8'b00000100) ? 8'b0000_0011 : // sub
    (instr[31:24] == 8'b00000101) ? 8'b0000_0100 : // jmpgez
    (instr[31:24] == 8'b10000000) ? 8'b0001_1101 :  // load
    (instr[31:24] == 8'b10000001) ? 8'b0010_0000 : // store
    (instr[31:24] == 8'b01000000) ? 8'b0010_0010 : // jal (unconditional branch) 
    (instr[31:24] == 8'b01100000) ? 8'b0010_0100 : // beq
    8'b1111_1111;  // default
//assign micro_code_addr_out = instr[31:24];
// counter: n of micro codes following this address
assign micro_code_cnt_out = 
    (flush_pipeline==1'b1) ? 3'b000 : // flush pipeline (no operations)
    (instr[31:24] == 8'b0000_0000) ? 3'b000 : // addi)
    (instr[31:24] == 8'b0000_0011) ? 3'b010 :
    (instr[31:24] == 8'b0001_0001) ? 3'b010 : // add, first source operand is from memory
    (instr[31:24] == 8'b1000_0000) ? 3'b010 : // load
    (instr[31:24] == 8'b1000_0001) ? 3'b001 : // store
    3'b000;                   

// 控制信号寄存器
always @(posedge clk or posedge rst) begin
    if (rst) begin
        ready_reg <= 1'b0;
    end else begin
        // 简单示例：始终准备接收指令
        ready_reg <= 1'b1;
        // instr_out_reg <= instr;
        // 更复杂的控制示例：
        // if (pipeline_stall_condition) 
        //     ready_reg <= 1'b0;
        // else
        //     ready_reg <= 1'b1;
    end
end

always @(posedge clk) begin
    micro_code_reg <= 16'b0;
end

endmodule

// CU controls timing of micro-instructions
module cu (
    input clk,
    input rst,
    input [7:0] micro_code_addr_in,
    input [2:0] micro_code_cnt_in,  // n of micro code for this instruction
    input [31:0] instr_cu_in,
    input flush_pipeline,
    output [7:0] micro_code_addr_out,
    output [15:0] micro_code_out,
    output o_exec_ready,  // CU is ready to receive new micro-code address from the decoder.
    output [31:0] instr_cu_out,
    input [7:0] instr_address_not_taken_de_cu,
    output [7:0] instr_address_not_taken_cu_alu,
    input [7:0] branch_instr_address_de_cu,
    input branch_prediction_result_de_cu,
    output [7:0] branch_instr_address_cu_alu,
    output branch_prediction_result_cu_alu
);
wire clk;
wire [7:0] micro_code_addr_in;
wire [15:0] micro_code_out;
wire [7:0] instr_address_not_taken_de_cu;
wire [7:0] instr_address_not_taken_cu_alu;
reg [7:0] micro_code_addr_reg;
reg [2:0] micro_code_cnt_reg;
reg [31:0] cu_instruction_reg;
reg [7:0] instr_address_not_taken_reg;
reg [7:0] branch_instr_address_reg;
reg [0:0] branch_prediction_result_reg;
assign instr_address_not_taken_cu_alu = instr_address_not_taken_reg;
assign micro_code_addr_out = micro_code_addr_reg;
assign branch_instr_address_cu_alu = branch_instr_address_reg;
assign branch_prediction_result_cu_alu = branch_prediction_result_reg;
assign instr_cu_out = cu_instruction_reg;
assign o_exec_ready = (micro_code_cnt_reg==3'b0) ? 1'b1 : 1'b0;  
// CU is ready to receive new micro-code address when micro-code-reg == 0 (all the micro-codes executed)
always @ (posedge clk or negedge rst)
begin
    if (rst || flush_pipeline) begin
        micro_code_cnt_reg <= 3'b0;
        micro_code_addr_reg <= 8'b1111_1111;
        cu_instruction_reg <= 32'b0;
        instr_address_not_taken_reg <= 8'b0;
        branch_instr_address_reg <= 8'b0;
        branch_prediction_result_reg <= 1'b0;
    end  
    if (rst==0) begin
    if (micro_code_cnt_reg == 0)
    begin
        micro_code_addr_reg <= micro_code_addr_in;
        micro_code_cnt_reg <= micro_code_cnt_in;
        cu_instruction_reg <= instr_cu_in;
        instr_address_not_taken_reg <= instr_address_not_taken_de_cu;
        branch_instr_address_reg <= branch_instr_address_de_cu;
        branch_prediction_result_reg <= branch_prediction_result_de_cu;
    end
    if (micro_code_cnt_reg > 0)
    begin
        micro_code_cnt_reg <= micro_code_cnt_reg - 1;
        micro_code_addr_reg <= micro_code_addr_reg + 1;
    end
    end

end
endmodule
// ALU

module alu (
input clk,
input [31:0] instruction, 
input [15:0] micro_code,
input [15:0] alu_regfile_in_1, // opcode 1 from regiester file
input [15:0] alu_regfile_in_2, // opcode 2 from register file
input [15:0] alu_memory_in,
input [7:0] instr_address_not_taken_cu_alu,
input branch_prediction_result_cu_alu,
input [7:0] branch_instr_address_cu_alu,
output [15:0] alu_result, // result calculated by alu
output [7:0] alu_regfile_address_out_1,
output [7:0] alu_regfile_address_out_2,
output [7:0] alu_memory_address_out,
output [0:0] alu_memory_write_en_out,
output [7:0] alu_regfile_address_out,
output [0:0] alu_regfile_write_en_out,
output [0:0] flush_pipeline_out,
output [7:0] instr_address_not_taken_alu_fe,
output [7:0] branch_instr_address_alu_fe,
output [0:0] is_conditional_branch_alu_fe,
output [0:0] branch_taken_alu_fe
);

// input and output ports
wire clk;
wire [31:0] instruction;
wire [15:0] micro_code;
wire [15:0] alu_result;
wire [15:0] alu_regfile_in_1;
wire [15:0] alu_regfile_in_2;
wire [7:0] alu_regfile_address_out_1;
wire [7:0] alu_regfile_address_out_2;
wire [15:0] alu_operand_1;
wire [15:0] alu_operand_2;
wire [7:0] instr_address_not_taken_cu_alu;
wire [7:0] instr_address_not_taken_alu_fe;
// results for various operations
wire [15:0] alu_add_result;
wire [15:0] alu_sub_result;
wire [15:0] alu_xor_result;
wire [15:0] alu_and_result;
wire [15:0] alu_or_result;
wire alu_judge_equal_result;



reg[15:0] alu_result_reg;
// assign alu_result = alu_result_reg;
assign alu_regfile_address_out_1 = instruction[23:16];
assign alu_regfile_address_out_2 = instruction[15:8];


// when reading from memory from is required
assign alu_memory_address_out = (micro_code[11:11] == 1'b1) ?  instruction[23:16]: 
                                (micro_code[10:10] == 1'b1) ? instruction[15:8]: 8'b0000_0000; 


// assign alu input operands
assign alu_operand_1 = (micro_code[9:9] == 1'b1) ?  alu_memory_in: 
                       (micro_code[7:7] == 1'b1) ? alu_regfile_in_1: 16'b0;

assign alu_operand_2 = (micro_code[8:8] == 1'b1) ?  alu_memory_in:
                       (micro_code[6:6] == 1'b1) ? alu_regfile_in_2: 
                       (micro_code[5:5] == 1'b1) ? instruction[7:0] : 16'b0;

// write enable for register file
assign alu_regfile_write_en_out = (micro_code[0:0]==1'b1) ? 1'b1: 1'b0;

// assign address
assign alu_regfile_address_out = instruction[7:0];

// write enable for memory
assign alu_memory_write_en_out = (micro_code[1:1]==1'b1) ? 1'b1: 1'b0;

                    

adder u_adder(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_add_result));
subtractor u_subtractor(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_sub_result));
xorer u_xorer(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_xor_result));
ander u_ander(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_and_result));
orer u_orer(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_or_result));
judge_equal u_judge_equal(.op_1(alu_operand_1), .op_2(alu_operand_2), .result(alu_judge_equal_result));

// select operation based on micro-code
assign alu_result = (micro_code[15:12] == 4'b0001) ? alu_add_result:
                    (micro_code[15:12] == 4'b0010) ? alu_sub_result:
                    (micro_code[15:12] == 4'b0011) ? alu_xor_result:
                    (micro_code[15:12] == 4'b0100) ? alu_and_result:
                    (micro_code[15:12] == 4'b0101) ? alu_or_result:   // 16'b0 is default value
                    (micro_code[15:12] == 4'b0000) ? alu_operand_1: // load
                    (micro_code[15:12] == 4'b1100) ? alu_judge_equal_result: // beq
                    16'b0;

// assign flush_pipeline_out = (instruction[31:28]==4'b0110  && alu_result == branch_prediction_result_cu_alu) ? alu_result : 1'b0;
// send flush pipeline signal to fetch when branch prediction fails
assign is_conditional_branch_alu_fe = (instruction[31:28]==4'b0110) ? 1'b1: 1'b0;
assign flush_pipeline_out = (!(instruction[31:28]==4'b0110)) ? 1'b0: 
                            (alu_result == branch_prediction_result_cu_alu) ? 1'b0: 1'b1;
assign instr_address_not_taken_alu_fe = instr_address_not_taken_cu_alu;
assign branch_instr_address_alu_fe = branch_instr_address_cu_alu;
assign branch_taken_alu_fe = (!(instruction[31:28]==4'b0110)) ? 1'b0:
                             (alu_result) ? 1'b1: 1'b0;

// inner registers
reg [15:0] micro_code_reg;
always @ (posedge clk)
begin
    micro_code_reg <= micro_code;
end

// behaviour according to micro-code
always @ (posedge clk)
begin
    if (micro_code_reg == 16'b0)
    begin
        alu_result_reg <= alu_regfile_in_1 + alu_regfile_in_2;
    end
end

endmodule


module adder (
    input [15:0] op_1,
    input [15:0] op_2,
    output [15:0] result
);
wire [15:0] op_1;
wire [15:0] op_2;
wire [15:0] result;

assign result = op_1 + op_2;
endmodule

module subtractor (
    input [15:0] op_1,
    input [15:0] op_2,
    output [15:0] result
);
wire [15:0] op_1;
wire [15:0] op_2;
wire [15:0] result;

assign result = op_1 - op_2;
endmodule

module xorer (
    input [15:0] op_1,
    input [15:0] op_2,
    output [15:0] result
);
wire [15:0] op_1;
wire [15:0] op_2;
wire [15:0] result;

assign result = op_1 ^ op_2;
endmodule

module ander (
    input [15:0] op_1,
    input [15:0] op_2,
    output [15:0] result
);
wire [15:0] op_1;
wire [15:0] op_2;
wire [15:0] result;

assign result = op_1 & op_2;
endmodule

module orer (
    input [15:0] op_1,
    input [15:0] op_2,
    output [15:0] result
);
wire [15:0] op_1;
wire [15:0] op_2;
wire [15:0] result;

assign result = op_1 | op_2;
endmodule

module judge_equal (
    input [15:0] op_1,
    input [15:0] op_2,
    output [0:0] result
);
assign result = (op_1 == op_2)? 1'b1 : 1'b0;
endmodule


// instruction memory
module instr_mem (
    input  [15:0] addr,
    output [31:0] data_out
);

reg [31:0] mem [0:255]; // 256x16存储器
assign data_out = mem[addr[15:1]];
endmodule


// micro instruction memory 
module micro_instr_mem (
    input [7:0] micro_code_addr_in,
    output [15:0] micro_code_data_out
);

reg [15:0] mem [0:255];
assign micro_code_data_out = mem[micro_code_addr_in];
endmodule

module external_mem (
    input clk,
    input [15:0] micro_code,
    input [7:0] addr,
    input [15:0] data_in,
    output [15:0] data_out,
    output [15:0] data_test
);
reg [15:0] mem [0:255];
reg [7:0] MAR; // memory address register
reg [15:0] MBR; // memory buffer register
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




// register file
module register_file (
    input clk,
    input  [7:0] reg_addr_1,
    input  [7:0] reg_addr_2,
    input [0:0] write_en,
    input [7:0] reg_addr_in,
    input [15:0] data_in,
    output [15:0] data_out_1,
    output [15:0] data_out_2,
    output [15:0] mem_test
);

reg [15:0] mem [0:255]; // 256x16存储器
assign data_out_1 = mem[reg_addr_1];
assign data_out_2 = mem[reg_addr_2];
assign mem_test = mem[0];
always @ (posedge clk)
begin
    if (write_en)
    begin
        mem[reg_addr_in] <= data_in;
    end
end
endmodule


// write back module
module write_back (
    input clk,
    input [0:0] exec_ready_in,
    input [15:0] alu_result,
    input [7:0] reg_addr_dest,
    input [7:0] memory_addr_dest,
    output [0:0] write_en_regfile_out,
    output [15:0] data_out_dest
);
endmodule


// testbench
module tb;

reg clk;
reg rst;
wire [15:0] imem_addr;
wire [31:0] imem_data;
wire [7:0] register_file_addr_1;
wire [7:0] register_file_addr_2;
wire [15:0] register_data_out_1;
wire [15:0] register_data_out_2;
wire [31:0] instr;
wire [31:0] instr_idecode_alu;
wire [31:0] instr_idecode_cu;
wire [31:0] instr_cu_alu;
wire [15:0] micro_code;
wire [7:0] micro_code_addr_de_cu;
wire [7:0] micro_code_addr_cu_alu;
wire [2:0] micro_code_cnt_de_cu;
wire [15:0] alu_result;
wire [15:0] data_memory_alu;
wire [7:0] address_memory_alu;
wire [0:0] write_en_memory;
wire [0:0] write_en_regfile;
wire [7:0] register_file_addr_dest;
wire [15:0] mem_regfile_test;
wire [15:0] mem_external_test;
wire [0:0] branch_prediction_failed;
wire [0:0] flush_pipeline; // flush pipeline when branch prediction fails
wire [7:0] instr_address_not_taken_alu_fe;
wire [7:0] instr_address_not_taken_fe_de;
wire [7:0] instr_address_not_taken_de_cu;
wire [7:0] instr_address_not_taken_cu_alu;
wire [7:0] branch_instr_address_alu_fe;
wire [7:0] branch_instr_address_fe_de;
wire [7:0] branch_instr_address_de_cu;
wire [7:0] branch_instr_address_cu_alu;
wire branch_prediction_result_alu_fe;
wire branch_prediction_result_fe_de;
wire branch_prediction_result_de_cu;
wire branch_prediction_result_cu_alu;
wire is_conditional_branch_alu_fe;
wire branch_taken_alu_fe;
wire instr_valid;
wire dec_ready;
wire exec_ready; // connects CU and Fetch

// 新增译码信号
wire [2:0] opcode;
wire [4:0] rs1, rs2, rd;

// 实例化所有模块
fetch u_fetch (
    .clk(clk),
    .rst(rst),
    .imem_addr(imem_addr),
    .imem_data(imem_data),
    .instr(instr),
    .instr_valid(instr_valid),
    .dec_ready(dec_ready),
    .exec_ready(exec_ready),
    .flush_pipeline(flush_pipeline),
    .branch_prediction_failed(branch_prediction_failed),
    .instr_address_not_taken_alu_fe(instr_address_not_taken_alu_fe),
    .instr_address_not_taken(instr_address_not_taken_fe_de),
    .branch_instr_address(branch_instr_address_fe_de),
    .branch_prediction_result(branch_prediction_result_fe_de),
    .branch_instr_address_alu_fe(branch_instr_address_alu_fe),
    .is_conditional_branch_alu_fe(is_conditional_branch_alu_fe),
    .branch_taken_in(branch_taken_alu_fe)
);

instr_mem u_mem (
    .addr(imem_addr),
    .data_out(imem_data)
);

idecode u_decode (
    .clk(clk),
    .rst(rst),
    .instr(instr),
    .instr_valid(instr_valid),
    .dec_ready(dec_ready),
    .opcode(opcode),
    .instr_out(instr_idecode_cu),
    .rs1(rs1),
    .rs2(rs2),
    .rd(rd),
    .micro_code_addr_out(micro_code_addr_de_cu),
    .micro_code_cnt_out(micro_code_cnt_de_cu),
    .flush_pipeline(flush_pipeline),
    .instr_address_not_taken_fe_de(instr_address_not_taken_fe_de),
    .instr_address_not_taken_de_cu(instr_address_not_taken_de_cu),
    .branch_instr_address_fe_de(branch_instr_address_fe_de),
    .branch_instr_address_de_cu(branch_instr_address_de_cu),
    .branch_prediction_result_fe_de(branch_prediction_result_fe_de),
    .branch_prediction_result_de_cu(branch_prediction_result_de_cu)
);


cu u_cu(
    .clk(clk),
    .rst(rst),
    .micro_code_addr_in(micro_code_addr_de_cu),
    .micro_code_cnt_in(micro_code_cnt_de_cu),
    .instr_cu_in(instr_idecode_cu),
    .micro_code_addr_out(micro_code_addr_cu_alu),
    .o_exec_ready(exec_ready),
    .instr_cu_out(instr_cu_alu),
    .flush_pipeline(flush_pipeline),
    .instr_address_not_taken_de_cu(instr_address_not_taken_de_cu),
    .instr_address_not_taken_cu_alu(instr_address_not_taken_cu_alu),
    .branch_instr_address_de_cu(branch_instr_address_de_cu),
    .branch_instr_address_cu_alu(branch_instr_address_cu_alu),
    .branch_prediction_result_de_cu(branch_prediction_result_de_cu),
    .branch_prediction_result_cu_alu(branch_prediction_result_cu_alu)
);

register_file u_register_file(
    .clk(clk),
    .reg_addr_1(register_file_addr_1),
    .reg_addr_2(register_file_addr_2),
    .data_out_1(register_data_out_1),
    .data_out_2(register_data_out_2),
    .write_en(write_en_regfile),
    .reg_addr_in(register_file_addr_dest),
    .data_in(alu_result),
    .mem_test(mem_regfile_test)
);


micro_instr_mem u_micro_instr_mem(
    .micro_code_addr_in(micro_code_addr_cu_alu),
    .micro_code_data_out(micro_code)
);

alu u_alu(
    .clk(clk),
    .instruction(instr_cu_alu),
    .micro_code(micro_code),
    .alu_regfile_in_1(register_data_out_1),
    .alu_regfile_in_2(register_data_out_2),
    .alu_memory_in(data_memory_alu),
    .alu_result(alu_result),
    .alu_regfile_address_out_1(register_file_addr_1),
    .alu_regfile_address_out_2(register_file_addr_2),
    .alu_memory_address_out(address_memory_alu),
    .alu_memory_write_en_out(write_en_memory),
    .alu_regfile_write_en_out(write_en_regfile),
    .alu_regfile_address_out(register_file_addr_dest),
    .flush_pipeline_out(branch_prediction_failed),
    .instr_address_not_taken_alu_fe(instr_address_not_taken_alu_fe),
    .instr_address_not_taken_cu_alu(instr_address_not_taken_cu_alu),
    .branch_instr_address_alu_fe(branch_instr_address_alu_fe),
    .branch_instr_address_cu_alu(branch_instr_address_cu_alu),
    .branch_prediction_result_cu_alu(branch_prediction_result_cu_alu),
    .is_conditional_branch_alu_fe(is_conditional_branch_alu_fe),
    .branch_taken_alu_fe(branch_taken_alu_fe)
);

external_mem u_external_mem(
    .clk(clk),
    .micro_code(micro_code),
    .addr(address_memory_alu),
    .data_in(alu_result),
    .data_out(data_memory_alu),
    .data_test(mem_external_test)
);

always #5 clk = ~clk;

initial begin
clk = 0;
rst = 1;
#10 rst = 0;


// // instructions initial values
// u_mem.mem[0] = 32'b0000_0001_0000_0000_0000_0001_0000_0000; // 0100add register 0 and register 1 to produce alu result
// // u_mem.mem[1] = 32'b0000_0001_0000_0001_0000_0010_0000_0000;  // reg[1] + reg[2]
// u_mem.mem[1] = 32'b0000_0001_0000_0000_0000_0000_0000_0000;  // reg[1] + reg[2]
// u_mem.mem[2] = 32'b0000_0001_0000_0010_0000_0011_0000_0000;
// //u_mem.mem[2] = 32'b0001_0001_0000_0010_0000_0011_0000_0000; // add memory[2] and register[3]
// u_mem.mem[3] = 32'b1000_0000_0000_1000_0000_0000_0000_0000; // load from memory[8](0xF) to reg[0]                    
// u_mem.mem[4] = 32'b0000_0001_0000_0011_0000_0000_0000_0000; // reg[3] + reg[0] (reg[0]=0xF+3=0x14)
// u_mem.mem[5] = 32'b1000_0001_0000_0000_0000_0000_0000_0000;  // store reg[0] to memory[0]  (expected: memory[0]=0x14)

// // u_mem.mem[4] = 32'b0000_0001_0000_0100_0000_0101_0000_0000; // reg[4] + reg[5]
// // u_mem.mem[4] = 32'b0100_0000_0001_0000_0000_0000_0000_0000; // jump to instruction 8
// u_mem.mem[6] = 32'b0110_0000_0000_0011_0000_0011_0001_0100; // jump to instruction 8 if equal// 60030010
// // u_mem.mem[5] = 32'b0000_0001_0000_0101_0000_0100_0000_0000; // reg[5] + reg[4]
// u_mem.mem[7] = 32'b1000_0001_0000_1111_0000_0000_0000_0000;  // store reg[15] to memory[0]
// u_mem.mem[8] = 32'b0000_0001_0000_0110_0000_0101_0000_0000; // reg[6] + reg[5]
// u_mem.mem[9] = 32'b0000_0001_0000_0111_0000_0110_0000_0000; // reg[7] + reg[6]  // 01070600
// u_mem.mem[10] = 32'b0000_0001_0000_1000_0000_0111_0000_0000; // reg[8] + reg[7]
// expected results: 3, 5, 37(0x25), 9, 11(0xB), 13(0xD)

// instruction initial values (test repetitive jump instructions)
u_mem.mem[0] = 32'b1000_0000_0000_1000_0000_0000_0000_0000; // load from memory[8](0xF) to reg[0] reg[0] = 0xF
u_mem.mem[1] = 32'b0000_0001_0000_0000_0000_0001_0000_0000; // reg[0] <= reg[0] + reg[1]  reg[0] = 2+0xF = 0x11
u_mem.mem[2] = 32'b0000_0001_0000_0000_0000_0010_0000_0000; // reg[0] <= reg[0] + reg[2]  reg[0] = 0x11+3 = 0x14
u_mem.mem[3] = 32'b0100_0000_0001_0000_0000_0000_0000_0000; // jump to instruction 8 (unconditional jump)
u_mem.mem[4] = 32'b0000_0001_0000_0000_0000_0001_0000_0000; // reg[0] <= reg[0] + reg[1]
u_mem.mem[5] = 32'b0000_0001_0000_0000_0000_0010_0000_0000; // reg[0] <= reg[0] + reg[2]    
u_mem.mem[6] = 32'b0000_0001_0000_0000_0000_0001_0000_0000; // reg[0] <= reg[0] + reg[1]
u_mem.mem[7] = 32'b0000_0001_0000_0000_0000_0010_0000_0000; // reg[0] <= reg[0] + reg[2]
u_mem.mem[8] = 32'b1000_0001_0000_0000_0000_0000_0000_0000; // reg[0] => memory[0] (store)  memory[0] = 0x14
u_mem.mem[9] = 32'b0110_0000_0000_0011_0000_0011_0000_0100; // jump to instruction 2 if equal  
u_mem.mem[10] = 32'b0000_0001_0000_0000_0000_0001_0000_0000; // reg[0] <= reg[0] + reg[1]
u_mem.mem[11] = 32'b0000_0001_0000_0000_0000_0010_0000_0000; 
u_mem.mem[12] = 32'b0000_0001_0000_0000_0000_0001_0000_0000; // reg[0] <= reg[0] + reg[1]
u_mem.mem[13] = 32'b0000_0001_0000_0000_0000_0010_0000_0000; 


// external memory initial values
u_external_mem.mem[0] = 16'b0000_0001;
u_external_mem.mem[1] = 16'b0001_0010;
u_external_mem.mem[2] = 16'b0010_0000;
u_external_mem.mem[3] = 16'b0000_0100;
u_external_mem.mem[4] = 16'b0000_0101;
u_external_mem.mem[5] = 16'b0000_0110;
u_external_mem.mem[6] = 16'b0000_0111;
u_external_mem.mem[7] = 16'b0000_1000;
u_external_mem.mem[8] = 16'b0000_1111;
u_external_mem.mem[9] = 16'b0000_1010;  
u_external_mem.mem[10] = 16'b0000_1011;


// register file initial values
u_register_file.mem[0] = 16'b0000_0000_0000_0001;
u_register_file.mem[1] = 16'b0000_0000_0000_0010;
u_register_file.mem[2] = 16'b0000_0000_0000_0011;
// u_register_file.mem[3] = 16'b0000_0000_0000_0100;
u_register_file.mem[3] = 16'b0000_0000_0000_0101;
u_register_file.mem[4] = 16'b0000_0000_0000_0110;
u_register_file.mem[5] = 16'b0000_0000_0000_0111;
u_register_file.mem[6] = 16'b0000_0000_0000_1000;
u_register_file.mem[7] = 16'b0000_0000_0000_1001;
u_register_file.mem[8] = 16'b0000_0000_0000_1010;
u_register_file.mem[9] = 16'b0000_0000_0000_1011;
u_register_file.mem[10] = 16'b0000_0000_0000_1100;
u_register_file.mem[11] = 16'b0000_0000_0000_1101;
u_register_file.mem[12] = 16'b0000_0000_0000_1110;
u_register_file.mem[13] = 16'b0000_0000_0000_1111;
u_register_file.mem[14] = 16'b0000_0000_0001_0000;
u_register_file.mem[15] = 16'b0000_0000_0001_0001;
u_register_file.mem[16] = 16'b0000_0000_0001_0010;
u_register_file.mem[17] = 16'b0000_0000_0001_0011;

// micro instruction initial values
// micro instruction format:
// [15:12]  operation completed (e.g. add, sub)
// [11]  MAR <- IR[23:16]  // fetching operand 1 in memory
// [10]  MAR <- IR[15:8]  // fetching operand 2 in memory
// [9]   alu_in_1 <- MBR // fetching operand 1 in memory
// [8]   alu_in_2 <- MBR //  fetching operand 2 in memory
// [7]   alu_in_1 <- alu_regfile_out_1  // fetching operand 1 in register file
// [6]   alu_in_2 <- alu_regfile_out_2  // fetching operand 2 in register file
// [5]   alu_in_2 <- IR[7:0]   // one of the source operands is an immediate number in IR (used in jump/branch or instructions with imm)
// [4]   MAR <- IR[15:0] // used in load and store
// [3]   memory <- MBR
//// [2]   alu_regfile_out_1 <- alu_result
// [2]   MBR <- alu_result
// [1]   memory write enable
// [0]   register file write enable

// Source operand is in register file , destination operand is in register file
u_micro_instr_mem.mem[0] = 16'b0001_0000_1100_0001; // add rd, rs1, rs2
u_micro_instr_mem.mem[1] = 16'b0010_0000_1100_0000; // sub
u_micro_instr_mem.mem[2] = 16'b0011_0000_1100_0000; // slt
u_micro_instr_mem.mem[3] = 16'b0100_0000_1100_0000; // and
u_micro_instr_mem.mem[4] = 16'b0101_0000_1100_0000; // or
u_micro_instr_mem.mem[5] = 16'b0110_0000_1100_0000; // xor
u_micro_instr_mem.mem[6] = 16'b0111_0000_1100_0000; // sll
u_micro_instr_mem.mem[7] = 16'b1000_0000_1100_0000; // srl



// One of the source operand is in memory, destination operand is in register file
// add rd, [memory address], rs2
u_micro_instr_mem.mem[8] = 16'b0000_1000_0001_0001; // MAR <- IR[23:16]  // fetching operand 1 in memory (transferring address to MAR)
u_micro_instr_mem.mem[9] = 16'b0000_0000_0000_1001; // MBR <- memory[MAR](MBR) // fetching operand 1 in memory (transferring data to MBR)
u_micro_instr_mem.mem[10] = 16'b0001_0010_0100_0001; // add rd, MBR, rs2

u_micro_instr_mem.mem[11] = 16'b0000_1000_0001_0001; // MAR <- IR[23:16]  // fetching operand 1 in memory (transferring address to MAR)
u_micro_instr_mem.mem[12] = 16'b0000_0000_0000_1001; // MBR <- memory[MAR](MBR) // fetching operand 1 in memory (transferring data to MBR)
u_micro_instr_mem.mem[13] = 16'b0010_0010_0100_0001; // sub rd, MBR, rs2

u_micro_instr_mem.mem[14] = 16'b0000_1000_0001_0001; // MAR <- IR[23:16]  // fetching operand 1 in memory (transferring address to MAR)
u_micro_instr_mem.mem[15] = 16'b0000_0000_0000_1001; // MBR <- memory[MAR](MBR) // fetching operand 1 in memory (transferring data to MBR)
u_micro_instr_mem.mem[16] = 16'b0011_0010_0100_0001; // slt rd, MBR, rs2

u_micro_instr_mem.mem[17] = 16'b0000_1000_0001_0001; // MAR <- IR[23:16]  // fetching operand 1 in memory (transferring address to MAR)
u_micro_instr_mem.mem[18] = 16'b0000_0000_0000_1001; // MBR <- memory[MAR](MBR) // fetching operand 1 in memory (transferring data to MBR)
u_micro_instr_mem.mem[19] = 16'b0100_0010_0100_0001; // and rd, MBR, rs2

u_micro_instr_mem.mem[20] = 16'b0000_1000_0001_0001; // MAR <- IR[23:16]  // fetching operand 1 in memory (transferring address to MAR)
u_micro_instr_mem.mem[21] = 16'b0000_0000_0000_1001; // MBR <- memory[MAR](MBR) // fetching operand 1 in memory (transferring data to MBR)
u_micro_instr_mem.mem[22] = 16'b0101_0010_0100_0001; // or rd, MBR, rs2

u_micro_instr_mem.mem[23] = 16'b0000_1000_0001_0001; // MAR <- IR[23:16]  // fetching operand 1 in memory (transferring address to MAR)
u_micro_instr_mem.mem[24] = 16'b0000_0000_0000_1001; // MBR <- memory[MAR](MBR) // fetching operand 1 in memory (transferring data to MBR)
u_micro_instr_mem.mem[25] = 16'b0110_0010_0100_0001; // xor rd, MBR, rs2

u_micro_instr_mem.mem[26] = 16'b0000_1000_0001_0001; // MAR <- IR[23:16]  // fetching operand 1 in memory (transferring address to MAR)
u_micro_instr_mem.mem[27] = 16'b0000_0000_0000_1001; // MBR <- memory[MAR](MBR) // fetching operand 1 in memory (transferring data to MBR)
u_micro_instr_mem.mem[28] = 16'b0111_0010_0100_0001; // sll rd, MBR, rs2


// Load and store instructions
// load [memory address], rd [31:24] opcode ; [23:16] memory address ; [7:0] rd
// store rs, [memory address] [31:24] opcode ; [23:16] rs ; [15:8] memory address

// load rd, [memory address] (consumes 3 clock cycles, 1 extra cycle to write to register file)
u_micro_instr_mem.mem[29] = 16'b0000_1000_0001_0000; // MAR <- IR[23:16]  // fetching operand 1 in memory (transferring address to MAR)
u_micro_instr_mem.mem[30] = 16'b0000_0000_0000_1000; // MBR <- memory[MAR](MBR) // fetching operand 1 in memory (transferring data to MBR)
u_micro_instr_mem.mem[31] = 16'b0000_0010_0000_0001; // rd <- MBR  // fetching operand 2 in memory (transferring address to MAR) // 0000 means no-op
// 时钟生成（周期10ns）

// store
u_micro_instr_mem.mem[32] = 16'b0000_0100_1001_0100; // in parallel: MAR <- IR[15:8]; alu_result <- rs1 ; MBR <- alu_result ;
// u_micro_instr_mem.mem[33] = 16'b0000_0000_0000_0100; // MBR <- alu_result
u_micro_instr_mem.mem[33] = 16'b0000_0000_0000_0010; // memory write enable (writing MBR to memory)


// unconditional branch: jal, target ; [31:24] opcode ; [23:16] target
u_micro_instr_mem.mem[34] = 16'b0000_0000_0000_0000; // NO-OP

// conditional branch: beq
u_micro_instr_mem.mem[36] = 16'b1100_0000_1100_0000; // judge whether rs1 and rs2 is equal

// NO-OP for flushing pipeline
u_micro_instr_mem.mem[255] = 16'b0000_0000_0000_0000; // NO-OP
end

// 波形记录（支持iverilog）
initial begin
    $dumpfile("wave.vcd");
    $dumpvars(0, tb);
    #2000
    $finish;
end


endmodule

// u_micro_instr_mem.mem[0] = 16'b0000_0000_0000_0001;    
// u_micro_instr_mem.mem[1] = 16'b1111_0000_0000_0010;
// u_micro_instr_mem.mem[2] = 16'b0000_0000_0000_0011;
// u_micro_instr_mem.mem[3] = 16'b1111_0000_0000_0010;
// u_micro_instr_mem.mem[4] = 16'b0000_0000_0000_0011;
// u_micro_instr_mem.mem[5] = 16'b1111_0000_0000_0010;
// u_micro_instr_mem.mem[6] = 16'b0000_0000_0000_0001;
// u_micro_instr_mem.mem[7] = 16'b1111_0000_0000_0010;
// u_micro_instr_mem.mem[8] = 16'b0000_0000_0000_0011;
// u_micro_instr_mem.mem[9] = 16'b1111_0000_0000_0010;
// u_micro_instr_mem.mem[10] = 16'b0000_0000_0000_0011;
// u_micro_instr_mem.mem[11] = 16'b1111_0000_0000_0010;

