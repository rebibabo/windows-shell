import argparse
import os
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text as print
from cmds.base import Command

normabs = lambda x: os.path.normpath(os.path.abspath(x.replace('~', os.path.expanduser('~'))))

@dataclass
class TouchCommand(Command):

    def __init__(self, command: str) -> 'TouchCommand':
        """
        解析 touch 命令并返回 TouchCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Change file timestamps or create empty files.", add_help=False)
        parser.add_argument("-c", "--no-create", action="store_true", help="Do not create any files.")
        parser.add_argument("-m", "--modify", action="store_true", help="Change only the modification time.")
        parser.add_argument("-a", "--access", action="store_true", help="Change only the access time.")
        parser.add_argument("files", nargs="+", help="File(s) to be created or updated.")

        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        for file in self.files:
            filepath = normabs(file)

            try:
                # 如果文件不存在并且未指定 -c 选项，则创建文件
                if not os.path.exists(filepath):
                    if not self.no_create:
                        with open(filepath, 'a'):
                            os.utime(filepath, None)  # 更新访问和修改时间
                        print(HTML(f"<success>Created file '{filepath}'</success>"), style=self.log_style)
                    else:
                        print(HTML(f"<warning>File '{filepath}' does not exist and no-create option is set. Skipping.</warning>"), style=self.log_style)
                        continue
                else:
                    # 更新文件的时间戳
                    if self.modify:
                        os.utime(filepath, (None, os.path.getmtime(filepath)))  # 仅更新修改时间
                    elif self.access:
                        os.utime(filepath, (os.path.getatime(filepath), None))  # 仅更新访问时间
                    else:
                        os.utime(filepath, None)  # 更新访问和修改时间

                    print(HTML(f"<success>Updated timestamps for '{filepath}'</success>"), style=self.log_style)

            except Exception as e:
                print(HTML(f"<error>Error: Failed to create or update '{filepath}': {e}</error>"), style=self.log_style)

# 示例用法
if __name__ == "__main__":
    command = "-m filename.txt"  # 示例命令
    touch_command = TouchCommand(command)
    touch_command.execute()