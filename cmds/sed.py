import argparse
import re
import os
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text
from cmds.base import Command

normabs = lambda x: os.path.normpath(os.path.abspath(x.replace('~', os.path.expanduser('~'))))

@dataclass
class SedCommand(Command):
    def __init__(self, command: str) -> 'SedCommand':
        """
        解析 sed 命令并返回 SedCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Stream editor for filtering and transforming text.", add_help=False)
        parser.add_argument("-e", "--expression", type=str, required=True, help="The editing expression to apply (e.g., 's/pattern/replacement/')")
        parser.add_argument("-i", "--in-place", action="store_true", help="Edit files in place")
        parser.add_argument("-n", "--no-autoprint", action="store_true", help="Suppress automatic line printing")
        parser.add_argument("files", nargs="*", type=str, help="Files to process")

        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self, stream=None):
        # 解析替换表达式
        expression = self.expression
        match = re.match(r's/([^/]+)/([^/]+)/?', expression)
        if not match:
            print_formatted_text(HTML(f"<error>Error: Invalid expression '{expression}'. Expected format: s/pattern/replacement/</error>"), style=self.log_style)
            return
        pattern, replacement = match.groups()

        # 创建正则表达式
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            print_formatted_text(HTML(f"<error>Error: Invalid regular expression '{pattern}': {e}</error>"), style=self.log_style)
            return

        if stream:
            # 从流中读取内容
            lines = stream.readlines()
            self._process_lines(lines, compiled_pattern, replacement)
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
                            new_lines = self._process_lines(lines, compiled_pattern, replacement)

                        if self.in_place:
                            # 如果是修改文件的操作
                            with open(file, 'w', encoding='utf-8') as f:
                                f.writelines(new_lines)
                    except Exception as e:
                        print_formatted_text(HTML(f"<critical>Critical Error: Failed to read file '{file}': {e}</critical>"), style=self.log_style)

    def _process_lines(self, lines, pattern, replacement):
        """
        处理输入的行，执行替换操作。
        """
        new_lines = []
        for line in lines:
            new_line = re.sub(pattern, replacement, line)
            new_lines.append(new_line)

            if not self.no_autoprint:
                print(new_line, end='')  # 默认打印修改后的内容
        return new_lines

if __name__ == "__main__":
    command = "-i -e s/replace/asda/  hello.txt"  # 将 "test" 替换为 "replace"
    sed_command = SedCommand(command)
    sed_command.execute()
