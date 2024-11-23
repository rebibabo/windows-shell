import argparse
import os
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text as print
from cmd.base import Command

@dataclass
class PwdCommand(Command):
    def __init__(self, command: str) -> 'PwdCommand':
        """
        解析 pwd 命令并返回 PwdCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Print the current working directory.", add_help=False)
        parser.add_argument("-L", "--logical", action="store_true", help="Use PWD from the environment, even if it contains symbolic links")
        parser.add_argument("-P", "--physical", action="store_true", help="Avoid all symbolic links (default)")
        
        self.parser = parser
        super().__init__(command)

    def execute(self):
        """
        执行 pwd 命令逻辑。
        """

        # 获取当前工作目录
        if self.logical:
            # 从环境变量中获取 PWD（可能包含符号链接）
            pwd = os.getenv("PWD", os.getcwd())
        else:
            # 获取实际的物理路径
            pwd = os.path.realpath(os.getcwd())

        # 打印工作目录
        print(pwd, style=self.log_style)

# 示例用法
if __name__ == "__main__":
    command = "-LP"  # 示例命令
    pwd_command = PwdCommand(command)
    pwd_command.execute()
