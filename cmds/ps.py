import argparse
import psutil
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text
from cmds.base import Command

@dataclass
class PsCommand(Command):

    def __init__(self, command: str) -> 'PsCommand':
        """
        解析 ps 命令并返回 PsCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Display information about running processes.", add_help=False)
        parser.add_argument("-a", "--all", action="store_true", help="Show all processes")
        parser.add_argument("-u", "--user", action="store_true", help="Show processes for the current user")
        parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        # 显示所有进程
        processes = psutil.process_iter(['pid', 'name', 'username', 'status'])
        process_list = []

        for proc in processes:
            try:
                # 过滤当前用户的进程
                if self.user and proc.info['username'] != psutil.Process().username():
                    continue
                process_list.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not process_list:
            print_formatted_text(HTML("<warning>No processes found.</warning>"), style=self.log_style)
            return

        # 打印进程信息
        if self.verbose:
            print_formatted_text(HTML("<b>PID  | Name                       | User                      | Status</b>"))
            print("-" * 50)

        for proc in process_list:
            # 格式化输出
            pid = proc['pid']
            name = proc['name'][:25]  # 限制名称长度
            user = proc['username'][:25]  # 限制用户名长度
            status = proc['status']
            print_formatted_text(HTML(f"{pid:<5} | {name:<25} | {user:<25} | {status}"))

# 示例用法
if __name__ == "__main__":
    command = "-av"  # 示例命令
    ps_command = PsCommand(command)
    ps_command.execute()