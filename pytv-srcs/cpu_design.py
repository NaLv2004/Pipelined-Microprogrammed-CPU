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
    #/ wire is_micro_code_conflict;
    #/ wire is_micro_code_dependent;
    #/ assign is_micro_code_conflict = (| (micro_code_speculative[`cpu_spec.micro_instruction_data_width-1`:0] & micro_code_normal[`cpu_spec.micro_instruction_data_width-1`:0])) ? 1'b1:
    #/                               (| micro_code_normal[11:5]) ? 1'b1 : 1'b0;
    #/ aassign is_micro_code_dependent = (instruction_speculative[23:16]==instruction_normal[7:0])|(instruction_speculative[15:8]==instruction_normal[7:0]);
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
    ModuleOneBitBranchPredictor(cpu_spec=cpu_spec, PORTS = ports_one_bit_branch_predictor)
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
        low_bit = cpu_spec.idecode_cu_interface[fetch_port][0]
        high_bit = cpu_spec.idecode_cu_interface[fetch_port][1]
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
    #/ assign opcode = instr[2:0];  // 假设操作码在低3位
    #/ assign rs1 = instr[7:3];     // 源寄存器1
    #/ assign rs2 = instr[12:8];    // 源寄存器2
    #/ assign rd = instr[15:13];    // 目的寄存器（示例位置）
    #/ assign micro_code = micro_code_reg;
    #/ assign instr_address_not_taken_de_cu = instr_address_not_taken_fe_de;
    #/ assign branch_prediction_result_de_cu = branch_prediction_result_fe_de;
    #/ assign branch_instr_address_de_cu = branch_instr_address_fe_de;
    #/ assign micro_code_addr_out = 
    #/     (flush_pipeline==1'b1) ? 8'b1111_1111 : // flush pipeline (no operations)
    #/     (instr[31:24] == 8'b00000000) ? 8'b1111_1111 : // addi)
    #/     (instr[31:24] == 8'b00000001) ? 8'b0000_0000 : // add
    #/     (instr[31:24]== 8'b00010001) ? 8'b0000_1000 : // add, first source operand is from memory
    #/    // (instr[31:24] == 8'b10000000) ? 8'b0000_0001 : // load
    #/     (instr[31:24] == 8'b00000011) ? 8'b0000_0010 : // add
    #/     (instr[31:24] == 8'b00000010) ? 8'b0000_0001 : // sub
    #/     (instr[31:24] == 8'b00000101) ? 8'b0000_0100 : // jmpgez
    #/     (instr[31:24] == 8'b10000000) ? 8'b0001_1101 :  // load
    #/     (instr[31:24] == 8'b10000001) ? 8'b0010_0000 : // store
    #/     (instr[31:24] == 8'b01000000) ? 8'b0010_0010 : // jal (unconditional branch) 
    #/     (instr[31:24] == 8'b01100000) ? 8'b0010_0100 : // beq
    #/     8'b1111_1111;  // default
    #/ //assign micro_code_addr_out = instr[31:24];
    #/ // counter: n of micro codes following this address
    #/ assign micro_code_cnt_out = 
    #/     (flush_pipeline==1'b1) ? 3'b000 : // flush pipeline (no operations)
    #/     (instr[31:24] == 8'b0000_0000) ? 3'b000 : // addi)
    #/     (instr[31:24] == 8'b0000_0011) ? 3'b010 :
    #/     (instr[31:24] == 8'b0001_0001) ? 3'b010 : // add, first source operand is from memory
    #/     (instr[31:24] == 8'b1000_0000) ? 3'b010 : // load
    #/     (instr[31:24] == 8'b1000_0001) ? 3'b001 : // store
    #/     3'b000;                   
    #/ // 控制信号寄存器
    #/ always @(posedge clk or posedge rst) begin
    #/     if (rst) begin
    #/         ready_reg <= 1'b0;
    #/     end else begin
    #/         // 简单示例：始终准备接收指令
    #/         ready_reg <= 1'b1;
    #/         // instr_out_reg <= instr;
    #/         // 更复杂的控制示例：
    #/         // if (pipeline_stall_condition) 
    #/         //     ready_reg <= 1'b0;
    #/         // else
    #/         //     ready_reg <= 1'b1;
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
    #/     input  [`micro_instruction_data_width-1`:0] micro_code_in_normal,
    #/     input  [`micro_instruction_data_width-1`:0] micro_code_in_speculative,
    #/     input  [`idecode_cu_interface_width-1`:0] idecode_cu_interface,
    #/     output [`cu_alu_interface_width-1`:0] cu_alu_interface,
    #/     output o_exec_ready_combined,
    #/     output o_exec_ready_normal
    #/     );
    #/ wire clk;
    #/ wire rst;
    #/ wire flush_pipeline;
    #/ wire o_exec_ready_combined;
    #/ wire o_exec_ready_normal;
    #/ wire [`micro_instruction_data_width-1`:0] micro_code_in_normal;
    #/ wire [`micro_instruction_data_width-1`:0] micro_code_in_speculative;
    #/ wire [`idecode_cu_interface_width-1`:0] idecode_cu_interface;
    #/ wire [`cu_alu_interface_width-1`:0] cu_alu_interface;
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
    #/ wire clk;
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
    #/ assign o_exec_combined = o_exec_ready_normal | o_exec_ready_speculative_fetch;
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
    
# // when reading from memory from is required
# assign alu_memory_address_out = (micro_code[11:11] == 1'b1) ?  instruction_choosed[23:16]: 
#                                 (micro_code[10:10] == 1'b1) ? instruction_choosed[15:8]: 8'b0000_0000; 


# // assign alu input operands
# assign alu_operand_1 = (micro_code[9:9] == 1'b1) ?  alu_memory_in: 
#                        (micro_code[7:7] == 1'b1) ? alu_regfile_in_1: 16'b0;

# assign alu_operand_2 = (micro_code[8:8] == 1'b1) ?  alu_memory_in:
#                        (micro_code[6:6] == 1'b1) ? alu_regfile_in_2: 
#                        (micro_code[5:5] == 1'b1) ? instruction_choosed[7:0] : 16'b0;

# // write enable for register file
# assign alu_regfile_write_en_out = (micro_code[0:0]==1'b1) ? 1'b1: 1'b0;

# // assign address
# assign alu_regfile_address_out = instruction_choosed[7:0];

# // write enable for memory
# assign alu_memory_write_en_out = (micro_code[1:1]==1'b1) ? 1'b1: 1'b0;

                    

# adder u_adder(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_add_result));
# subtractor u_subtractor(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_sub_result));
# xorer u_xorer(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_xor_result));
# ander u_ander(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_and_result));
# orer u_orer(.op_1(alu_operand_1),.op_2(alu_operand_2),.result(alu_or_result));
# judge_equal u_judge_equal(.op_1(alu_operand_1), .op_2(alu_operand_2), .result(alu_judge_equal_result));

# // select operation based on micro-code
# assign alu_result = (micro_code[15:12] == 4'b0001) ? alu_add_result:
#                     (micro_code[15:12] == 4'b0010) ? alu_sub_result:
#                     (micro_code[15:12] == 4'b0011) ? alu_xor_result:
#                     (micro_code[15:12] == 4'b0100) ? alu_and_result:
#                     (micro_code[15:12] == 4'b0101) ? alu_or_result:   // 16'b0 is default value
#                     (micro_code[15:12] == 4'b0000) ? alu_operand_1: // load
#                     (micro_code[15:12] == 4'b1100) ? alu_judge_equal_result: // beq
#                     16'b0;

# // assign flush_pipeline_out = (instruction[31:28]==4'b0110  && alu_result == branch_prediction_result_cu_alu) ? alu_result : 1'b0;
# // send flush pipeline signal to fetch when branch prediction fails
# assign is_conditional_branch_alu_fe = (instruction_choosed[31:28]==4'b0110) ? 1'b1: 1'b0;
# assign flush_pipeline_out = (!(instruction_choosed[31:28]==4'b0110)) ? 1'b0: 
#                             (alu_result == branch_prediction_result_cu_alu) ? 1'b0: 1'b1;
# assign instr_address_not_taken_alu_fe = instr_address_not_taken_cu_alu;
# assign branch_instr_address_alu_fe = branch_instr_address_cu_alu;
# assign branch_taken_alu_fe = (!(instruction_choosed[31:28]==4'b0110)) ? 1'b0:
#                              (alu_result) ? 1'b1: 1'b0;

# // inner registers
# reg [31:0] micro_code_reg;
# always @ (posedge clk)
# begin
#     micro_code_reg <= micro_code;
#     if (micro_code[17:17])
#     begin
#         instruction_pipeline <= instruction;
#     end
# end

# // behaviour according to micro-code
# always @ (posedge clk)
# begin
#     if (micro_code_reg == 16'b0)
#     begin
#         alu_result_reg <= alu_regfile_in_1 + alu_regfile_in_2;
#     end
# end 

# the following pytv function is based on the above verilog code.
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
    #/ // assign inner wires to alu_fe_interface ports (output)
    for alu_output_port in cpu_spec.alu_fe_interface.keys():
        low_bit = cpu_spec.alu_fe_interface[alu_output_port][0]
        high_bit = cpu_spec.alu_fe_interface[alu_output_port][1]
        port_width = high_bit - low_bit + 1
        #/ wire [`port_width-1`:0] `alu_output_port`;
        #/ assign alu_fe_interface[`high_bit`:`low_bit`] = `alu_output_port`;
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
    #/ wire [`instruction_data_width-1`:0] instruction_choosed;
    #/ assign instruction_choosed = (micro_code[16:16])? instruction_pipeline :instruction;
    #/ assign alu_regfile_out_1 = instruction_choosed[23:16];
    #/ assign alu_regfile_out_2 = instruction_choosed[15:8];
    #/ assign alu_memory_address_out = (micro_code[11:11] == 1'b1) ?  instruction_choosed[23:16]: 
    #/                                 (micro_code[10:10] == 1'b1) ? instruction_choosed[15:8]: 8'b0000_0000; 
    #/ assign alu_operand_1 = (micro_code[9:9] == 1'b1) ?  alu_memory_in: 
    #/                        (micro_code[7:7] == 1'b1) ? alu_regfile_in_1: 16'b0;
    #/ assign alu_operand_2 = (micro_code[8:8] == 1'b1) ?  alu_memory_in:
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
    ports_equal = {'op_1':'alu_operand_1','op_2':'alu_operand_2','result':'judge_equal_result'}
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
    #/ assign is_conditonal_branch_alu_fe = (instruction_choosed[31:28]==4'b0110) ? 1'b1: 1'b0;
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

