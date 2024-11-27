import argparse
import os
import shutil
from prompt_toolkit import HTML, print_formatted_text as print
from cmds.base import Command

class RmCommand(Command):

    def __init__(self, command: str) -> 'RmCommand':
        """
        解析 rm 命令并返回 RmCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Remove files or directories.", add_help=False)
        parser.add_argument("-i", "--interactive", action="store_true", help="Prompt before each removal")
        parser.add_argument("-f", "--force", action="store_true", help="Ignore nonexistent files and never prompt")
        parser.add_argument("-r", "--recursive", action="store_true", help="Remove directories and their contents recursively")
        parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
        parser.add_argument("targets", nargs='+', type=str, help="Files or directories to remove")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        for target in self.targets:
            target_path = self.normabs(target)
            target_files = self.get_file_list(target_path, traverse=False)
            
            # 检查路径是否存在
            if not target_files:
                if not self.force:
                    print(HTML(f"<error>Error: '{target}' does not exist.</error>"), style=self.log_style)
                continue

            for target_path in target_files:
                # 处理目录删除
                if os.path.isdir(target_path):
                    if not self.recursive:
                        print(HTML(f"<error>Error: '{target}' is a directory. Use -r to remove directories.</error>"), style=self.log_style)
                        continue
                    
                    if self.interactive:
                        response = input(f"Remove directory '{target}' and its contents? [y/N]: ").strip().lower()
                        if response not in ['y', 'yes']:
                            print(HTML(f"<warning>Skipped: '{target}' not removed.</warning>"), style=self.log_style)
                            continue

                    try:
                        shutil.rmtree(target_path, ignore_errors=self.force)
                        if self.verbose:
                            print(HTML(f"<success>Removed directory '{target}'</success>"), style=self.log_style)
                    except Exception as e:
                        print(HTML(f"<critical>Critical Error: Failed to remove '{target}': {e}</critical>"), style=self.log_style)

                # 处理文件删除
                else:
                    if self.interactive:
                        response = input(f"Remove file '{target}'? [y/N]: ").strip().lower()
                        if response not in ['y', 'yes']:
                            print(HTML(f"<warning>Skipped: '{target}' not removed.</warning>"), style=self.log_style)
                            continue

                    try:
                        os.remove(target_path)
                        if self.verbose:
                            print(HTML(f"<success>Removed file '{target}'</success>"), style=self.log_style)
                    except Exception as e:
                        if not self.force:
                            print(HTML(f"<critical>Critical Error: Failed to remove '{target}': {e}</critical>"), style=self.log_style)

# 示例用法
if __name__ == "__main__":
    command = "*.zip"  # 示例命令
    rm_command = RmCommand(command)
    rm_command.execute()
