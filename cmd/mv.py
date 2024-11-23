import argparse
import os
import shutil
import re
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text as print
from cmd.base import Command

normabs = lambda x: os.path.normpath(os.path.abspath(x.replace('~', os.path.expanduser('~'))))

@dataclass
class MvCommand(Command):
    force: bool = False  # 是否强制覆盖目标文件
    verbose: bool = False  # 是否显示详细信息
    interactive: bool = False  # 是否在覆盖前提示用户
    no_clobber: bool = False  # 是否禁止覆盖文件
    verbose: bool = False  # 是否显示详细信息

    def __init__(self, command: str) -> 'MvCommand':
        """
        解析 mv 命令并返回 MvCommand 实例。

        :param command: 包含 mv 命令选项和参数的字符串。
        """
        # 解析命令行参数
        parser = argparse.ArgumentParser(description="Move files or directories.", add_help=False)
        parser.add_argument("-f", "--force", action="store_true", help="Force move by overwriting existing files")
        parser.add_argument("-b", "--backup", action="store_true", help="Make backup of each existing file")
        parser.add_argument("-i", "--interactive", action="store_true", help="Prompt before overwrite")
        parser.add_argument("-n", "--no-clobber", action="store_true", help="Do not overwrite existing files")
        parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
        parser.add_argument("src", type=str, help="Source file or directory")
        parser.add_argument("dst", type=str, help="Destination file or directory")
        
        # 解析命令
        self.parser = parser
        super().__init__(command)

    def execute(self):
        if self.help:
            self.parser.print_help()
            return
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
                if self.no_clobber:
                    # 不覆盖现有文件
                    print(HTML(f"<warning>Skipped: '{dst}' already exists.</warning>"), style=self.log_style)
                    return
                elif self.interactive:
                    # 提示用户确认
                    response = input(f"Overwrite '{dst}'? [y/N]: ").strip().lower()
                    if response not in ['y', 'yes']:
                        print(HTML(f"<warning>Skipped: '{dst}' not overwritten.</warning>"))
                        return
                elif self.backup:
                    # 创建备份文件
                    backup_path = dst + ".bak"
                    shutil.move(dst, backup_path)
                    if self.verbose:
                        print(HTML(f"<success>Backup created: '{backup_path}'</success>"), style=self.log_style)
                elif not self.force:
                    # 非强制模式直接报错
                    print(HTML(f"<aaa bg='ansired'>Error: '{dst}' already exists. Use -f to force overwrite.</aaa>"))
                    return

            # 执行移动操作
            try:
                shutil.move(src, dst)
                if self.verbose:
                    print(HTML(f"Moved <aaa fg='ansiyellow'>'{src}'</aaa> to <aaa fg='ansigreen'>'{dst}'</aaa>"))
            except Exception as e:
                print(HTML(f"<critical>Error: {e}</critical>"), style=self.log_style)
            

# 主程序
if __name__ == "__main__":
    command = "-vb __pycache__/*  ./"  # 示例命令
    mv_command = MvCommand(command)
    mv_command.execute()
