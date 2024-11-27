import argparse
import os      
import re
from prompt_toolkit import HTML, print_formatted_text as print
from cmds.base import Command

class CdCommand(Command):
    last_path = None  # 记录上一次的路径，用于 cd - 功能
    def __init__(self, command: str) -> 'CdCommand':
        """
        解析 cd 命令并返回 CdCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Change the current directory.", add_help=False)
        parser.add_argument("directory", nargs="*", type=str, help="Target directory to change to")     # 如果有空格的话，会拆分为不同的参数
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        target_directory = ' '.join(self.directory) # 在这里把参数列表拼接成字符串
        if target_directory.endswith('\\') or target_directory.endswith('/'):
            target_directory = target_directory[:-1]
        
        # 处理 ~ 符号
        if target_directory.startswith('~'):
            target_directory = os.path.expanduser(target_directory)

        # 处理 - 符号
        if target_directory == '-':
            if CdCommand.last_path is None:
                CdCommand.last_path = os.getcwd()
                print(HTML(f"<error>Error: No previous directory to go back to.</error>"), style=self.log_style)
                return
            else:
                target_directory = CdCommand.last_path
        CdCommand.last_path = os.getcwd()

        # 正则匹配支持
        if '*' in target_directory or '?' in target_directory:
            current_dir = os.getcwd()
            target_directory_regex = re.escape(target_directory).replace(r'\*', '.*').replace(r'\?', '.')
            matched_dirs = [d for d in os.listdir(current_dir) if re.match(target_directory_regex, d)]
            if matched_dirs:
                target_directory = os.path.join(current_dir, matched_dirs[0])  # 使用第一个匹配的目录
            else:
                print(HTML(f"<error>Error: No matching directories found for '{self.directory}'.</error>"), style=self.log_style)
                return

        # 获取绝对路径
        target_directory = os.path.normpath(os.path.abspath(target_directory))

        # 检查目标目录是否存在
        if not os.path.isdir(target_directory):
            print(HTML(f"<error>Error: Directory '{target_directory}' does not exist.</error>"), style=self.log_style)
            return

        # 切换目录
        try:
            os.chdir(target_directory)
            # print(HTML(f"<success>Changed directory to: '{target_directory}'</success>"), style=self.log_style)
        except Exception as e:
            print(HTML(f"<critical>Critical Error: Failed to change directory to '{target_directory}': {e}</critical>"), style=self.log_style)

# 示例用法
if __name__ == "__main__":
    command = "__pyca*he__"  # 示例命令
    cd_command = CdCommand(command)
    cd_command.execute()