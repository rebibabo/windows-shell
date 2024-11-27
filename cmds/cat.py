import argparse
import os
from prompt_toolkit import HTML, print_formatted_text as print
from cmds.base import Command

class CatCommand(Command):

    def __init__(self, command: str) -> 'CatCommand':
        """
        解析 cat 命令并返回 CatCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Concatenate and display file content.", add_help=False)
        parser.add_argument("-n", "--number", action="store_true", help="Number all output lines")
        parser.add_argument("-b", "--number-nonblank", action="store_true", help="Number only non-blank output lines")
        parser.add_argument("-E", "--show-ends", action="store_true", help="Display $ at the end of each line")
        parser.add_argument("files", nargs="*", type=str, help="Files to concatenate and display")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        if not self.files:
            print(HTML("<error>Error: No files specified.</error>"), style=self.log_style)
            return

        for file_path in self.files:
            file_path = self.normabs(file_path)
            
            # 检查文件是否存在
            if not os.path.isfile(file_path):
                print(HTML(f"<error>Error: File '{file_path}' does not exist or is not a file.</error>"), style=self.log_style)
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                line_number = 1
                for line in lines:
                    if self.number or (self.number_nonblank and line.strip()):
                        line_prefix = f"{line_number:6}  "  # 右对齐的行号格式
                        line_number += 1
                    else:
                        line_prefix = ""

                    line_content = line.rstrip("\n") + ("$" if self.show_ends else "")
                    print(HTML(f"{line_prefix}{line_content}"))

            except Exception as e:
                print(HTML(f"<critical>Critical Error: Failed to read file '{file_path}': {e}</critical>"), style=self.log_style)
        
# 示例用法
if __name__ == "__main__":
    command = "-n history.txt"  # 示例命令
    cat_command = CatCommand(command)
    cat_command.execute()
