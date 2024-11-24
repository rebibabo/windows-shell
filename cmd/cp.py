import argparse
import os
import shutil
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text as print
from cmd.base import Command

normabs = lambda x: os.path.normpath(os.path.abspath(x.replace('~', os.path.expanduser('~'))))

@dataclass
class CpCommand(Command):

    def __init__(self, command: str) -> 'CpCommand':
        """
        解析 cp 命令并返回 CpCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Copy files or directories.", add_help=False)
        parser.add_argument("-a", "--archive", action="store_true", help="Preserve attributes and copy recursively")
        parser.add_argument("-r", "--recursive", action="store_true", help="Copy directories recursively")
        parser.add_argument("-i", "--interactive", action="store_true", help="Prompt before overwrite")
        parser.add_argument("-u", "--update", action="store_true", help="Copy only when the source is newer")
        parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
        parser.add_argument("-p", "--preserve", action="store_true", help="Preserve file attributes")
        parser.add_argument("-f", "--force", action="store_true", help="Force copy, overwrite if necessary")
        parser.add_argument("-l", "--link", action="store_true", help="Create hard links instead of copying")
        parser.add_argument("src", type=str, help="Source file or directory")
        parser.add_argument("dst", type=str, help="Destination file or directory")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        srcs = self.get_file_list(self.src)

        # 检查源路径是否存在
        if not srcs:
            print(HTML(f"<error>Error: Source '{self.src}' does not exist.</error>"), style=self.log_style)
            return

        for src in srcs:
            src = normabs(src)
            dst = normabs(self.dst)
            # 如果目标是目录，拼接源文件名到目标路径
            if os.path.isdir(dst):
                dst = os.path.join(dst, os.path.basename(src))

            # 如果目标文件已存在
            if os.path.exists(dst):
                if self.interactive:
                    response = input(f"Overwrite '{dst}'? [y/N]: ").strip().lower()
                    if response not in ['y', 'yes']:
                        print(HTML(f"<warning>Skipped: '{dst}' not overwritten.</warning>"), style=self.log_style)
                        return
                elif self.update:
                    if os.path.getmtime(src) <= os.path.getmtime(dst):
                        print(f"Skipped: '{dst}' is up to date.")
                        return
                elif not self.force:
                    print(HTML(f"<error>Error: '{dst}' already exists. Use -f to force overwrite.</error>"), style=self.log_style)
                    return

            # 创建链接而非复制
            if self.link:
                try:
                    os.link(src, dst)
                    if self.verbose:
                        print(HTML(f"<success>Linked '{src}' to '{dst}'</success>"), style=self.log_style)
                except Exception as e:
                    print(HTML(f"<error>Error: Failed to link '{src}' to '{dst}': {e}</error>"), style=self.log_style)
                return

            # 执行复制操作
            try:
                if os.path.isdir(src):
                    if not (self.recursive or self.archive):
                        print(HTML(f"<error>Error: '{src}' is a directory. Use -r or -a to copy directories.</error>"), style=self.log_style)
                        return
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst) if self.preserve else shutil.copy(src, dst)

                if self.verbose:
                    print(HTML(f"Copied <aaa fg='ansiyellow'>'{src}'</aaa> to <aaa fg='ansigreen'>'{dst}'</aaa>"))

                # 保留文件权限等属性
                if self.archive or self.preserve:
                    shutil.copystat(src, dst)

            except Exception as e:
                print(HTML(f"<critical>Critical Error: Failed to copy '{src}' to '{dst}': {e}</critical>"), style=self.log_style)

# 示例用法
if __name__ == "__main__":
    command = "-avf __pycache__/*.pyc ../"  # 示例命令
    cp_command = CpCommand(command)
    cp_command.execute()
