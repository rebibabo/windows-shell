import os
import io
import sys
from prompt_toolkit import prompt

commands = []
cur_dir = os.path.dirname(__file__)
for file in os.listdir(cur_dir):
    file_path = os.path.join(cur_dir, file)
    if os.path.isfile(file_path) and file.endswith('.py') and file not in ['base.py', '__init__.py']:
        commands.append(file[:-3])

for command in commands:
    exec(f"from cmds.{command} import {command.capitalize()}Command")

class Cmd:
    # def __init__(self, cmd):
    #     type = cmd.split()[0]                  
    #     command = ' '.join(cmd.split()[1:])
    #     if type in commands:
    #         try:
    #             command = eval(f"{type.capitalize()}Command(command)")
    #             command.execute()
    #         except:
    #             pass
    #     else:
    #         os.system(cmd)
    
    def __init__(self, cmd):
        # 解析命令，判断是否有管道符
        if '|' in cmd:
            self._handle_pipe(cmd)
        else:
            self._execute_single_command(cmd, input_stream=None, last=True)
            
    def _handle_pipe(self, cmd):
        # 按照管道符分割命令
        sub_commands = cmd.split('|')
        
        # 初始化第一个命令的输入流为 None
        input_stream = None
        for i, sub_cmd in enumerate(sub_commands):
            sub_cmd = sub_cmd.strip()  # 去除多余的空格
            is_last = (i == len(sub_commands) - 1)  # 判断是否是最后一条命令
            # 使用 StringIO 捕获前一个命令的输出
            input_stream = self._execute_single_command(sub_cmd, input_stream=input_stream, last=is_last)
    
    def _execute_single_command(self, cmd, input_stream=None, last=False):
        if len(cmd.split()) == 0:
            return None  # 空命令不执行
        type = cmd.split()[0]
        command = ' '.join(cmd.split()[1:])
        
        # 如果当前命令是最后一个命令，输出到标准输出
        if not last:
            original_stdout = sys.stdout
            output_stream = io.StringIO()
            sys.stdout = output_stream  # 否则将输出重定向到 StringIO 缓存
        
        # 执行命令
        if type in commands:
            try:
                # 如果有输入流，就传递给 execute 的 stream 参数
                command_class = eval(f"{type.capitalize()}Command(command)")
                # 判断command_class.execute是否有stream参数，如果有就传递input_stream
                if 'stream' in command_class.execute.__code__.co_varnames:
                    command_class.execute(stream=input_stream)
                else:
                    command_class.execute()
            except Exception as e:
                print(f"Error executing command '{type}': {e}")
        else:
            # 如果命令不是我们定义的，则直接执行 shell 命令
            os.system(cmd)
        
        # 恢复标准输出
        if not last:
            sys.stdout = original_stdout
            print("yewfweh")
            prompt(output_stream.getvalue())
            return io.StringIO(output_stream.getvalue())
        return None  # 最后一条命令不返回任何流，因为它的输出直接打印到标准输出