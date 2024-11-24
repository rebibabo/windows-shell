import argparse
import os
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text
from cmds.base import Command

normabs = lambda x: os.path.normpath(os.path.abspath(x.replace('~', os.path.expanduser('~'))))


@dataclass
class TailCommand(Command):
    def __init__(self, command: str) -> 'TailCommand':
        """
        解析 tail 命令并返回 TailCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Display the last N lines of each FILE.", add_help=False)
        parser.add_argument("-n", "--lines", type=int, default=10, help="Number of lines to display (default: 10)")
        parser.add_argument("files", nargs="*", type=str, help="Files to display")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self, stream=None):
        if stream:
            # 从流中读取内容
            lines = stream.readlines()
            self._print_lines(lines)
        else:
            if not self.files:
                print_formatted_text(HTML("<error>Error: No files specified and no input stream provided.</error>"), style=self.log_style)
                return

            for file_path in self.files:
                file_path = normabs(file_path)
                file_lists = self.get_file_list(file_path)

                if not file_lists:
                    print_formatted_text(HTML(f"<error>Error: File '{file_path}' does not exist or is not a file.</error>"), style=self.log_style)
                    continue

                for file in file_lists:
                    print_formatted_text(HTML(f"<aaa bg='ansiblue'>{file}:</aaa>"))
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            self._print_lines(lines)
                    except Exception as e:
                        print_formatted_text(HTML(f"<critical>Critical Error: Failed to read file '{file}': {e}</critical>"), style=self.log_style)

    def _print_lines(self, lines):
        """
        打印最后 N 行内容。
        """
        for line in lines[-self.lines:]:
            print(line.rstrip())

if __name__ == "__main__":
    command = "-n 5 *.py"  # 示例命令
    tail_command = TailCommand(command)
    tail_command.execute()
