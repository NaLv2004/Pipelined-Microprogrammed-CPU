
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(__file__)))
sys.path.append(dirname(__file__))

import pytv
from pytv.Converter import convert
from pytv.ModuleLoader import moduleloader
import sys
from os.path import dirname, abspath
import math
from parse_asembly import assemble
from generate_micro_code import construct_micro_code_addr_list  


# from PyTU import QuMode, OfMode, QuType

micro_code_addr_list, opcode_list, micro_code_len_dict, micro_code_list, comments_list, n_micro_code_groups = construct_micro_code_addr_list()
for i in range (0,n_micro_code_groups):
    if micro_code_addr_list[i] is not None:
        print(f"addr: {micro_code_addr_list[i]}")
        print(f"opcode: {opcode_list[i]}")
        print(f"len: {micro_code_len_dict[i]}")
        print(f"micro_code: {micro_code_list[i]}")
        print(f"comments: {comments_list[i]}")
        print(f"===============================")
        
    
print(f"FINSIHED GENERATING MICRO CODES")

# ======================================== CPU DATA WIDTH CONFIGURATIONS ===========================================
class cpu_specifications:  
    def __init__(self):
        self.instruction_data_width = 32
        self.instruction_addr_width = 8
        self.external_mem_data_width = 16
        self.external_mem_addr_width = 8
        self.external_mem_depth = 256
        self.register_file_data_width = 16
        self.register_file_addr_width = 8
        self.register_file_depth = 256
        self.micro_instruction_data_width = 32
        self.micro_instruction_addr_width = 8
        self.branch_prediction_table_depth = 8
        self.branch_prediction_table_addr_width = math.ceil(math.log2(self.branch_prediction_table_depth))
        self.branch_prediction_table_data_width = 11
        self.micro_instruction_cnt_width = 3
        self.micro_instruction_depth = 256
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
        
        
        # micro code configuration
        self.micro_code_addr_list = micro_code_addr_list
        self.opcode_list = opcode_list
        self.micro_code_len_list = micro_code_len_dict
        self.micro_code_list = micro_code_list
        self.comments_list = comments_list
        self.n_micro_code_groups = n_micro_code_groups

        # self.allocate_interface(fetch_idecode_interface, 'fetch_idecode')
    
    def allocate_interface(self, interface, interface_name):
        interface_ports = interface.keys()
        port_start_bit = 0
        if interface_name == 'fetch_idecode':
            for port in interface_ports:
                port_width = interface[port]
                port_end_bit = port_start_bit + port_width -1
                self.fetch_idecode_interface[port] = [0,1]
                self.fetch_idecode_interface[port][0] = port_start_bit  
                self.fetch_idecode_interface[port][1] = port_end_bit
                port_start_bit = port_end_bit + 1
                self.fetch_idecode_interface_width += port_width
        if interface_name == 'alu_fetch':
            for port in interface_ports:
                port_width = interface[port]
                port_end_bit = port_start_bit + port_width -1
                self.alu_fetch_interface[port] = [0,1]
                self.alu_fetch_interface[port][0] = port_start_bit  
                self.alu_fetch_interface[port][1] = port_end_bit
                port_start_bit = port_end_bit + 1
                self.alu_fetch_interface_width += port_width
        if interface_name == 'cu_alu':
            for port in interface_ports:
                port_width = interface[port]
                self.cu_alu_interface[port] = [0,1]
                port_end_bit = port_start_bit + port_width -1
                self.cu_alu_interface[port][0] = port_start_bit  
                self.cu_alu_interface[port][1] = port_end_bit
                port_start_bit = port_end_bit + 1
                self.cu_alu_interface_width += port_width
        if interface_name == 'idecode_cu':
            for port in interface_ports:
                port_width = interface[port]
                self.idecode_cu_interface[port] = [0,1]
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

# these ports are copied from the source code of fetch
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
# cu_alu_interface['micro_code_addr_out'] = my_cpu_spec.micro_instruction_addr_width
cu_alu_interface['micro_code_out'] = my_cpu_spec.micro_instruction_data_width
# cu_alu_interface['micro_code_addr_speculative_fetch'] =  my_cpu_spec.micro_instruction_addr_width
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
    #/     output is_conditional_branch
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
    #/     input [`cpu_spec.instruction_addr_width-1`:0] instr_address_alu,
    #/     input branch_taken_in,
    #/     input is_conditional_branch_fe,
    #/     input is_conditional_branch_alu,
    #/     output branch_taken_out,
    #/     output [`cpu_spec.branch_prediction_table_depth-1`:0] mem_one_bit_predictor_test
    #/     );
    #/ wire [`cpu_spec.instruction_addr_width-1`:0] instr_address_fe;
    #/ wire [`cpu_spec.instruction_addr_width-1`:0] instr_address_alu;
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
    #/ assign idx_slot_alu = instr_address_alu[`cpu_spec.branch_prediction_table_addr_width-1`:0];
    #/ assign slot_hit_alu = (counters_and_address[idx_slot_alu][`cpu_spec.instruction_addr_width-1`:0]==instr_address_alu[`cpu_spec.instruction_addr_width-1`:0]) ?
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
    #/ wire is_micro_code_conflict;
    #/ wire is_micro_code_dependent;
    #/ assign is_micro_code_conflict = (| (micro_code_speculative[`cpu_spec.micro_instruction_data_width-1`:0] & micro_code_normal[`cpu_spec.micro_instruction_data_width-1`:0])) ? 1'b1:
    #/                               (| micro_code_normal[11:5]) ? 1'b1 : 1'b0;
    #/ assign is_micro_code_dependent = (instruction_speculative[23:16]==instruction_normal[7:0])|(instruction_speculative[15:8]==instruction_normal[7:0]);
    #/ assign is_micro_code_not_conflict = ~(is_micro_code_conflict|is_micro_code_dependent);
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
    #/ assign data_out = mem[addr[7:1]];
    #/ endmodule
    pass
    
    
@ convert
def ModuleMicroInstrMem(cpu_spec):
    #/ module MicroInstrMem(
    #/        input [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_addr_in,
    #/        output [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_data_out,
    #/        input [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_addr_speculative_fetch_in,
    #/        output [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_data_speculative_fetch_out
    #/        );
    #/ reg [`cpu_spec.micro_instruction_data_width-1`:0] mem [`cpu_spec.micro_instruction_depth-1`:0];
    #/ assign micro_code_data_out = mem[micro_code_addr_in];
    #/ assign micro_code_data_speculative_fetch_out = mem[micro_code_addr_speculative_fetch_in];
    #/ endmodule
    pass


@ convert
def ModuleRegisterFile(cpu_spec):
    #/ module RegisterFile(
    #/     input clk,
    #/     input  [`cpu_spec.register_file_addr_width-1`:0] reg_addr_1,
    #/     input  [`cpu_spec.register_file_addr_width-1`:0] reg_addr_2,
    #/     input  [0:0] write_en,
    #/     input  [`cpu_spec.register_file_addr_width-1`:0] reg_addr_in,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] data_in,
    #/     output [`cpu_spec.register_file_data_width-1`:0] data_out_1,
    #/     output [`cpu_spec.register_file_data_width-1`:0] data_out_2,
    #/     output [`cpu_spec.register_file_data_width-1`:0] mem_test
    #/     );
    #/ reg [`cpu_spec.register_file_data_width-1`:0] mem [`cpu_spec.register_file_depth-1`:0];
    #/ assign data_out_1 = mem[reg_addr_1];
    #/ assign data_out_2 = mem[reg_addr_2];
    #/ assign mem_test = mem[0];
    #/ always @(posedge clk)
    #/ begin
    #/     if (write_en)
    #/     begin
    #/         mem[reg_addr_in] <= data_in;
    #/     end
    #/ end
    #/ endmodule
    pass


@ convert
def ModuleExternalMem(cpu_spec):
    #/ module ExternalMem(
    #/     input clk,
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
    #/ wire branch_prediction_failed;
    #/ wire [`cpu_spec.instruction_addr_width-1`:0] instr_address_not_taken_alu_fe;
    #/ assign branch_instr_address_alu_fe = alu_fetch_interface[`cpu_spec.alu_fetch_interface['branch_instr_address_alu_fe'][1]`:`cpu_spec.alu_fetch_interface['branch_instr_address_alu_fe'][0]`];
    #/ assign is_conditional_branch_alu_fe = alu_fetch_interface[`cpu_spec.alu_fetch_interface['is_conditional_branch_alu_fe'][1]`:`cpu_spec.alu_fetch_interface['is_conditional_branch_alu_fe'][0]`];
    #/ assign branch_taken_in = alu_fetch_interface[`cpu_spec.alu_fetch_interface['branch_taken_in'][1]`:`cpu_spec.alu_fetch_interface['branch_taken_in'][0]`];
    #/ assign instr_address_not_taken_alu_fe = alu_fetch_interface[`cpu_spec.alu_fetch_interface['instr_address_not_taken_alu_fe'][1]`:`cpu_spec.alu_fetch_interface['instr_address_not_taken_alu_fe'][0]`];
    #/ assign branch_prediction_failed = alu_fetch_interface[`cpu_spec.alu_fetch_interface['branch_prediction_failed'][1]`:`cpu_spec.alu_fetch_interface['branch_prediction_failed'][0]`];
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
    #/ assign fetch_idecode_interface[`cpu_spec.fetch_idecode_interface['instr_address_not_taken'][1]`:`cpu_spec.fetch_idecode_interface['instr_address_not_taken'][0]`] = branch_target_buffer;
    #/ wire [`cpu_spec.instruction_addr_width-1`:0]  curr_instr_address;
    #/ assign curr_instr_address = pc[`cpu_spec.instruction_addr_width-1`:0];
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
    #/ assign fetch_idecode_interface[`cpu_spec.fetch_idecode_interface['branch_instr_address'][1]`:`cpu_spec.fetch_idecode_interface['branch_instr_address'][0]`] = pc_delayed;
    #/ assign fetch_idecode_interface[`cpu_spec.fetch_idecode_interface['branch_prediction_result'][1]`:`cpu_spec.fetch_idecode_interface['branch_prediction_result'][0]`] = branch_prediction_result_reg;
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
    ModuleOneBitBranchPredictor(cpu_spec=cpu_spec, PORTS = ports_one_bit_branch_predictor)
    #/ always @(posedge clk or posedge rst) begin
    #/     if (rst) begin
    #/         branch_target_buffer <= `cpu_spec.instruction_addr_width`'b0;
    #/         pc_delayed <= `cpu_spec.instruction_addr_width`'b0;
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
    #/         pc_delayed <= pc[`cpu_spec.instruction_addr_width-1`:0];
    #/         branch_prediction_result_reg <= branch_prediction_result_in_fe;
    #/         if (branch_prediction_failed) begin
    #/             instruction_reg <= `cpu_spec.instruction_data_width`'b0;
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
    #/         instruction_reg <= `cpu_spec.instruction_data_width`'b0;
    #/     end else begin
    #/         valid_reg <= 1'b1;
    #/     end
    #/ end
    #/ 
    #/ assign imem_addr = pc;
    #/ assign fetch_idecode_interface[`cpu_spec.fetch_idecode_interface['instr_valid'][1]`:`cpu_spec.fetch_idecode_interface['instr_valid'][0]`] = valid_reg;
    #/ assign fetch_idecode_interface[`cpu_spec.fetch_idecode_interface['instr'][1]`:`cpu_spec.fetch_idecode_interface['instr'][0]`] = instruction_reg;
    #/ endmodule
  
        
@ convert      
def ModuleDecode(cpu_spec):
    #/ module Decode(
    #/     input  clk,
    #/     input  rst,
    #/     input  flush_pipeline,
    #/     input  [`cpu_spec.fetch_idecode_interface_width-1`:0] fetch_idecode_interface,
    #/     output [2:0] opcode,
    #/     output [4:0] rs1,
    #/     output [4:0] rs2,
    #/     output [4:0] rd,
    #/     output dec_ready,
    #/     output [`cpu_spec.idecode_cu_interface_width-1`:0] idecode_cu_interface
    #/     );
    fetch_idecode_interface_port_mapping = {
    'instr_valid':'instr_valid',
    'instr_address_not_taken':'instr_address_not_taken_fe_de',
    'branch_instr_address':'branch_instr_address_fe_de',
    'branch_prediction_result':'branch_prediction_result_fe_de',
    'instr':'instr'
    }
    # // assign inner wires to fetches interface ports (input)
    for fetch_port in fetch_idecode_interface_port_mapping.keys():
        idecode_port = fetch_idecode_interface_port_mapping[fetch_port]
        low_bit = cpu_spec.fetch_idecode_interface[fetch_port][0]
        high_bit = cpu_spec.fetch_idecode_interface[fetch_port][1]
        port_width = high_bit - low_bit + 1
        #/ wire [`port_width-1`:0] `idecode_port`;
        #/ assign `idecode_port` = fetch_idecode_interface[`high_bit`:`low_bit`];
    
    # // assign inner wires to idecode_cu_interface ports (output)
    for idecode_output_port in cpu_spec.idecode_cu_interface.keys():
        low_bit = cpu_spec.idecode_cu_interface[idecode_output_port][0]
        high_bit = cpu_spec.idecode_cu_interface[idecode_output_port][1]
        port_width = high_bit - low_bit + 1
        #/ wire [`port_width-1`:0] `idecode_output_port`;
        #/ assign idecode_cu_interface[`high_bit`:`low_bit`] = `idecode_output_port`;
    
    #/ reg ready_reg;
    #/ reg micro_code_reg;
    #/ reg [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_addr_reg;
    #/ reg [`cpu_spec.instruction_data_width-1`:0] instr_out_reg;
    #/ reg [`cpu_spec.micro_instruction_cnt_width-1`:0] micro_code_cnt_reg;
    #/ // assign instr_out = instr_out_reg;
    #/ assign instr_out = instr;
    #/ assign dec_ready = ready_reg;
    #/ wire [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_cnt_in;
    #/ assign opcode = instr[2:0];  
    #/ assign rs1 = instr[7:3];     
    #/ assign rs2 = instr[12:8];    
    #/ assign rd = instr[15:13];    
    #/ assign micro_code = micro_code_reg;
    #/ assign instr_address_not_taken_de_cu = instr_address_not_taken_fe_de;
    #/ assign branch_prediction_result_de_cu = branch_prediction_result_fe_de;
    #/ assign branch_instr_address_de_cu = branch_instr_address_fe_de;
    for i_micro_code_group, micro_code_addr in enumerate(cpu_spec.micro_code_addr_list):
        if micro_code_addr is None:
            break
        if i_micro_code_group == 0:
            #/ assign micro_code_addr_out = 
            #/      (flush_pipeline==1'b1) ? 8'b1111_1111 : // flush pipeline (no operations))   8'b1111_1111;
            pass
        #/      (instr[31:24]==`cpu_spec.opcode_list[i_micro_code_group]`) ? `micro_code_addr`: 
    #/      8'b1111_1111;
    #/ //assign micro_code_addr_out = instr[31:24];
    #/ // counter: n of micro codes following this address     
    for i_micro_code_group, micro_code_len in enumerate(cpu_spec.micro_code_len_list):
        if micro_code_len is None:
            break
        if i_micro_code_group == 0:
            #/ assign micro_code_cnt_out = 
            #/      (flush_pipeline==1'b1) ? 3'b000 : // flush pipeline (no operations))   3'b000;
            pass
        #/      (instr[31:24]==`cpu_spec.opcode_list[i_micro_code_group]`) ? `micro_code_len`: 
    #/      3'b000;         
    #/ always @(posedge clk or posedge rst) begin
    #/     if (rst) begin
    #/         ready_reg <= 1'b0;
    #/     end else begin
    #/         ready_reg <= 1'b1;
    #/     end
    #/ end
    #/ always @(posedge clk) begin
    #/     micro_code_reg <= `cpu_spec.micro_instruction_data_width`'b0;
    #/ end
    #/ endmodule
    
    pass
    
@ convert
def ModuleCU(cpu_spec):
    #/ module CU(
    #/     input  clk,
    #/     input  rst,
    #/     input  flush_pipeline,
    #/     input  [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_in_normal,
    #/     input  [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_in_speculative,
    #/     input  [`cpu_spec.idecode_cu_interface_width-1`:0] idecode_cu_interface,
    #/     output [`cpu_spec.cu_alu_interface_width-1`:0] cu_alu_interface,
    #/     output o_exec_ready_combined,
    #/     output o_exec_ready_normal,
    #/     output [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_addr_out,
    #/     output [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_addr_speculative_fetch
    #/     );
    #/ wire clk;
    #/ wire rst;
    #/ wire flush_pipeline;
    #/ wire o_exec_ready_combined;
    #/ wire o_exec_ready_normal;
    #/ wire [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_in_normal;
    #/ wire [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_in_speculative;
    #/ wire [`cpu_spec.idecode_cu_interface_width-1`:0] idecode_cu_interface;
    #/ wire [`cpu_spec.cu_alu_interface_width-1`:0] cu_alu_interface;
    #/ // assign inner wires to de_cu_interface ports (input)
    idecode_cu_interface_port_mapping = {
    'instr_out': 'instr_cu_in',
    'micro_code_addr_out':'micro_code_addr_in',
    'micro_code_cnt_out':'micro_code_cnt_in',
    'instr_address_not_taken_de_cu': 'instr_address_not_taken_de_cu',
    'branch_prediction_result_de_cu': 'branch_prediction_result_de_cu',
    'branch_instr_address_de_cu': 'branch_instr_address_de_cu'
    }
    for idecode_port in idecode_cu_interface_port_mapping.keys():
        cu_port = idecode_cu_interface_port_mapping[idecode_port]
        low_bit = cpu_spec.idecode_cu_interface[idecode_port][0]
        high_bit = cpu_spec.idecode_cu_interface[idecode_port][1]
        port_width = high_bit - low_bit + 1
        #/ wire [`port_width-1`:0] `cu_port`;
        #/ assign `cu_port` = idecode_cu_interface[`high_bit`:`low_bit`];
    #/ // assign inner wires to cu_alu_interface ports (output)
    for cu_output_port in cpu_spec.cu_alu_interface.keys():
        low_bit = cpu_spec.cu_alu_interface[cu_output_port][0]
        high_bit = cpu_spec.cu_alu_interface[cu_output_port][1]
        port_width = high_bit - low_bit + 1
        #/ wire [`port_width-1`:0] `cu_output_port`;
        #/ assign cu_alu_interface[`high_bit`:`low_bit`] = `cu_output_port`;
    #/ wire [`cpu_spec.instruction_data_width-1`:0]  instruction_normal;
    #/ reg [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_addr_reg;
    #/ reg [`cpu_spec.micro_instruction_cnt_width-1`:0] micro_code_cnt_reg;
    #/ reg [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_addr_speculative_fetch_reg;
    #/ reg [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_speculative_fetch_reg;
    #/ reg [`cpu_spec.instruction_data_width-1`:0] cu_instruction_reg;
    #/ reg [`cpu_spec.instruction_addr_width-1`:0] instr_address_not_taken_reg;
    #/ reg [`cpu_spec.instruction_addr_width-1`:0] branch_instr_address_reg;
    #/ reg branch_prediction_result_reg;
    #/ reg exec_combined_reg;
    #/ reg [`cpu_spec.instruction_data_width-1`:0] instruction_normal_reg;
    #/ assign instr_address_not_taken_cu_alu = instr_address_not_taken_reg;
    #/ assign micro_code_addr_out = micro_code_addr_reg;
    #/ assign micro_code_addr_speculative_fetch = micro_code_addr_speculative_fetch_reg;
    #/ assign branch_instr_address_cu_alu = branch_instr_address_reg;
    #/ assign branch_prediction_result_cu_alu = branch_prediction_result_reg;
    #/ assign instr_cu_out = cu_instruction_reg;
    #/ assign instruction_normal = instruction_normal_reg;
    #/ assign o_exec_ready_normal = (micro_code_cnt_reg==3'b0) ? 1'b1 : 1'b0;  
    ports_judge_not_conflict_speculative_fetch = {
        'micro_code_normal': 'micro_code_in_normal',
       'micro_code_speculative': 'micro_code_in_speculative',
        'instruction_normal': 'instruction_normal',
        'instruction_speculative': 'instr_cu_out',
        'is_micro_code_not_conflict': 'o_exec_ready_speculative_fetch'
    }
    ModuleJudgeNotConflictSpeculativeFetch(cpu_spec=cpu_spec, PORTS = ports_judge_not_conflict_speculative_fetch)
    #/ assign o_exec_ready_combined = o_exec_ready_normal | o_exec_ready_speculative_fetch;
    #/ // fused micro-code 
    #/ assign micro_code_out = (o_exec_ready_speculative_fetch)? (micro_code_in_normal ^ micro_code_in_speculative): micro_code_in_normal;
    #/ // CU is ready to receive new micro-code address when micro-code-reg == 0 (all the micro-codes executed)
    #/ always @ (posedge clk or negedge rst)
    #/ begin
    #/     exec_combined_reg <= o_exec_ready_combined;
    #/     if (rst || flush_pipeline) begin
    #/         micro_code_cnt_reg <= 3'b0;
    #/         micro_code_addr_reg <= 8'b1111_1111;
    #/         cu_instruction_reg <= 32'b0;
    #/         instruction_normal_reg <= 32'b0;
    #/         instr_address_not_taken_reg <= 8'b0;
    #/         branch_instr_address_reg <= 8'b0;
    #/         branch_prediction_result_reg <= 1'b0;
    #/         micro_code_addr_speculative_fetch_reg <= 8'b1111_1111;
    #/     end  
    #/     if (rst==0) begin
    #/     if ((micro_code_cnt_reg == 0 | exec_combined_reg) && (!flush_pipeline))  // prev: o_exec_ready_combined
    #/     begin
    #/         micro_code_addr_reg <= micro_code_addr_in;
    #/         micro_code_cnt_reg <= micro_code_cnt_in;
    #/         cu_instruction_reg <= instr_cu_in;
    #/         instr_address_not_taken_reg <= instr_address_not_taken_de_cu;
    #/         branch_instr_address_reg <= branch_instr_address_de_cu;
    #/         branch_prediction_result_reg <= branch_prediction_result_de_cu;
    #/         micro_code_addr_speculative_fetch_reg <= 8'b1111_1111;
    #/      end
    #/      if (micro_code_cnt_reg == 0 && (!flush_pipeline))
    #/      begin
    #/         instruction_normal_reg <= instr_cu_in;
    #/      end
    #/      if (micro_code_cnt_reg > 0)
    #/      begin
    #/         micro_code_cnt_reg <= micro_code_cnt_reg - 1;
    #/         micro_code_addr_reg <= micro_code_addr_reg + 1;
    #/         micro_code_addr_speculative_fetch_reg <= micro_code_addr_in;
    #/      end
    #/      end
    #/ end
    #/ endmodule
    pass
    
@ convert      
def ModuleALU(cpu_spec):
    #/ module ALU(
    #/     input  clk,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] alu_regfile_in_1,
    #/     input  [`cpu_spec.register_file_data_width-1`:0] alu_regfile_in_2,
    #/     input  [`cpu_spec.external_mem_data_width-1`:0] alu_memory_in,
    #/     output [`cpu_spec.alu_result_width-1`:0] alu_result,
    #/     output [`cpu_spec.register_file_addr_width-1`:0] alu_regfile_address_out_1,
    #/     output [`cpu_spec.register_file_addr_width-1`:0] alu_regfile_address_out_2,
    #/     output [`cpu_spec.external_mem_addr_width-1`:0] alu_memory_address_out,
    #/     output alu_memory_write_en_out,
    #/     output [`cpu_spec.register_file_addr_width-1`:0] alu_regfile_address_out,
    #/     output alu_regfile_write_en_out,
    #/     input  [`cpu_spec.cu_alu_interface_width-1`:0] cu_alu_interface,
    #/     output [`cpu_spec.alu_fetch_interface_width-1`:0] alu_fetch_interface
    #/     );
    cu_alu_interface_port_mapping = {
    'micro_code_out':'micro_code',
    'instr_cu_out':'instruction',
    'instr_address_not_taken_cu_alu': 'instr_address_not_taken_cu_alu',
    'branch_prediction_result_cu_alu': 'branch_prediction_result_cu_alu',
    'branch_instr_address_cu_alu': 'branch_instr_address_cu_alu',
    }
    for cu_port in cu_alu_interface_port_mapping.keys():
        alu_port = cu_alu_interface_port_mapping[cu_port]
        low_bit = cpu_spec.cu_alu_interface[cu_port][0]
        high_bit = cpu_spec.cu_alu_interface[cu_port][1]
        port_width = high_bit - low_bit + 1
        #/ wire [`port_width-1`:0] `alu_port`;
        #/ assign `alu_port` = cu_alu_interface[`high_bit`:`low_bit`];
    #/ // assign inner wires to alu_fetch_interface ports (output)
    fe_alu_interface_port_mapping = {
    'branch_prediction_failed':'flush_pipeline_out',
    'instr_address_not_taken_alu_fe':'instr_address_not_taken_alu_fe',
    'branch_instr_address_alu_fe':'branch_instr_address_alu_fe',
    'is_conditional_branch_alu_fe':'is_conditional_branch_alu_fe',
    'branch_taken_in':'branch_taken_alu_fe'
    }
    # for alu_output_port in cpu_spec.alu_fetch_interface.keys():
    #     low_bit = cpu_spec.alu_fetch_interface[alu_output_port][0]
    #     high_bit = cpu_spec.alu_fetch_interface[alu_output_port][1]
    #     port_width = high_bit - low_bit + 1
    #     #/ wire [`port_width-1`:0] `alu_output_port`;
    #     #/ assign alu_fetch_interface[`high_bit`:`low_bit`] = `alu_output_port`;
    for fe_port in fe_alu_interface_port_mapping.keys():
        alu_port = fe_alu_interface_port_mapping[fe_port]
        low_bit = cpu_spec.alu_fetch_interface[fe_port][0]
        high_bit = cpu_spec.alu_fetch_interface[fe_port][1]
        port_width = high_bit - low_bit + 1
        #/ wire [`port_width-1`:0] `alu_port`;
        #/ assign alu_fetch_interface[`high_bit`:`low_bit`] = `alu_port`;
    #/ wire clk;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_regfile_in_1;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_regfile_in_2;
    #/ wire [`cpu_spec.register_file_addr_width-1`:0] alu_regfile_address_out_1;
    #/ wire [`cpu_spec.register_file_addr_width-1`:0] alu_regfile_address_out_2;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_operand_1;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_operand_2;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_add_result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_sub_result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_and_result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_or_result;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_xor_result;
    #/ wire judge_equal_result;
    #/ reg [`cpu_spec.register_file_data_width-1`:0] alu_result_reg;
    #/ reg [`cpu_spec.instruction_data_width-1`:0] instruction_pipeline;
    #/ wire [`cpu_spec.instruction_data_width-1`:0] instruction_choosed;
    #/ assign instruction_choosed = (micro_code[16:16])? instruction_pipeline :instruction;
    #/ assign alu_regfile_address_out_1 = instruction_choosed[23:16];
    #/ assign alu_regfile_address_out_2 = instruction_choosed[15:8];
    #/ assign alu_memory_address_out = (micro_code[11:11] == 1'b1) ?  instruction_choosed[23:16]: 
    #/                                 (micro_code[10:10] == 1'b1) ? instruction_choosed[15:8]: 8'b0000_0000; 
    #/ assign alu_operand_1 =  (micro_code[21:21] == 1'b1) ? instruction_choosed[23:16]: // first operand is an immediate value
    #/                        (micro_code[9:9] == 1'b1) ?  alu_memory_in: 
    #/                        (micro_code[7:7] == 1'b1) ? alu_regfile_in_1: 16'b0;
    #/ assign alu_operand_2 = (micro_code[20:20] == 1'b1) ? instruction_choosed[15:8]: // second operand is an immediate value
    #/                        (micro_code[8:8] == 1'b1) ?  alu_memory_in:
    #/                        (micro_code[6:6] == 1'b1) ? alu_regfile_in_2: 
    #/                        (micro_code[5:5] == 1'b1) ? instruction_choosed[7:0] : 16'b0;
    #/ assign alu_regfile_write_en_out = (micro_code[0:0]==1'b1) ? 1'b1: 1'b0;
    #/ assign alu_regfile_address_out = instruction_choosed[7:0];
    #/ assign alu_memory_write_en_out = (micro_code[1:1]==1'b1) ? 1'b1: 1'b0;
    ports_adder = {'op_1':'alu_operand_1','op_2':'alu_operand_2','result':'alu_add_result'}
    ports_subtractor = {'op_1':'alu_operand_1','op_2':'alu_operand_2','result':'alu_sub_result'}
    ports_and = {'op_1':'alu_operand_1','op_2':'alu_operand_2','result':'alu_and_result'}
    ports_or = {'op_1':'alu_operand_1','op_2':'alu_operand_2','result':'alu_or_result'}
    ports_xor = {'op_1':'alu_operand_1','op_2':'alu_operand_2','result':'alu_xor_result'}
    ports_equal = {'op_1':'alu_operand_1','op_2':'alu_operand_2','result':'alu_judge_equal_result'}
    ModuleAdder(cpu_spec=cpu_spec,PORTS=ports_adder)
    ModuleSubstractor(cpu_spec=cpu_spec,PORTS=ports_subtractor)
    ModuleAnder(cpu_spec=cpu_spec,PORTS=ports_and)
    ModuleOrer(cpu_spec=cpu_spec,PORTS=ports_or)
    ModuleXorer(cpu_spec=cpu_spec,PORTS=ports_xor)
    ModuleJudgeEqual(cpu_spec=cpu_spec,PORTS=ports_equal)
    #/ assign alu_result = (micro_code[15:12] == 4'b0001) ? alu_add_result:
    #/                     (micro_code[15:12] == 4'b0010) ? alu_sub_result:
    #/                     (micro_code[15:12] == 4'b0011) ? alu_xor_result:
    #/                     (micro_code[15:12] == 4'b0100) ? alu_and_result:
    #/                     (micro_code[15:12] == 4'b0101) ? alu_or_result:
    #/                     (micro_code[15:12] == 4'b0000) ? alu_operand_1:
    #/                     (micro_code[15:12] == 4'b1100) ? alu_judge_equal_result:
    #/                     16'b0;
    #/ assign is_conditional_branch_alu_fe = (instruction_choosed[31:28]==4'b0110) ? 1'b1: 1'b0;
    #/ assign flush_pipeline_out = (!(instruction_choosed[31:28]==4'b0110)) ? 1'b0: 
    #/                             (alu_result == branch_prediction_result_cu_alu) ? 1'b0: 1'b1;
    #/ assign instr_address_not_taken_alu_fe = instr_address_not_taken_cu_alu;
    #/ assign branch_instr_address_alu_fe = branch_instr_address_cu_alu;
    #/ assign branch_taken_alu_fe = (!(instruction_choosed[31:28]==4'b0110)) ? 1'b0:
    #/                              (alu_result) ? 1'b1: 1'b0;
    #/ // inner registers
    #/ reg [31:0] micro_code_reg;
    #/ always @ (posedge clk)
    #/ begin
    #/     micro_code_reg <= micro_code;
    #/     if (micro_code[17:17])
    #/     begin
    #/         instruction_pipeline <= instruction;
    #/     end
    #/ end
    #/ // behaviour according to micro-code
    #/ always @ (posedge clk)
    #/ begin
    #/     if (micro_code_reg == 16'b0)
    #/     begin
    #/         alu_result_reg <= alu_regfile_in_1 + alu_regfile_in_2;
    #/     end
    #/ end 
    #/ endmodule
    pass

@ convert 
def ModuleCPUTop(cpu_spec):
    #/ module CPUTop;
    #/ reg clk;
    #/ reg rst;
    #/ wire [15:0] imem_addr;
    #/ wire [`cpu_spec.instruction_data_width-1`:0] imem_data;
    #/ wire [`cpu_spec.register_file_addr_width-1`:0] register_file_addr_1;
    #/ wire [`cpu_spec.register_file_addr_width-1`:0] register_file_addr_2;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] register_data_out_1;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] register_data_out_2;
    #/ wire [`cpu_spec.micro_instruction_data_width-1`:0] micro_code;
    #/ wire [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_addr;
    #/ wire [`cpu_spec.micro_instruction_data_width-1`:0] micro_code_speculative_fetch;  // REASSIGN!
    #/ wire [`cpu_spec.micro_instruction_addr_width-1`:0] micro_code_addr_speculative_fetch;  // REASSIGN!
    #/ wire [`cpu_spec.register_file_data_width-1`:0] alu_result;
    #/ wire [`cpu_spec.external_mem_data_width-1`:0] data_memory_alu;
    #/ wire [`cpu_spec.external_mem_addr_width-1`:0] address_memory_alu;
    #/ wire [0:0] write_en_memory;
    #/ wire [0:0] write_en_regfile;
    #/ wire [`cpu_spec.register_file_addr_width-1`:0] register_file_addr_dest;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] mem_regfile_test;
    #/ wire [`cpu_spec.external_mem_data_width-1`:0] mem_external_test;
    #/ wire [`cpu_spec.register_file_data_width-1`:0] mem_regfile_test1;
    #/ wire [`cpu_spec.external_mem_data_width-1`:0] mem_external_test1;
    #/ wire [0:0] flush_pipeline; // flush pipeline when branch prediction fails
    #/ wire dec_ready;
    #/ wire exec_ready; // connects CU and Fetch
    #/ // fe-de; de-cu; cu-alu; alu-fe interfaces
    #/ wire [`cpu_spec.fetch_idecode_interface_width-1`:0] fetch_idecode_interface;
    #/ wire [`cpu_spec.idecode_cu_interface_width-1`:0] idecode_cu_interface;
    #/ wire [`cpu_spec.cu_alu_interface_width-1`:0] cu_alu_interface;
    #/ wire [`cpu_spec.alu_fetch_interface_width-1`:0] alu_fetch_interface;
    #/ 
    #/ assign mem_external_test1 = u_0000000001_RegisterFile0000000001.mem[1];
    
    ports_fetch ={
        'clk':'clk',
        'rst':'rst',
        'imem_addr':'imem_addr',
        'imem_data':'imem_data',
        'dec_ready':'dec_ready',
        'exec_ready':'exec_ready',
        'flush_pipeline':'flush_pipeline',
        'fetch_idecode_interface':'fetch_idecode_interface',
        'alu_fetch_interface':'alu_fetch_interface'
    }
    ModuleFetch(cpu_spec=cpu_spec,PORTS=ports_fetch)
    
    ports_instr_mem = {
        'addr':'imem_addr',
        'data_out':'imem_data',
    }
    
    ModuleInstrMem(cpu_spec=cpu_spec,PORTS=ports_instr_mem)
    
    ports_idecode = {
        'clk':'clk',
        'rst':'rst',
        'dec_ready':'dec_ready',
        'flush_pipeline':'flush_pipeline',
        'fetch_idecode_interface':'fetch_idecode_interface',
        'idecode_cu_interface':'idecode_cu_interface'
    }
    
    ModuleDecode(cpu_spec=cpu_spec,PORTS=ports_idecode)
    
    ports_cu = {
        'clk':'clk', #
        'rst':'rst', #
        'micro_code_in_normal':'micro_code', #
        'micro_code_in_speculative':'micro_code_speculative_fetch', #
        'micro_code_addr_out':'micro_code_addr',
        'micro_code_addr_speculative_fetch':'micro_code_addr_speculative_fetch',
        'o_exec_ready_combined':'exec_ready', #
        'flush_pipeline':'flush_pipeline', #
        'idecode_cu_interface':'idecode_cu_interface', #
        'cu_alu_interface':'cu_alu_interface' #
    }
    
    ModuleCU(cpu_spec=cpu_spec,PORTS=ports_cu)
    
    
    # register_file u_register_file(
    # .clk(clk),
    # .reg_addr_1(register_file_addr_1),
    # .reg_addr_2(register_file_addr_2),
    # .data_out_1(register_data_out_1),
    # .data_out_2(register_data_out_2),
    # .write_en(write_en_regfile),
    # .reg_addr_in(register_file_addr_dest),
    # .data_in(alu_result),
    # .mem_test(mem_regfile_test)
    # );

    ports_regfile = {
        'clk':'clk',
        'reg_addr_1':'register_file_addr_1',
        'reg_addr_2':'register_file_addr_2',
        'data_out_1':'register_data_out_1',
        'data_out_2':'register_data_out_2',
         'write_en':'write_en_regfile',
        'reg_addr_in':'register_file_addr_dest',
         'data_in':'alu_result',
        'mem_test':'mem_regfile_test'
    }
    
    ModuleRegisterFile(cpu_spec=cpu_spec,PORTS=ports_regfile)
    
    ports_micro_instr_mem = {
        'micro_code_addr_in':'micro_code_addr',
        'micro_code_data_out':'micro_code',
        'micro_code_addr_speculative_fetch_in':'micro_code_addr_speculative_fetch',
        'micro_code_data_speculative_fetch_out':'micro_code_speculative_fetch'
    }
    
    ModuleMicroInstrMem(cpu_spec=cpu_spec,PORTS=ports_micro_instr_mem)
    
    ports_external_mem ={
        'clk':'clk',
        'micro_code':'micro_code',
        'addr':'address_memory_alu',
        'data_in':'alu_result',
        'data_out':'data_memory_alu',
        'data_test':'mem_external_test'
    }
    
    ModuleExternalMem(cpu_spec=cpu_spec,PORTS=ports_external_mem)

    ports_alu = {
        'clk':'clk',
        'alu_regfile_in_1':'register_data_out_1',
        'alu_regfile_in_2':'register_data_out_2',
        'alu_memory_in':'data_memory_alu',
        'alu_result':'alu_result',
        'alu_regfile_address_out_1':'register_file_addr_1',
        'alu_regfile_address_out_2':'register_file_addr_2',
        'alu_memory_address_out':'address_memory_alu',
        'alu_memory_write_en_out':'write_en_memory',
        'alu_regfile_write_en_out':'write_en_regfile',
        'alu_regfile_address_out':'register_file_addr_dest',
        'cu_alu_interface':'cu_alu_interface',
        'alu_fetch_interface':'alu_fetch_interface'
    }
    ModuleALU(cpu_spec=cpu_spec, PORTS=ports_alu)
    
    #/ always #5 clk = ~clk;
    
    #/ initial begin
    #/   clk = 0;
    #/   rst = 1;
    #/   #10 rst = 0;
    #/ end
    instruction_memory_list = [
    '1000_0000_0000_1000_0000_0000_0000_0000',    # R0 = 0xF
    '0000_0001_0000_0000_0000_0001_0000_0000',    # R0 = 0xF+2 = 0x11
    '0000_0010_0000_0010_0000_0000_0000_0000',    # R0 = 3-0x11 = FFF2
    '0000_0001_0000_1000_0000_0000_0000_0001',    # R1 = R0 + R8 = 0xFFF2 + 0x0009
    '0100_0000_0001_0000_0000_0000_0000_0000',    # JUMP to I8
    '0000_0001_0000_0000_0000_0010_0000_0000',
    '0000_0001_0000_0000_0000_0001_0000_0000',
    '0000_0001_0000_0000_0000_0010_0000_0000',     
    '1000_0001_0000_0000_0000_0000_0000_0000',    # mem[0] <= R0
    '0110_0000_0000_0011_0000_0011_0000_0100',    # JUMP to I2
    '0000_0001_0000_0000_0000_0001_0000_0000',
    '0000_0001_0000_0000_0000_0010_0000_0000',
    '0000_0001_0000_0000_0000_0001_0000_0000',
    '0000_0001_0000_0000_0000_0010_0000_0000'
    ]
    
    instruction_memory_list = [
    '1000_0000_0000_1000_0000_0000_0000_0010',    # R2 = mem[8] = 0xF
    '0000_0001_0000_0000_0000_0001_0000_0000',    # R0 = R0 + R1 = 1 + 2 = 3 ----> R0 = 0xC
    '0000_0010_0000_0010_0000_0000_0000_0000',    # R0 = R2 - R0 = 0xF - 3 = 0xC ----> R0 = 0xF - 0xC = 3 -----> R0 = 0xC
    '0000_0001_0000_1000_0000_0000_0000_0001',    # R1 = R0 + R8 = 0xC + 0xA = 0x16 -----> R1 = 3 + 0xA = 0xD ------> R1 = 0x16
    '0100_0000_0001_0000_0000_0000_0000_0000',    # JUMP to I8
    '0000_0001_0000_0000_0000_0010_0000_0000',
    '0000_0001_0000_0000_0000_0001_0000_0000',
    '0000_0001_0000_0000_0000_0010_0000_0000',     
    '1000_0001_0000_0000_0000_0000_0000_0000',    # mem[0] <= R0 (0x16) -----> 0x0003 ------> 0x3
    '0110_0000_0000_0011_0000_0011_0000_0100',    # JUMP to I2 
    '0000_0001_0000_0000_0000_0001_0000_0000',
    '0000_0001_0000_0000_0000_0010_0000_0000',
    '0000_0001_0000_0000_0000_0001_0000_0000',
    '0000_0001_0000_0000_0000_0010_0000_0000'
    ]
    
    
    instruction_memory_list = [
    '0010_0001_0000_0000_0110_0000_0000_0000',    # R0 = R0 + 0x60 (imm add)   // 0
    '1000_0001_0000_0000_0000_0001_0000_0000',    # mem[1] <= R0 (0x61) (store reg)    // 1
    '0000_0010_0000_0000_0000_0010_0000_0000',    # R0 = R0 - R2 (reg sub)   // 2  0x61 - 3 = 0x5E  // 0xF2 - 3 = 0xEF
    '0100_0000_0001_0000_0000_0000_0000_0000',    # JUMP to I8  // 3
    '0000_0001_0000_0000_0000_0010_0000_0000',
    '0000_0001_0000_0000_0000_0001_0000_0000',
    '0000_0001_0000_0000_0000_0010_0000_0000',     
    '1000_0001_0000_0000_0000_0000_0000_0000',    # mem[0] <= R0 (0x16) -----> 0x0003 ------> 0x3 // 8 mem[0]  = 0x5E
    '0000_0010_0000_0000_0000_0010_0000_0000',    # R0 = R0 - R2 (reg sub)  // 9  0x5E - 3 = 0x5B
    '1001_0001_1111_0000_0000_0000_0000_0000',    # mem[0] <= 0xF0(store imm)   // 10  // mem[0] = 0xF0
    '0010_0001_0000_0000_0110_0000_0000_0000',    # R0 = R0 + 0x60 (imm add)   // 11  R0 = 0x5B + 0x60 = 91 + 96 = 187 = 0xBB
    '0001_0001_0000_0000_0000_0001_0000_0000',    # R0 = mem[0] + R1 (mem-reg add)  // 12  R0 = 0xF0 + 2 = 0xF2
    '0110_0000_0000_0011_0000_0011_0000_0100',    # JUMP to I2 // 13
    '0000_0001_0000_0000_0000_0001_0000_0000',
    '0000_0001_0000_0000_0000_0010_0000_0000',
    '0000_0001_0000_0000_0000_0001_0000_0000',
    '0000_0001_0000_0000_0000_0010_0000_0000'
    ]
    # instruction_memory_list = [
    # 'add, rs1[1], rs2[2], rd[3]',
    # 'add, mem[1], rs2[3], rd[4]',
    # 'sub, rs1[1], rs2[2], rd[3]',
    # 'load, mem[1], rd[4]',
    # 'jump, 8',
    # 'store, rs1[1], mem[2]'
    # ]
    # my_assemble = assemble(instruction_memory_list)
    
    
    # print(my_assemble)
    
    #/ initial begin
    for i in range(len(instruction_memory_list)):
        #/ u_0000000001_InstrMem0000000001.mem[`i`] = `cpu_spec.instruction_data_width`'b`instruction_memory_list[i]`;
        pass
        
        
    
    
    micro_instruction_memory_dict = {
    '0' : '16\'b0001_0000_1100_0001',
    '1' : '16\'b0010_0000_1100_0001',
    '2' : '16\'b0011_0000_1100_0000',
    '3' : '16\'b0100_0000_1100_0000',
    '4' : '16\'b0101_0000_1100_0000',
    '4' : '16\'b0101_0000_1100_0000',
    '5' : '16\'b0110_0000_1100_0000',
    '6' : '16\'b0111_0000_1100_0000',
    '7' : '16\'b1000_0000_1100_0000',
    '8' : '16\'b0000_1000_0001_0001',
    '9' : '16\'b0000_0000_0000_1001',
    '9' : '16\'b0000_0000_0000_1001',
    '10' : '16\'b0001_0010_0100_0001',
    '11' : '16\'b0000_1000_0001_0001',
    '12' : '16\'b0000_0000_0000_1001',
    '12' : '16\'b0000_0000_0000_1001',
    '13' : '16\'b0010_0010_0100_0001',
    '14' : '16\'b0000_1000_0001_0001',
    '15' : '16\'b0000_0000_0000_1001',
    '15' : '16\'b0000_0000_0000_1001',
    '16' : '16\'b0011_0010_0100_0001',
    '17' : '16\'b0000_1000_0001_0001',
    '18' : '16\'b0000_0000_0000_1001',
    '18' : '16\'b0000_0000_0000_1001',
    '19' : '16\'b0100_0010_0100_0001',
    '20' : '16\'b0000_1000_0001_0001',
    '21' : '16\'b0000_0000_0000_1001',
    '22' : '16\'b0101_0010_0100_0001',
    '23' : '16\'b0000_1000_0001_0001',
    '24' : '16\'b0000_0000_0000_1001',
    '25' : '16\'b0110_0010_0100_0001',
    '26' : '16\'b0000_1000_0001_0001',
    '27' : '16\'b0000_0000_0000_1001',
    '28' : '16\'b0111_0010_0100_0001',
    '29' : '20\'b0010_0000_1000_0001_0000',
    '30' : '20\'b0000_0000_0000_0000_1000',
    '31' : '20\'b0001_0000_0010_0000_0001',
    '32' :  '16\'b0000_0100_1001_0100',
    '33' : '16\'b0000_0000_0000_0010',
    '34' : '16\'b0000_0000_0000_0000',
    '36' : '16\'b1100_0000_1100_0000',
    '255' : '16\'b0000_0000_0000_0000',
    }
    
    
    # for index in micro_instruction_memory_dict.keys():
    #     data = micro_instruction_memory_dict[index]
    #     #/ u_0000000001_MicroInstrMem0000000001.mem[`index`] = `data`;
    #     pass
    
    # enumerate micro_code_list
    address = 0
    for index, micro_code_group in enumerate(cpu_spec.micro_code_list):
        if micro_code_group is None:
            break
        #/ // `cpu_spec.comments_list[index]`;
        if micro_code_group is not None:
            for micro_code in micro_code_group:
                if micro_code is not None:
                    #/ u_0000000001_MicroInstrMem0000000001.mem[`address`] = `micro_code`;
                    address += 1
    
    #/ u_0000000001_MicroInstrMem0000000001.mem[255] = 16'b0000_0000;
        
    
    external_memory_list = [
    "0000_0001",
    "0001_0010",
    "0010_0000",
    "0000_0100",
    "0000_0101",
    "0000_0110",
    "0000_0111",
    "0000_1000",
    "0000_1111",
    "0000_1010",
    "0000_1011"
    ]
    
    for i in range(len(external_memory_list)):
        #/ u_0000000001_ExternalMem0000000001.mem[`i`] = `cpu_spec.external_mem_data_width`'b`external_memory_list[i]`;
        pass
    
    register_file_memory_list = [
    "0000_0000_0000_0001",
    "0000_0000_0000_0010",
    "0000_0000_0000_0011",
    "0000_0000_0000_0101",
    "0000_0000_0000_0110",
    "0000_0000_0000_0111",
    "0000_0000_0000_1000",
    "0000_0000_0000_1001",
    "0000_0000_0000_1010",
    "0000_0000_0000_1011",
    "0000_0000_0000_1100",
    "0000_0000_0000_1101",
    "0000_0000_0000_1110",
    "0000_0000_0000_1111",
    "0000_0000_0001_0000",
    "0000_0000_0001_0001",
    "0000_0000_0001_0010",
    "0000_0000_0001_0011"
    ]
    
    for i in range(len(register_file_memory_list)):
        #/ u_0000000001_RegisterFile0000000001.mem[`i`] = `cpu_spec.register_file_data_width`'b`register_file_memory_list[i]`;
        pass
    
    #/ end
    
    
    #/ initial begin
    #/     $dumpfile("wave.vcd"); 
    #/     $dumpvars(0, CPUTop0000000001);
    #/     #2500
    #/     $finish;
    #/ end
    #/ endmodule
    pass
    
    
moduleloader.set_naming_mode('SEQUENTIAL')  
moduleloader.set_root_dir('RTL_GEN_NEW')
moduleloader.set_debug_mode(True)
ModuleCPUTop(cpu_spec=my_cpu_spec)



import os

# 定义目标文件夹路径（默认当前目录）
folder_path = 'RTL_GEN_NEW'
# 定义输出的新文件名
output_filename = 'cpu_tb.v'

# 获取所有文件（排除目录和输出文件自身）
file_list = [
    f for f in os.listdir(folder_path)
    if os.path.isfile(os.path.join(folder_path, f)) and f != output_filename
]

# 按文件名排序（可选，根据需求决定是否保留）
file_list.sort()

# 写入合并内容
with open(os.path.join(folder_path, output_filename), 'w', errors='ignore') as outfile:
    for filename in file_list:
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', errors='ignore') as infile:
            outfile.write(f"// === Contents from: {filename} ===\n")
            outfile.write(infile.read())
            outfile.write("\n\n")  # 添加两个换行作为文件分隔符



