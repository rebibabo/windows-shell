import argparse
import os
import re
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text
from cmds.base import Command

normabs = lambda x: os.path.normpath(os.path.abspath(x.replace('~', os.path.expanduser('~'))))

@dataclass
class GrepCommand(Command):
    def __init__(self, command: str) -> 'GrepCommand':
        """
        解析 grep 命令并返回 GrepCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Search for PATTERN in each FILE.", add_help=False)
        parser.add_argument("-i", "--ignore-case", action="store_true", help="Ignore case distinctions in patterns and data")
        parser.add_argument("-v", "--invert-match", action="store_true", help="Select non-matching lines")
        parser.add_argument("-n", "--line-number", action="store_true", help="Prefix each line of output with the line number")
        parser.add_argument("-e", "--regexp", type=str, required=True, help="PATTERN to search for")
        parser.add_argument("files", nargs="*", type=str, help="Files to search")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self, stream=None):
        try:
            # 编译正则表达式，支持忽略大小写选项 dpf def
            pattern = re.compile(self.regexp, re.IGNORECASE if self.ignore_case else 0)
        except re.error as e:
            print_formatted_text(HTML(f"<error>Error: Invalid regular expression '{self.regexp}': {e}</error>"), style=self.log_style)
            return

        if stream:
            lines = stream.readlines()
            self._process_lines(lines, pattern)
        else:
            if not self.files:
                print_formatted_text(HTML("<error>Error: No files specified.</error>"), style=self.log_style)
                return
            
            for file_path in self.files:
                file_path = normabs(file_path)
                file_lists = self.get_file_list(file_path)
                # 检查文件是否存在
                if not file_lists:
                    print_formatted_text(HTML(f"<error>Error: File '{file_path}' does not exist or is not a file.</error>"), style=self.log_style)
                    continue

                for file in file_lists:
                    print_formatted_text(HTML(f"<aaa bg='ansiblue'>{file}:</aaa>"))
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            self._process_lines(lines, pattern)
                    except Exception as e:
                        print_formatted_text(HTML(f"<critical>Critical Error: Failed to read file '{file}': {e}</critical>"), style=self.log_style)
                        
    def _process_lines(self, lines, pattern):
        """
        处理输入的行，根据正则表达式匹配并输出结果。
        """
        for line_number, line in enumerate(lines, start=1):
            match = bool(pattern.search(line))  # 检查是否匹配
            if self.invert_match:
                match = not match  # 反转匹配结果

            if match:
                prefix = f"{line_number:6}  " if self.line_number else ""
                if self.invert_match:
                    print(f"{prefix}{line.rstrip()}")
                else:
                    print(prefix, end='')
                    idx = 0
                    for m in pattern.finditer(line):
                        l, r = m.span()
                        print(line[idx: l], end='')
                        print_formatted_text(HTML(f"<aaa bg='ansired'>{line[l:r]}</aaa>"), end='')
                        idx = r
                    print(line[idx:], end='')

# 示例用法
if __name__ == "__main__":
    import io
    command = "-e d.f -n *.py"  # 示例命令
    grep_command = GrepCommand(command)
    grep_command.execute()
    
    print("="*100)
    input_data = """
    def my_function():
        pass

    class MyClass:
        def __init__(self):
            pass

    def another_function():
        return "hello"
    """
    stream = io.StringIO(input_data)

    command = "-e def"
    grep_command = GrepCommand(command)
    grep_command.execute(stream=stream)
