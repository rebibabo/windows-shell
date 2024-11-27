import argparse
import os
from prompt_toolkit import HTML, print_formatted_text as print
from cmds.base import Command

class WcCommand(Command):
    def __init__(self, command: str) -> 'WcCommand':
        """
        解析 wc 命令并返回 WcCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Print newline, word, and byte counts for each FILE.", add_help=False)
        parser.add_argument("-l", "--lines", action="store_true", help="Print the number of lines")
        parser.add_argument("-w", "--words", action="store_true", help="Print the number of words")
        parser.add_argument("-b", "--bytes", action="store_true", help="Print the number of bytes")
        parser.add_argument("-c", "--chars", action="store_true", help="Print the number of characters")
        parser.add_argument("files", nargs="*", type=str, help="Files to process")

        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self, input_lines=None):
        if input_lines:
            # 从流中读取内容
            self._count_lines(input_lines)
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
                            self._count_lines(lines)
                    except Exception as e:
                        print(HTML(f"<critical>Critical Error: Failed to read file '{file}': {e}</critical>"), style=self.log_style)

    def _count_lines(self, lines):
        """
        计算并输出行数、字数、字节数和字符数。
        """
        line_count = len(lines)
        word_count = sum(len(line.split()) for line in lines)
        byte_count = sum(len(line.encode('utf-8')) for line in lines)
        char_count = sum(len(line) for line in lines)  # UTF-8字符数，包含Unicode字符

        if self.lines:
            print(f"Lines: {line_count}")
        if self.words:
            print(f"Words: {word_count}")
        if self.bytes:
            print(f"Bytes: {byte_count}")
        if self.chars:
            print(f"Characters: {char_count}")
        
        # 打印所有信息
        if not (self.lines or self.words or self.bytes or self.chars):
            print(f"{line_count} {word_count} {byte_count} {char_count}")

if __name__ == "__main__":
    command = "-lwcb *.py"  # 统计行数、字数和字节数
    wc_command = WcCommand(command)
    wc_command.execute()
