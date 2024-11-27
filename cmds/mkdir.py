import argparse
import os
from prompt_toolkit import HTML, print_formatted_text as print
from cmds.base import Command

class MkdirCommand(Command):

    def __init__(self, command: str) -> 'MkdirCommand':
        """
        解析 mkdir 命令并返回 MkdirCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Create directories.", add_help=False)
        parser.add_argument("-p", "--parents", action="store_true", help="Create parent directories as needed")
        parser.add_argument("-m", "--mode", type=int, help="Set file mode (as in chmod), not a=rw - umask")
        parser.add_argument("dirs", nargs='+', help="Directory to create")

        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        for dir_path in self.dirs:
            norm_dir_path = self.normabs(dir_path)

            try:
                # 如果要创建的目录已存在
                if os.path.exists(norm_dir_path):
                    print(HTML(f"<warning>Warning: Directory '{norm_dir_path}' already exists.</warning>"), style=self.log_style)
                    continue

                # 如果使用- p选项，递归创建父目录
                if self.parents:
                    os.makedirs(norm_dir_path)
                else:
                    os.mkdir(norm_dir_path)

                # 如果提供了mode选项，则设置权限
                if self.mode is not None:
                    os.chmod(norm_dir_path, self.mode)

                print(HTML(f"<success>Directory '{norm_dir_path}' created successfully.</success>"), style=self.log_style)

            except Exception as e:
                print(HTML(f"<error>Error: Failed to create directory '{norm_dir_path}': {e}</error>"), style=self.log_style)

# 示例用法
if __name__ == "__main__":
    command = "-p new_dir/another_dir"  # 示例命令
    mkdir_command = MkdirCommand(command)
    mkdir_command.execute()