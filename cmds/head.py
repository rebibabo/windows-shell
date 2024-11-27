import argparse
import os
from prompt_toolkit import HTML, print_formatted_text as print
from cmds.base import Command

class HeadCommand(Command):
    def __init__(self, command: str) -> 'HeadCommand':
        """
        解析 head 命令并返回 HeadCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Display the first N lines of each FILE.", add_help=False)
        parser.add_argument("-n", "--lines", type=int, default=10, help="Number of lines to display (default: 10)")
        parser.add_argument("files", nargs="*", type=str, help="Files to display")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self, input_lines=None):
        if input_lines:
            # 从流中读取内容
            self._print_lines(input_lines)
        else:
            if not self.files:
                print(HTML("<error>Error: No files specified and no input stream provided.</error>"), style=self.log_style)
                return

            for file_path in self.files:
                file_path = self.normabs(file_path)
                file_lists = self.get_file_list(file_path)

                if not file_lists:
                    print(HTML(f"<error>Error: File '{file_path}' does not exist or is not a file.</error>"), style=self.log_style)
                    continue

                for file in file_lists:
                    print(HTML(f"<aaa bg='ansiblue'>{file}:</aaa>"))
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            self._print_lines(lines)
                    except Exception as e:
                        print(HTML(f"<critical>Critical Error: Failed to read file '{file}': {e}</critical>"), style=self.log_style)

    def _print_lines(self, lines):
        """
        打印前 N 行内容。
        """
        for line in lines[:self.lines]:
            print(line.rstrip())

if __name__ == "__main__":
    command = "-n 5 head.py"  # 示例命令
    head_command = HeadCommand(command)
    head_command.execute()
    
    input_data = """
    def my_function():
        pass

    class MyClass:
        def __init__(self):
            pass

    def another_function():
        return "hello"
    """
    import io
    
    stream = io.StringIO(input_data)

    command = "-n 5"
    grep_command = HeadCommand(command)
    grep_command.execute(stream=stream)
