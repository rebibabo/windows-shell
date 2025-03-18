import os
from prompt_toolkit import print_formatted_text
import shutil
from wcwidth import wcswidth
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
import stat
import re

history_path = os.path.join(os.path.dirname(__file__), 'history.txt')
file_style = Style.from_dict({
    'file': '#ffffff',
    'directory': '#87CEFA',
    'link': '#98FB98',
})

class CmdHistory:
    def __init__(self, max_size=100):
        self.max_size = max_size
        self.history = []
        self.history_path = history_path
        if not os.path.exists(history_path):
            with open(history_path, 'w', encoding='utf-8') as f:
                f.write('')
            return
        with open(history_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.history.append(line.strip())
                
    def clear(self, left_num=0):
        if left_num == 0:
            self.history = []
        else:
            self.history = self.history[-left_num:] 
        with open(history_path, 'w',  encoding='utf-8') as f:
            for cmd in self.history:
                f.write(cmd+'\n')     
                
    def add(self, cmd):
        self.history.append(cmd)
        with open(history_path, 'a',  encoding='utf-8') as f:
            f.write(cmd+'\n')
          
    @ property           
    def data(self):
        return self.history[-self.max_size:]
    
    def __len__(self):
        return len(self.history)
    
    def __str__(self):
        his = ''
        for i, cmd in enumerate(self.history[-self.max_size:]):
            his += f"{i+1+len(self)-self.max_size:{len(str(self.max_size))}d} {cmd}\n"
        return his     
    

def is_executable(filepath):
    if not os.path.isfile(filepath):
        return False
    st = os.stat(filepath)
    return bool(st.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

def display_files(files):
    print()
    files = sorted(files, key=lambda x: x.name)
    terminal_width = int(shutil.get_terminal_size().columns)
    num_files = len(files)
    column_gap = 2

    # 提前计算所有文件名的显示宽度
    file_widths = [wcswidth(file.name) + int(file.is_dir()) for file in files]
    max_col_width = max(file_widths) + column_gap
    max_columns = terminal_width // max_col_width

    # 提前过滤出目录和可执行文件
    dir_files = [file for file in files if file.is_dir()]
    exec_files = [file for file in files if is_executable(file.path)]

    # 找到实际可用的列数
    for columns in range(max_columns, 0, -1):
        rows = (num_files + columns - 1) // columns
        col_widths = []

        # 计算每列的宽度
        for col in range(columns):
            col_items = files[col * rows:(col + 1) * rows]
            if col_items:
                col_width = max(file_widths[col * rows + i] for i in range(len(col_items))) + column_gap
                col_widths.append(col_width)

        # 检查总宽度是否符合终端宽度
        total_width = sum(col_widths)
        if total_width <= terminal_width:
            break

    # 打印结果
    row_content = ''
    for row in range(rows):
        
        for col in range(columns):
            index = col * rows + row
            if index < num_files:
                file = files[index]
                padding = col_widths[col] - file_widths[index]
                if file in dir_files:
                    item = f"<directory>{file.name}/</directory>"
                elif file in exec_files:
                    item = f"<link>{file.name}</link>"
                else:
                    item = f"<file>{file.name}</file>"
                row_content += item + " " * padding
        row_content += '\n'
    ''' Fixed: 一次性打印所有文件，提高渲染效率'''
    print_formatted_text(HTML(row_content), style=file_style)
            
def longest_common_prefix(strs):
    """
    求字符串列表的公共前缀。

    :param strs: 字符串列表，例如 ["flower", "flow", "flight"]
    :return: 公共前缀，例如 "fl"
    """
    if not strs:
        return ""

    # 以第一个字符串为基准
    prefix = strs[0]

    for s in strs[1:]:
        # 逐个字符比较，更新公共前缀
        while not s.startswith(prefix):
            prefix = prefix[:-1]  # 缩短前缀
            if not prefix:
                return ""  # 如果前缀为空，返回空字符串

    return prefix
            
def parse_environment_command(command, export=False):
    """
    解析 环境变量 命令，提取变量名和值
    """
    if export:
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            print("Error: Invalid export command")
            return None, None

        key_value = parts[1].strip()
    else:
        key_value = command.strip()
    if "=" not in key_value:
        print("Error: Invalid export command")
        return None, None

    key, value = key_value.split("=", maxsplit=1)
    return key.strip(), value.strip()


def is_assignment_command(command):
    """
    判断命令是否符合变量赋值的格式
    """
    # 正则表达式
    pattern = r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(?:\d+|"[\s\S]*?"|\'[\s\S]*?\')\s*$'
    # 匹配
    return bool(re.match(pattern, command))
            
class HDFS_FILE:
    def __init__(self, name, path, is_dir_):
        self.name = name
        self.path = path
        self.is_dir_ = is_dir_
        
    def is_dir(self):
        return self.is_dir_