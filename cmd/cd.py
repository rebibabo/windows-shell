import argparse
import os      
import re
from prompt_toolkit import HTML, print_formatted_text as print
from cmd.base import Command

class CdCommand(Command):

    def __init__(self, command: str) -> 'CdCommand':
        """
        解析 cd 命令并返回 CdCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Change the current directory.", add_help=False)
        parser.add_argument("directory", type=str, help="Target directory to change to")
        
        self.parser = parser
        super().__init__(command)

    def execute(self):
        target_directory = self.directory
        if target_directory.endswith('\\') or target_directory.endswith('/'):
            target_directory = target_directory[:-1]
        
        # 处理 ~ 符号
        if target_directory.startswith('~'):
            target_directory = os.path.expanduser(target_directory)

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
            print(HTML(f"<success>Changed directory to: '{target_directory}'</success>"), style=self.log_style)
        except Exception as e:
            print(HTML(f"<critical>Critical Error: Failed to change directory to '{target_directory}': {e}</critical>"), style=self.log_style)

# 示例用法
if __name__ == "__main__":
    command = "__pyca*he__"  # 示例命令
    cd_command = CdCommand(command)
    cd_command.execute()