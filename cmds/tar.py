import argparse
import os
import tarfile
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text
from cmds.base import Command

normabs = lambda x: os.path.normpath(os.path.abspath(x.replace('~', os.path.expanduser('~'))))

@dataclass
class TarCommand(Command):

    def __init__(self, command: str) -> 'TarCommand':
        """
        解析 tar 命令并返回 TarCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Create or extract tar archives.", add_help=False)
        parser.add_argument("-x", "--extract", action="store_true", help="Extract files from the archive")
        parser.add_argument("-c", "--create", action="store_true", help="Create a new tar archive")
        parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
        parser.add_argument("-f", "--file", type=str, required=True, help="Name of the tar file")
        parser.add_argument("-C", "--directory", type=str, help="Change to directory DIR before performing any actions")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        if not self.extract and not self.create:
            print_formatted_text(HTML("<error>Error: Must specify either -c to create or -x to extract.</error>"), style=self.log_style)
            return

        tar_file = normabs(self.file)

        if self.extract:
            self.extract_tar(tar_file)
        elif self.create:
            self.create_tar(tar_file)

    def extract_tar(self, tar_file):
        if not os.path.exists(tar_file):
            print_formatted_text(HTML(f"<error>Error: Tar file '{tar_file}' does not exist.</error>"), style=self.log_style)
            return

        extract_path = self.directory if self.directory else os.getcwd()
        extract_path = normabs(extract_path)

        try:
            with tarfile.open(tar_file, "r") as tar:
                tar.extractall(path=extract_path)
                if self.verbose:
                    print_formatted_text(HTML(f"Extracted files from <aaa fg='ansiyellow'>'{tar_file}'</aaa> to <aaa fg='ansigreen'>'{extract_path}'</aaa>"))
        except Exception as e:
            print_formatted_text(HTML(f"<critical>Critical Error: Failed to extract '{tar_file}': {e}</critical>"), style=self.log_style)

    def create_tar(self, tar_file):
        if os.path.exists(tar_file) and not self.force:
            print_formatted_text(HTML(f"<error>Error: Tar file '{tar_file}' already exists. Use -f to force overwrite.</error>"), style=self.log_style)
            return

        # To be implemented: code for creating a tar archive.

# 示例用法
if __name__ == "__main__":
    command = "-cvf __pycache__ __pycache__.tar.gz"  # 示例命令
    tar_command = TarCommand(command)
    tar_command.execute()