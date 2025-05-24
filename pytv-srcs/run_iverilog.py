import os
import subprocess

def run_iverilog_flow():
    # 设置目标工作目录
    target_dir = r"D:\\ChannelCoding\\AutoGen\\Verilog\\Pipelined-Microprogrammed-CPU\\RTL_GEN_OOD_NEW"
    
    try:
        # 1. 切换工作目录
        os.chdir(target_dir)
        print(f"切换到目录: {os.getcwd()}")
        
        # 2. 使用iverilog编译
        compile_cmd = ["iverilog", "-o", "wave", "cpu_tb.v"]
        print("正在编译...")
        subprocess.run(compile_cmd, check=True)
        
        # 3. 使用vvp进行仿真
        simulate_cmd = ["vvp", "-n", "wave", "-lxt2"]
        print("正在仿真...")
        subprocess.run(simulate_cmd, check=True)
        
        # 4. 使用gtkwave查看波形
        print("打开波形文件...")
        gtkwave_cmd = ["gtkwave", "wave.vcd"]
        subprocess.Popen(gtkwave_cmd, shell=True)
        
    except FileNotFoundError as e:
        print(f"路径不存在: {e.filename}")
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e.cmd}")
    except Exception as e:
        print(f"发生未知错误: {str(e)}")

if __name__ == "__main__":
    run_iverilog_flow()