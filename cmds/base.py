from dataclasses import dataclass
from typing import List
from prompt_toolkit import HTML, print_formatted_text as print
from prompt_toolkit.styles import Style
from prompt_toolkit import HTML
from functools import wraps
import os
import re
import glob

@dataclass
class Command:
    name: List[str] = None
    log_style: dict = Style.from_dict({
        'success': 'fg:ansigreen',
        'warning': 'fg:ansiblack bg:ansiyellow',
        'error': 'fg:ansired',
        'critical': 'fg:ansiwhite bg:ansired',
    })
    
    def __init__(self, command: str='') -> 'Command':
        """
        从字符串解析命令并返回 Command 实例。

        :param command: 包含命令选项和参数的字符串
        :return: Command 实例
        """
        # 将字符串拆分成列表，类似于命令行参数
        args = self.split_command(command)
        self.parse_error = False
        if not hasattr(self, 'parser'):
            return
        self.parser.add_argument("--help", action="store_true", help="Show this help message and exit")
        try:
            parsed_args = self.parser.parse_args(args)  # 解析命令参数
        except SystemExit:
            self.parse_error = True
            return None
        for key, value in vars(parsed_args).items():
            setattr(self, key, value)  # 将解析结果添加到实例属性中
        
        return self
    
    def split_command(self, command: str) -> List[str]:
        """
        按空格分割参数，当参数有引号时，不保留引号，引号内空格不会分割。

        :param args: 参数字符串。
        :return: 参数列表。
        """
        args = []
        current_arg = ''
        in_quotes = False
        for char in command:
            if char in ['"', "'"]:
                in_quotes = not in_quotes
            elif char == ' ' and not in_quotes:
                args.append(current_arg)
                current_arg = ''
            else:
                current_arg += char
        if current_arg:
            args.append(current_arg)
        return args

    def get_file_list(self, path: str, traverse: bool = True, recursive: bool = False, include_dirs: bool = True) -> List[str]:
        """
        根据路径的类型（文件、目录、正则表达式）返回文件或目录。

        :param path: 文件路径、目录路径或正则表达式。
        :param traverse: 是否遍历目录的标志（仅对目录有效）。
        :param recursive: 是否递归遍历目录。
        :param include_dirs: 是否将目录也包括在内。
        :return: 匹配的文件路径列表。
        """
        # 判断路径是否是文件
        if os.path.isfile(path):
            return [path]  # 如果是文件，直接返回文件路径
        
        # 判断路径是否是目录
        elif os.path.isdir(path):
            files = []
            if traverse:
                # 如果需要遍历1层目录
                for entry in os.scandir(path):
                    if entry.is_file():
                        files.append(entry.path)
                    elif entry.is_dir() and include_dirs:
                        files.append(entry.path)  # 加入目录，但不继续递归
            elif recursive:
                # 递归遍历目录
                for dirpath, _, filenames in os.walk(path):
                    files.extend([os.path.join(dirpath, filename) for filename in filenames])
                    if include_dirs:
                        files.extend([os.path.join(dirpath, dir) for dir in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, dir))])
            else:
                # 只返回当前目录
                files.append(path)
            return files

        # 如果是正则表达式路径
        elif re.match(r".*\*.*", path):  # 如果是通配符或正则表达式
            file_list = glob.glob(path, recursive=recursive)
            return file_list

        return []  # 其他情况返回空列表
    
    @staticmethod
    def safe_exec(func):
        """
        安全执行函数，捕获异常并打印错误信息。

        :param func: 要执行的函数。
        :return: 装饰后的函数。
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.parse_error:
                return None
            if self.help:
                self.parser.print_help()
                return None
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                print(HTML(f'<error>Error: {e}</error>'), style=Command.log_style)  # 假设HTML是某种日志格式
                return None
        return wrapper

        
    def execute(self):
        raise NotImplementedError("Subclasses should implement this!")