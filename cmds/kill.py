import argparse
import os
import signal
from prompt_toolkit import HTML, print_formatted_text
from cmds.base import Command
from dataclasses import dataclass

@dataclass
class KillCommand(Command):

    def __init__(self, command: str) -> 'KillCommand':
        """
        解析 kill 命令并返回 KillCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Terminate processes by PID.", add_help=False)
        parser.add_argument("pids", nargs='+', type=int, help="Process IDs to terminate")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        for pid in self.pids:
            try:
                os.kill(pid, signal.SIGTERM)
                print_formatted_text(HTML(f"<success>Sent 'Killed process {pid}.</success>"), style=self.log_style)
            except ProcessLookupError:
                print_formatted_text(HTML(f"<error>Error: No process with PID {pid} exists.</error>"), style=self.log_style)
            except PermissionError:
                print_formatted_text(HTML(f"<error>Error: Permission denied to kill process {pid}.</error>"), style=self.log_style)
            except Exception as e:
                print_formatted_text(HTML(f"<critical>Critical Error: Failed to kill process {pid}: {e}</critical>"), style=self.log_style)

# 示例用法
if __name__ == "__main__":
    command = "22924"  # 示例命令，假设要终止 PID 1234 和 5678 的进程
    kill_command = KillCommand(command)
    kill_command.execute()