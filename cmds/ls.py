import argparse
from datetime import datetime
from prompt_toolkit import HTML, print_formatted_text as print
import os
import html
from prompt_toolkit.styles import Style
import shutil
from wcwidth import wcswidth
from cmds.base import Command

def bytes_to_appropriate_unit(size_in_bytes):
    # 定义单位和对应的字节数
    if size_in_bytes < 1024:
        return f"{size_in_bytes}B"
    units = [("KB", 1024), ("MB", 1024**2), ("GB", 1024**3), ("TB", 1024**4), ("PB", 1024**5)]
    
    # 遍历单位，找到最合适的一个
    for unit, byte_value in units:
        if size_in_bytes < byte_value * 1024:
            return f"{size_in_bytes / byte_value:.2f}{unit}"
    
    # 如果所有单位都不合适，返回原字节数
    return f"{size_in_bytes}"

class LsCommand(Command):
    file_style = Style.from_dict({
        'file': '#ffffff',
        'directory': '#28a0ea',
        'link': 'ansiyellow',
        'filesize': 'ansiyellow',
        'last_write_time': '#ffffff',
    })
    a: bool = False
    l: bool = False
    r: bool = False
    t: bool = False
    F: bool = False
    R: bool = False
    h: bool = False
    s: bool = False
    
    def __init__(self, command: str) -> 'LsCommand':
        """
        从字符串解析 ls 命令并返回 LsCommand 实例。

        :param command: 包含 ls 选项和路径的字符串
        :return: LsCommand 实例
        """
        # 解析参数
        parser = argparse.ArgumentParser(description="Parse ls command options.", add_help=False)
        # 添加选项
        parser.add_argument("-a", action="store_true", help="Display all files, including hidden files.")   
        parser.add_argument("-l", action="store_true", help="Use a long listing format.")   
        parser.add_argument("-r", action="store_true", help="Reverse order while sorting.") 
        parser.add_argument("-t", action="store_true", help="Sort by modification time.")       
        parser.add_argument("-F", action="store_true", help="Append indicator (e.g., /, *) to entries.") 
        parser.add_argument("-R", action="store_true", help="Recursively list subdirectories.")
        parser.add_argument("-h", action="store_true", help="Display file sizes in human-readable format.") 
        parser.add_argument("-s", action="store_true", help="Sort by file size.")
        parser.add_argument("name", nargs="*", default=[], help="Paths to list. Defaults to current directory.")
        
        self.parser = parser
        super().__init__(command)
        
    def get_file_info_list(self, path):
        files_info = []
        file_list = self.get_file_list(path)
        for file in file_list:
            file_info = {}
            dirname = os.path.dirname(file)
            file_info['basename'] = html.escape(os.path.basename(file)).replace('/', '')
            file_info['dirname'] = html.escape(self.normabs(dirname))
            file_info['fullpath'] = html.escape(self.normabs(file))
            
            if os.path.isdir(file):
                file_info['mode'] = 'd'
            elif file.endswith('.lnk') or file.startswith('~'):
                if not self.a:
                    continue
                file_info['mode'] = 'l'
            else:
                file_info['mode'] = 'f'

            last_write_time = os.path.getmtime(file)
            last_write_time_str = datetime.fromtimestamp(last_write_time).strftime('%Y/%m/%d %H:%M:%S')
            
            size = os.path.getsize(file) if os.path.isfile(file) else 0
            
            file_info['last_write_time'] = last_write_time_str
            file_info['size'] = size
            if self.h:
                file_info['h_size'] = bytes_to_appropriate_unit(size)
            
            files_info.append(file_info)
        return files_info
            
    @Command.safe_exec
    def execute(self):
        if not self.name:
            self.name = ['.']
        for path in self.name:
            path = path.replace('~', os.path.expanduser('~'))
            files_info = self.get_file_info_list(path)
            if self.l:
                if self.R:
                    print(HTML(f"<aaa bg='ansiblue'>{self.normabs(html.escape(path))}:</aaa>"))
                else:
                    print(HTML(f"<aaa bg='ansiblue'>{html.escape(path)}:</aaa>"))
            if not files_info and not self.R:
                print(HTML(f"<aaa bg='ansired'>cannot access '{html.escape(path)}': No such file or directory</aaa>\n"))
                continue
            files_info.sort(key=lambda x: x['basename'], reverse=self.r)
            if self.t:
                files_info.sort(key=lambda x: x['last_write_time'], reverse=self.r)
            if self.s:
                files_info.sort(key=lambda x: x['size'], reverse=self.r)
            
            if not self.l:
                # 获取终端宽度
                terminal_width = int(shutil.get_terminal_size().columns)
                # 从最大列数开始尝试
                num_files = len(files_info)
                # 函数：计算字符串的显示宽度（考虑非 ASCII 字符）
                def display_width(s):
                    return wcswidth(s)

                # 每列间隔为 2 个字符
                column_gap = 2
                # 计算单列宽度（最长文件名显示宽度 + 间隔）
                max_col_width = max(display_width(file['basename']) for file in files_info) + column_gap
                # 最大可能列数
                max_columns = terminal_width // max_col_width

                # 找到实际可用的列数
                for columns in range(max_columns, 0, -1):
                    rows = (num_files + columns - 1) // columns  # 向上取整计算行数
                    col_widths = []

                    # 计算每列的宽度
                    for col in range(columns):
                        col_items = files_info[col * rows:(col + 1) * rows]
                        if col_items:
                            # 当前列最大宽度（考虑非 ASCII 字符）
                            col_width = max(display_width(item['basename']) for item in col_items) + column_gap
                            col_widths.append(col_width)

                    # 检查总宽度是否符合终端宽度
                    total_width = sum(col_widths)
                    if total_width <= terminal_width:
                        break

                # 打印结果
                for row in range(rows):
                    row_content = ''
                    for col in range(columns):
                        index = col * rows + row
                        if index < num_files:
                            item = files_info[index]
                            # 动态填充宽度（考虑非 ASCII 字符）
                            padding = col_widths[col] - display_width(item['basename'])
                            if files_info[index]['mode'] == 'd':
                                item = f"<directory>{item['basename']}</directory>"
                                if self.F:
                                    item += '/'
                                    padding -= 1
                            elif files_info[index]['mode'] == 'l':
                                item = f"<link>{item['basename']}</link>"
                                if self.F:
                                    item += '*'
                                    padding -= 1
                            else:
                                item = f"<file>{item['basename']}</file>"
                            row_content += item + " " * padding
                    print(HTML(row_content), style=self.file_style)
            else:
                for file in files_info:
                    size = file['h_size'] if self.h else file['size']
                    print(HTML(f"<filesize>{size:>12}</filesize>"), style=self.file_style, end='  ')
                    print(HTML(f"<last_write_time>{file['last_write_time']}</last_write_time>"), style=self.file_style, end='  ')
                    if file['mode'] == 'd':
                        print(HTML(f"<directory>{file['basename']}{'/' if self.F else ''}</directory>"), style=self.file_style)
                    elif file['mode'] == 'l':
                        print(HTML(f"<link>{file['basename']}</link>{'*' if self.F else ''}"), style=self.file_style)
                    else:
                        print(HTML(f"<file>{file['basename']}</file>"), style=self.file_style)
            
            if self.R and files_info:
                directories = []
                for file in os.listdir(os.path.dirname(files_info[0]['fullpath'])):
                    if os.path.isdir(file):
                        directories.append(file)
                if not directories:
                    continue
                self.name = directories
                self.execute()
                
if __name__ == "__main__":
    # 输入 lsr 命令的字符串
    command = "--help -l ../*.py ../"
    # command = "-l asd/"
    parsed_command = LsCommand(command)
    print(parsed_command)
    parsed_command.execute()
