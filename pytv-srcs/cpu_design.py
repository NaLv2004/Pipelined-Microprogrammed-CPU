import pytv
from pytv.Converter import convert
from pytv.ModuleLoader import moduleloader
import sys
from os.path import dirname, abspath
import math

sys.path.append(dirname(dirname(__file__)))
sys.path.append(dirname(__file__))
# from PyTU import QuMode, OfMode, QuType

class cpu_specifications:  
    def __init__(self):
        self.instruction_data_width = 32
        self.instruction_addr_width = 8
        self.external_mem_data_width = 16
        self.external_mem_addr_width = 8
        self.external_mem_depth = 256
        self.register_file_data_width = 16
        self.register_file_data_width = 8
        self.register_file_depth = 256
        self.micro_instruction_data_width = 32
        self.micro_instruction_addr_width = 8
        self.branch_prediction_table_depth = 8
        self.branch_prediction_table_addr_width = math.ceil(math.log2(self.branch_prediction_table_depth))
        self.branch_prediction_table_data_width = 11
        self.micro_instruction_cnt_width = 3
        self.alu_result_width = 16
        self.branch_prediction_enable = True
        self.out_of_order_execution_enable = True
        self.fetch_idecode_interface = dict()
        self.fetch_idecode_interface_width = 0
        self.alu_fetch_interface = dict()
        self.alu_fetch_interface_width = 0
        self.cu_alu_interface = dict()
        self.cu_alu_interface_width = 0
        self.idecode_cu_interface = dict()
        self.idecode_cu_interface_width = 0
    
    
        
        
    def allocate_interface(self, interface, interface_name):
        interface_ports = interface.keys()
        port_start_bit = 0
        if interface_name == 'fetch_idecode':
            for port in interface_ports:
                port_width = interface[port]
                port_end_bit = port_start_bit + port_width -1
                self.fetch_idecode_interface[port] = []
                self.fetch_idecode_interface[port][0] = port_start_bit  
                self.fetch_idecode_interface[port][1] = port_end_bit
                port_start_bit = port_end_bit + 1
                self.fetch_idecode_interface_width += port_width
        if interface_name == 'alu_fetch':
            for port in interface_ports:
                port_width = interface[port]
                port_end_bit = port_start_bit + port_width -1
                self.alu_fetch_interface[port] = []
                self.alu_fetch_interface[port][0] = port_start_bit  
                self.alu_fetch_interface[port][1] = port_end_bit
                port_start_bit = port_end_bit + 1
                self.alu_fetch_interface_width += port_width
        if interface_name == 'cu_alu':
            for port in interface_ports:
                port_width = interface[port]
                self.cu_alu_interface[port] = []
                port_end_bit = port_start_bit + port_width -1
                self.cu_alu_interface[port][0] = port_start_bit  
                self.cu_alu_interface[port][1] = port_end_bit
                port_start_bit = port_end_bit + 1
                self.cu_alu_interface_width += port_width
        if interface_name == 'idecode_cu':
            for port in interface_ports:
                port_width = interface[port]
                self.idecode_cu_interface[port] = []
                port_end_bit = port_start_bit + port_width -1
                self.idecode_cu_interface[port][0] = port_start_bit  
                self.idecode_cu_interface[port][1] = port_end_bit
                port_start_bit = port_end_bit + 1
                self.idecode_cu_interface_width += port_width

        
        
        
        

my_cpu_spec = cpu_specifications()

fetch_idecode_interface = dict()
fetch_idecode_interface['instr_valid'] = 1
fetch_idecode_interface['instr_address_not_taken'] = my_cpu_spec.instruction_addr_width
fetch_idecode_interface['branch_instr_address'] = my_cpu_spec.instruction_addr_width
fetch_idecode_interface['branch_prediction_result'] = 1
fetch_idecode_interface['instr'] = my_cpu_spec.instruction_data_width


alu_fetch_interface = dict()
alu_fetch_interface['branch_prediction_failed'] = 1
alu_fetch_interface['branch_instr_address_alu_fe'] = my_cpu_spec.instruction_addr_width
alu_fetch_interface['instr_address_not_taken_alu_fe'] = my_cpu_spec.instruction_addr_width
alu_fetch_interface['is_conditional_branch_alu_fe'] = 1
alu_fetch_interface['branch_taken_in'] = 1


idecode_cu_interface = dict()
idecode_cu_interface['instr_out'] = my_cpu_spec.instruction_data_width
idecode_cu_interface['micro_code_addr_out'] = my_cpu_spec.micro_instruction_addr_width
idecode_cu_interface['micro_code_cnt_out'] = my_cpu_spec.micro_instruction_cnt_width
idecode_cu_interface['micro_code'] = my_cpu_spec.micro_instruction_data_width
idecode_cu_interface['instr_address_not_taken_de_cu'] = my_cpu_spec.instruction_addr_width
idecode_cu_interface['branch_instr_address_de_cu'] = my_cpu_spec.instruction_addr_width
idecode_cu_interface['branch_prediction_result_de_cu'] = 1

cu_alu_interface = dict()
cu_alu_interface['micro_code_addr_out'] = my_cpu_spec.micro_instruction_addr_width
cu_alu_interface['micro_code_out'] = my_cpu_spec.micro_instruction_data_width
cu_alu_interface['micro_code_addr_speculative_fetch'] =  my_cpu_spec.micro_instruction_addr_width
cu_alu_interface['micro_code_speculative_fetch'] = my_cpu_spec.micro_instruction_data_width
cu_alu_interface['instr_cu_out'] = my_cpu_spec.instruction_data_width
cu_alu_interface['instr_address_not_taken_cu_alu'] = my_cpu_spec.instruction_addr_width
cu_alu_interface['branch_instr_address_cu_alu'] = my_cpu_spec.instruction_addr_width
cu_alu_interface['branch_prediction_result_cu_alu'] = 1


# allocate interface for fetch and idecode
my_cpu_spec.allocate_interface(fetch_idecode_interface, 'fetch_idecode')
my_cpu_spec.allocate_interface(alu_fetch_interface, 'alu_fetch')
my_cpu_spec.allocate_interface(idecode_cu_interface, 'idecode_cu')
my_cpu_spec.allocate_interface(cu_alu_interface, 'cu_alu')



@convert 
def ModuleMiniDecode(cpu_spec):
    #/ module MiniDecode(
    #/     input  [`cpu_spec.instruction_data_width-1`:0] instr,
    #/     output is_unconditional_branch,
    #/     output is_conditional_branch,
    #/ );
    #/ assign is_unconditional_branch = (instr[31:28]==4'b0100) ? 1'b1 : 1'b0;
    #/ assign is_conditional_branch = (instr[31:28]==4'b0110) ? 1'b1 : 1'b0;
    #/ endmodule
    pass
  
    
@convert
def ModuleOneBitBranchPredictor(cpu_spec):
    #/ module OneBitBranchPredictor(
    #/     input clk,
    #/     input rst,
    #/     input [`cpu_spec.instruction_addr_width-1`:0] instr_address_fe,
    #/     input [`cpu_spec.instruction_addr_width-1`:0] intr_address_alu,
    #/     input branch_taken_in,
    #/     input is_conditional_branch_fe,
    #/     input is_conditional_branch_alu,
    #/     output branch_taken_out,
    #/     output [`cpu_spec.branch_prediction_table_depth-1`:0] mem_one_bit_predictor_test
    #/     );
    #/ wire [`cpu_spec.instruction_addr_width-1`:0] instr_address_fe;
    #/ wire [`cpu_spec.instruction_addr_width-1`:0] intr_address_alu;
    #/ reg [`cpu_spec.branch_prediction_table_data_width-1`:0] counters_and_address [`cpu_spec.branch_prediction_table_depth-1`:0];
    for i in range (0, cpu_spec.branch_prediction_table_depth):
        #/ assign mem_one_bit_predictor_test[`i`] = counters_and_address[`i`][`cpu_spec.branch_prediction_table_data_width-1`];
        pass
    #/ wire [`cpu_spec.branch_prediction_table_addr_width-1`:0] idx_slot_fe;
    #/ wire  slot_hit_fe;
    #/ wire  slot_not_occupied_fe;
    #/ assign idx_slot_fe = instr_address_fe[`cpu_spec.branch_prediction_table_addr_width-1`:0];
    #/ assign slot_hit_fe = (slot_not_occupied_fe) ? 1'b0 :
    #/                      (counters_and_address[idx_slot_fe][`cpu_spec.instruction_addr_width-1`:0]==instr_address_fe[`cpu_spec.instruction_addr_width-1`:0]) ?
    #/                      1'b1 : 1'b0;
    #/ assign slot_not_occupied_fe = (counters_and_address[idx_slot_fe][`cpu_spec.instruction_addr_width`:`cpu_spec.instruction_addr_width`]==1'b0) ? 1'b1 : 1'b0;
    #/ 
    #/ wire [`cpu_spec.branch_prediction_table_addr_width-1`:0] idx_slot_alu;
    #/ wire  slot_hit_alu;
    #/ wire  slot_not_occupied_alu;
    #/ wire  slot_occupied_alu;
    #/ assign idx_slot_alu = intr_address_alu[`cpu_spec.branch_prediction_table_addr_width-1`:0];
    #/ assign slot_hit_alu = (counters_and_address[idx_slot_alu][`cpu_spec.instruction_addr_width-1`:0]==intr_address_alu[`cpu_spec.instruction_addr_width-1`:0]) ?
    #/                      1'b1 : 1'b0;
    #/ assign slot_not_occupied_alu = (counters_and_address[idx_slot_alu][`cpu_spec.instruction_addr_width`:`cpu_spec.instruction_addr_width`]==1'b0) ? 1'b1 : 1'b0;
    #/ assign slot_occupied_alu = ! slot_not_occupied_alu;
    #/ 
    #/ // output logic: 
    #/ assign branch_taken_out = (slot_hit_fe) ? counters_and_address[idx_slot_fe][`cpu_spec.branch_prediction_table_data_width-1`:`cpu_spec.branch_prediction_table_data_width-1`] : 1'b0;
    #/ 
    #/ always @(posedge clk or posedge rst) begin
    #/     if (rst) begin
    for i in range (0, cpu_spec.branch_prediction_table_depth):
        #/         counters_and_address [`i`] <= 11'b000_0000_0000;
        pass
    #/     end else begin
    #/         if (is_conditional_branch_fe) begin
    #/             if (slot_not_occupied_fe) begin
    #/                 counters_and_address [idx_slot_fe] [`cpu_spec.instruction_addr_width-1`:0] <= instr_address_fe[`cpu_spec.instruction_addr_width-1`:0];
    #/                 counters_and_address [idx_slot_fe] [`cpu_spec.instruction_addr_width`:`cpu_spec.instruction_addr_width`] <= 1'b1; 
    #/                 counters_and_address [idx_slot_fe] [`cpu_spec.branch_prediction_table_data_width-1`:`cpu_spec.branch_prediction_table_data_width-1`] <= 1'b0; // or branch taken ?
    #/             end else begin
    #/                 if (slot_hit_fe) begin
    #/                     counters_and_address [idx_slot_fe] [`cpu_spec.branch_prediction_table_data_width-1`:`cpu_spec.branch_prediction_table_data_width-1`] <= counters_and_address [idx_slot_fe] [`cpu_spec.branch_prediction_table_data_width-1`:`cpu_spec.branch_prediction_table_data_width-1`] ;
    #/                 end else begin
    #/                     // if slot hit fails, drive the current slot with the new address and reset the counter
    #/                     counters_and_address [idx_slot_fe] [`cpu_spec.instruction_addr_width-1`:0] <= instr_address_fe[`cpu_spec.instruction_addr_width-1`:0];
    #/                     counters_and_address [idx_slot_fe] [`cpu_spec.instruction_addr_width`:`cpu_spec.instruction_addr_width`] <= 1'b1; 
    #/                     counters_and_address [idx_slot_fe] [`cpu_spec.branch_prediction_table_data_width-1`:`cpu_spec.branch_prediction_table_data_width-1`] <= 1'b0; // or branch_taken_in ?
    #/                 end
    #/             end
    #/         end 
    #/         if (is_conditional_branch_alu) begin
    #/             if (slot_occupied_alu) begin
    #/                 if (slot_hit_alu) begin
    #/                     counters_and_address [idx_slot_alu] [`cpu_spec.branch_prediction_table_data_width-1`:`cpu_spec.branch_prediction_table_data_width-1`] <= branch_taken_in;
    #/                 end
    #/             end
    #/         end
    #/     end
    #/ end
    #/ endmodule

   
   
    
      
@convert 
def ModuleJudgeNotConflictSpeculativeFetch(cpu_spec):
    #/ module JudgeNotConflictSpeculativeFetch(
    #/     input [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_normal,
    #/     input [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_speculative,
    #/     input [`cpu_spec.instruction_data_width-1`:0] instruction_normal,
    #/     input [`cpu_spec.instruction_data_width-1`:0] instruction_speculative,
    #/     output is_micro_code_not_conflict
    #/     );
    #/ endmodule
    pass
    
@ convert
def ModuleAdder(cpu_spec):
    #/ module Adder(
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_1,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_2,
    #/     output [`cpu_spec.register_file_data_width-1`:0] result
    #/     );
    #/ wire [`cpu_spec.register_file_data_width-1`:0] result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_1;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_2;
    #/ assign result = op_1 + op_2;
    #/ endmodule
    pass
    
    
@ convert
def ModuleSubstractor(cpu_spec):
    #/ module Substractor(
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_1,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_2,
    #/     output [`cpu_spec.register_file_data_width-1`:0] result
    #/     );
    #/ wire [`cpu_spec.register_file_data_width-1`:0] result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_1;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_2;
    #/ assign result = op_1 - op_2;
    #/ endmodule
    pass
    
    
@ convert
def ModuleXorer(cpu_spec):
    #/ module Xorer(
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_1,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_2,
    #/     output [`cpu_spec.register_file_data_width-1`:0] result
    #/     );
    #/ wire [`cpu_spec.register_file_data_width-1`:0] result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_1;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_2;
    #/ assign result = op_1 ^ op_2;
    #/ endmodule
    pass
    
    
@ convert
def ModuleAnder(cpu_spec):
    #/ module Ander(
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_1,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_2,
    #/     output [`cpu_spec.register_file_data_width-1`:0] result
    #/     );
    #/ wire [`cpu_spec.register_file_data_width-1`:0] result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_1;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_2;
    #/ assign result = op_1 & op_2;
    #/ endmodule
    pass
    
    
    
@ convert
def ModuleOrer(cpu_spec):
    #/ module Orer(
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_1,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_2,
    #/     output [`cpu_spec.register_file_data_width-1`:0] result
    #/     );
    #/ wire [`cpu_spec.register_file_data_width-1`:0] result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_1;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_2;
    #/ assign result = op_1 | op_2;
    #/ endmodule
    pass
    

@ convert 
def ModuleJudgeEqual(cpu_spec):
    #/ module JudgeEqual(
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_1,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] op_2,
    #/     output result
    #/     );
    #/ wire result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_1;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] op_2;
    #/ assign result = (op_1 == op_2);
    #/ endmodule
    pass
    
    

@ convert 
def ModuleInstrMem(cpu_spec):
    #/ module InstrMem(
    #/     input [`cpu_spec.instruction_addr_width-1`:0] addr,
    #/     output [`cpu_spec.instruction_data_width-1`:0] data_out
    #/ );
    #/ reg [`cpu_spec.instruction_data_width-1`:0] mem [`cpu_spec.external_mem_depth-1`:0];
    #/ 
    #/ endmodule
    pass
    
    
@ convert
def ModuleMicroInstrMem(cpu_spec):
    #/ module MicroInstrMem(
    #/        input [`cpu_spec.micro_instruction_addr_width-1`] micro_code_addr_in,
    #/        output [`cpu_spec.micro_instruction_data_width-1`] micro_code_data_out
    #/        input [`cpu_spec.micro_instruction_addr_width-1`] micro_code_addr_speculative_fetch_in,
    #/        output [`cpu_spec.micro_instruction_data_width-1`] micro_code_data_speculative_fetch_out
    #/        );
    #/ reg [`cpu_spec.micro_instruction_data_width-1`:0] mem [`cpu_spec.micro_instruction_depth-1`:0];
    #/ assign micro_code_data_out = mem[micro_code_addr_in];
    #/ assign micro_code_data_speculative_fetch_out = mem[micro_code_addr_speculative_fetch_in];
    #/ endmodule
    pass
    


@ convert
def ModuleExternalMem(cpu_spec):
    #/ module ExternalMem(
    #/     input clk;
    #/     input [`cpu_spec.micro_instruction_data_width-1`:0] micro_code,
    #/     input [`cpu_spec.external_mem_addr_width-1`:0] addr,
    #/     input [`cpu_spec.external_mem_data_width-1`:0] data_in,
    #/     output [`cpu_spec.external_mem_data_width-1`:0] data_out,
    #/     output [`cpu_spec.external_mem_data_width-1`:0] data_test
    #/     );
    #/ reg [`cpu_spec.external_mem_data_width-1`:0] mem [`cpu_spec.external_mem_depth-1`:0];
    #/ reg [`cpu_spec.external_mem_addr_width-1`:0] MAR;
    #/ reg [`cpu_spec.external_mem_data_width-1`:0] MBR;
    #/ wire [`cpu_spec.external_mem_data_width-1`:0] data_out_instant;
    #/ wire [`cpu_spec.external_mem_data_width-1`:0] read_en;
    #/ assign data_out = MBR;
    #/ assign data_test = mem[0];
    #/ 
    #/ 
    #/ always @(posedge clk)
    #/ begin
    #/     case (micro_code[4:4])
    #/         1'b1: MAR <= addr;
    #/     endcase
    #/ end
    #/ 
    #/ always @(posedge clk)
    #/ begin
    #/     case (micro_code[3:3])
    #/         1'b1: MBR <= mem[MAR];
    #/     endcase
    #/     case (micro_code[2:2])
    #/         1'b1: MBR <= data_in;
    #/     endcase
    #/     case (micro_code[1:1])
    #/         1'b1: mem[MAR] <= MBR;
    #/     endcase
    #/ end
    #/ endmodule
    pass

  
    
# reg [15:0] pc;
# reg [31:0] instruction_reg;
# reg        valid_reg;
# reg [7:0]  branch_target_buffer; // target instruction address if the branch is taken
# reg [7:0]  pc_delayed;
# reg [0:0]  branch_prediction_failed_buffer; // branch prediction failed flag
# wire [7:0] branch_target_address_wire;
# wire [7:0] instr_address_not_taken;
# wire [7:0] instr_address_not_taken_alu_fe;
# wire branch_taken_one_bit_predict;
# wire branch_prediction_result_in_fe;
# reg branch_prediction_result_reg;
# assign instr_address_not_taken = branch_target_buffer;

# wire [7:0] curr_instr_address;
# assign curr_instr_address = pc[7:0];

# // instruction mini-decode: decide whether the instruction is a branch instruction
# wire is_conditional_branch;
# wire is_unconditional_branch;
# i_mini_decode u_i_mini_decode (.instr(imem_data),
#                                .is_unconditional_branch(is_unconditional_branch),
#                                .is_conditional_branch(is_conditional_branch));


# // branch predictor
# wire [15:0] branch_predict;
# assign branch_predict = (is_unconditional_branch)? imem_data[23:16]:
#                         (is_conditional_branch && branch_taken_one_bit_predict)? imem_data[7:0]:
#                         (pc+16'h2);
# assign branch_target_address_wire = (is_conditional_branch)? imem_data[7:0] : branch_target_buffer;
# assign flush_pipeline = branch_prediction_failed;

# assign branch_instr_address = pc_delayed;
# assign branch_prediction_result = branch_prediction_result_reg;
# assign branch_prediction_result_in_fe = (is_conditional_branch && branch_taken_one_bit_predict)? 1'b1 : 1'b0;

# // one bit branch predictor
# one_bit_branch_predictor u_one_bit_branch_predictor (
#    .clk(clk),
#    .rst(rst),
#    .instr_address_fe(curr_instr_address),
#    .instr_address_alu(branch_instr_address_alu_fe),
#    .branch_taken_in(branch_taken_in),
#    .is_conditional_branch_fe(is_conditional_branch),
#    .is_conditional_branch_alu(is_conditional_branch_alu_fe),
#    .branch_taken_out(branch_taken_one_bit_predict)
# );


# always @(posedge clk or posedge rst) begin
#     if (rst) begin
#         branch_target_buffer <= 8'b0;
#         pc_delayed <= 8'b0;
#         branch_prediction_result_reg <= 1'b0;
#     end else begin
#         branch_target_buffer <= branch_target_address_wire;
#     end
# end


# always @(posedge clk or posedge rst) begin
#     if (rst) begin
#         pc <= 16'h0;
#     end else if (valid_reg && dec_ready && exec_ready) begin
#         pc_delayed <= pc[7:0];
#         branch_prediction_result_reg <= branch_prediction_result_in_fe;
#         if (branch_prediction_failed) begin
#             instruction_reg <= 32'b0;
#             // prev:pc <= branch_target_buffer;
#             pc <= instr_address_not_taken_alu_fe;
#         end else begin
#             instruction_reg <= imem_data;
#             // prev: pc <= pc + 16'h2;
#             pc <= branch_predict;
#         end
#     end
# end

# always @(posedge clk or posedge rst) begin
#     if (rst) begin
#         valid_reg <= 1'b0;
#         instruction_reg <= 31'b0;
#     end else begin
#         valid_reg <= 1'b1;
#     end
# end

# assign imem_addr = pc;
# assign instr_valid = valid_reg;
# // assign instr = imem_data;
# assign instr = instruction_reg;  
    
@ convert      
def ModuleFetch(cpu_spec):
    #/ module Fetch(
    #/     input  clk,
    #/     input  rst,
    #/     input  dec_ready,
    #/     input  exec_ready,
    #/     output flush_pipeline,
    #/     input [`cpu_spec.instruction_data_width-1`:0] imem_data,
    #/     output [`cpu_spec.instruction_addr_width-1`:0] imem_addr,
    #/     input  [`cpu_spec.alu_fetch_interface_width-1`:0] alu_fetch_interface,
    #/     output [`cpu_spec.fetch_idecode_interface_width-1`:0] fetch_idecode_interface
    #/     );
    #/ wire [`cpu_spec.instruction_addr_width-1`:0] branch_instr_address_alu_fe;
    #/ wire is_conditional_branch_alu_fe;
    #/ wire branch_taken_in;
    #/ wire [`cpu_spec.instruction_addr_width-1`:0] instr_address_not_taken_alu_fe;
    #/ assign branch_instr_address_alu_fe = alu_fetch_interface[`cpu_spec.alu_fetch_interface['branch_instr_address_alu_fe'][1]`:`cpu_spec.alu_fetch_interface['branch_instr_address_alu_fe'][0]`];
    #/ assign is_conditional_branch_alu_fe = alu_fetch_interface[`cpu_spec.alu_fetch_interface['is_conditional_branch_alu_fe'][1]`:`cpu_spec.alu_fetch_interface['is_conditional_branch_alu_fe'][0]`];
    #/ assign branch_taken_in = alu_fetch_interface[`cpu_spec.alu_fetch_interface['branch_taken_in'][1]`:`cpu_spec.alu_fetch_interface['branch_taken_in'][0]`];
    #/ assign instr_address_not_taken_alu_fe = alu_fetch_interface[`cpu_spec.alu_fetch_interface['instr_address_not_taken_alu_fe'][1]`:`cpu_spec.alu_fetch_interface['instr_address_not_taken_alu_fe'][0]`];
    #/ reg [15:0] pc;
    #/ reg [`cpu_spec.instruction_data_width-1`:0] instruction_reg;
    #/ reg valid_reg;
    #/ reg [`cpu_spec.instruction_addr_width-1`:0] branch_target_buffer; // target instruction address if the branch is taken
    #/ reg [`cpu_spec.instruction_addr_width-1`:0] pc_delayed;
    #/ reg [0:0] branch_prediction_failed_buffer; // branch prediction failed flag
    #/ wire [`cpu_spec.instruction_addr_width-1`:0] branch_target_address_wire;
    #/ wire branch_taken_one_bit_predict;
    #/ wire branch_prediction_result_in_fe;
    #/ reg branch_prediction_result_reg;
    #/ assign fe_idecode_interface[`cpu_spec.fe_idecode_interface['instr_address_not_taken'][1]`:`cpu_spec.fe_idecode_interface['instr_address_not_taken'][0]`] = branch_target_buffer;
    #/ wire [`instruction_addr_width-1`:0]  curr_instr_address;
    #/ assign curr_instr_address = pc[`instruction_addr_width-1`:0];
    #/ wire is_conditional_branch;
    #/ wire is_unconditional_branch;
    ports_mini_decode = {
    'instr':'imem_data',
    'is_unconditional_branch':'is_unconditional_branch',
    'is_conditional_branch':'is_conditional_branch'
    }
    ModuleMiniDecode(cpu_spec=cpu_spec, PORTS = ports_mini_decode)
    #/ wire [15:0] branch_predict;
    #/ assign branch_predict = (is_unconditional_branch)? imem_data[23:16]:
    #/                         (is_conditional_branch && branch_taken_one_bit_predict)? imem_data[7:0]:
    #/                         (pc+16'h2);
    #/ assign branch_target_address_wire = (is_conditional_branch)? imem_data[7:0] : branch_target_buffer;
    #/ assign flush_pipeline = branch_prediction_failed;
    #/ assign fe_idecode_interface[`cpu_spec.fe_idecode_interface['branch_instr_address'][1]`:`cpu_spec.fe_idecode_interface['branch_instr_address'][0]`] = pc_delayed;
    #/ assign fe_idecode_interface[`cpu_spec.fe_idecode_interface['branch_prediction_result'][1]`:`cpu_spec.fe_idecode_interface['branch_prediction_result'][0]`] = branch_prediction_result_reg;
    #/ assign branch_prediction_result_in_fe = (is_conditional_branch && branch_taken_one_bit_predict)? 1'b1 : 1'b0;
    ports_one_bit_branch_predictor = {
    'clk':'clk',
    'rst':'rst',
    'instr_address_fe':'curr_instr_address',
    'instr_address_alu':'branch_instr_address_alu_fe',
    'branch_taken_in':'branch_taken_in',
    'is_conditional_branch_fe':'is_conditional_branch',
    'is_conditional_branch_alu':'is_conditional_branch_alu_fe',
    'branch_taken_out':'branch_taken_one_bit_predict'
    }
    pass
    #/ always @(posedge clk or posedge rst) begin
    #/     if (rst) begin
    #/         branch_target_buffer <= `instruction_addr_width`'b0;
    #/         pc_delayed <= `instruction_addr_width`'b0;
    #/         branch_prediction_result_reg <= 1'b0;
    #/     end else begin
    #/         branch_target_buffer <= branch_target_address_wire;
    #/     end
    #/ end
    #/ 
    #/ always @(posedge clk or posedge rst) begin
    #/     if (rst) begin
    #/         pc <= 16'h0;
    #/     end else if (valid_reg && dec_ready && exec_ready) begin
    #/         pc_delayed <= pc[`instruction_addr_width-1`:0];
    #/         branch_prediction_result_reg <= branch_prediction_result_in_fe;
    #/         if (branch_prediction_failed) begin
    #/             instruction_reg <= `instruction_data_width`'b0;
    #/             // prev:pc <= branch_target_buffer;
    #/             pc <= instr_address_not_taken_alu_fe;
    #/         end else begin
    #/             instruction_reg <= imem_data;
    #/             // prev: pc <= pc + 16'h2;
    #/             pc <= branch_predict;
    #/         end
    #/     end
    #/ end
    #/ 
    #/ always @(posedge clk or posedge rst) begin
    #/     if (rst) begin
    #/         valid_reg <= 1'b0;
    #/         instruction_reg <= `instruction_data_width`'b0;
    #/     end else begin
    #/         valid_reg <= 1'b1;
    #/     end
    #/ end
    #/ 
    #/ assign imem_addr = pc;
    #/ assign fetch_idecode_interface[`fetch_idecode_interface['instr_valid'][1]`:`fetch_idecode_interface['instr_valid'][0]`] = valid_reg;
    #/ assign fetch_idecode_interface[`fetch_idecode_interface['instr'][1]`:`fetch_idecode_interface['instr'][0]`] = instruction_reg;
    #/ endmodule
    
    
@ convert      
def ModuleDecode(cpu_spec):
    #/ module Decode(
    #/     input  clk,
    #/     input  rst,
    #/     input  flush_pipeline,
    #/     input  [`fetch_idecode_interface_width-1`:0] fetch_idecode_interface,
    #/     output [2:0] opcode,
    #/     output [4:0] rs1,
    #/     output [4:0] rs2,
    #/     output [4:0] rd,
    #/     output dec_ready,
    #/     output [`idecode_cu_interface_width-1`:0] idecode_cu_interface
    #/     );
    #/ endmodule
    pass
    

@ convert
def ModuleCU(cpu_spec):
    #/ module CU(
    #/     input  clk,
    #/     input  rst,
    #/     input  flush_pipeline,
    #/     input  [`micro_instruction_data_width-1`:0] micro_code_in_normal,
    #/     input  [`micro_instruction_data_width-1`:0] micro_code_in_speculative,
    #/     input  [`idecode_cu_interface_width-1`:0] idecode_cu_interface,
    #/     output [`cu_alu_interface_width-1`:0] cu_alu_interface,
    #/     output o_exec_ready_combined,
    #/     output o_exec_ready_normal
    #/     );
    #/ endmodule
    pass
    
    
@ convert      
def ModuleALU(cpu_spec):
    #/ module ALU(
    #/     input  clk,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] alu_regfile_in_1,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] alu_regfile_in_2,
    #/     input  [`cpu_spec.external_mem_data_width-1`:0] alu_memory_in,
    #/     output [`alu_result_width-1`:0] alu_result,
    #/     output [`cpu_spec.register_file_addr_width-1`:0] alu_regfile_address_out_1,
    #/     output [`cpu_spec.register_file_addr_width-1`:0] alu_regfile_address_out_2,
    #/     output [`cpu_spec.external_mem_addr_width-1`:0] alu_memory_address_out,
    #/     output alu_memory_write_en_out,
    #/     output [`cpu_spec.register_file_addr_width-1`:0] alu_regfile_address_out,
    #/     output alu_regfile_write_en_out,
    #/     output flush_pipeline_out,
    #/     input  [`cpu_spec.cu_alu_interface_width-1`:0] cu_alu_interface,
    #/     output [`cpu_spec.alu_fe_interface_width-1`:0] alu_fe_interface
    #/     );
    #/ endmodule
    pass

