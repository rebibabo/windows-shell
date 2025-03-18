import os
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style, merge_styles
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import print_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from style import ShellLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
import pyperclip
import getpass
import subprocess

from utils import CmdHistory, is_executable, \
    longest_common_prefix, HDFS_FILE, display_files, \
    parse_environment_command, is_assignment_command

env_vars = os.environ.copy()

user = getpass.getuser()
bindings = KeyBindings()

normabs = lambda x: os.path.abspath(x.replace('~', os.path.expanduser('~')))       
        
class CmdWindow:
    custom_style = Style.from_dict({
        'username': '#00FF7F',
        'at':       '#20fe8b',
        'colon':    '#ffffff',
        'dollar':   '#ffffff',
        'host':     '#00FF7F',
        'path':     '#00BFFF',
    })
    process = subprocess.Popen(
        ["bash"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    pygments_style = style_from_pygments_cls(get_style_by_name('github-dark'))    # manni github-dark
    last_buffer = None
    style = merge_styles([custom_style, pygments_style])
    
    cmd_history = CmdHistory()
    history = InMemoryHistory(cmd_history.data)
    session = PromptSession(history=history)
    suggestions = []
    basename = ''
    tab_two = False
        
    def __init__(self):
        os.system('clear')
        self.alias = {}
        ''' Fixed: 解决~/.bashrc中alias命令无法识别的问题 '''
        try:
            with open(os.path.expanduser('~/.bashrc'), 'r') as f:
                for line in f:
                    if line.startswith('alias '):
                        line = line.split('alias ')[1].replace('"', '').replace("'", '').strip()
                        alias_name = line.split('=')[0].strip()
                        alias_cmd = '='.join(line.split('=')[1:])
                        self.alias[alias_name] = alias_cmd.strip()
        except:
            pass
        ''' Fixed: 解决非交互式界面history为空的问题 '''
        self.alias['history'] = f'cat {self.cmd_history.history_path}'
        self.alias['ll'] = 'ls -la --color'
        
    @staticmethod    
    def print_prefix():
        prefix = [
            ('class:username',  user),
            ('class:at',       '@'),
            ('class:host',     'localhost'),
            ('class:colon',    ':'),
            ('class:path',      os.getcwd()),
            ('class:pound',    '$ '),
        ]

        return CmdWindow.session.prompt(prefix, 
                style=CmdWindow.style, 
                key_bindings=bindings, 
                lexer=PygmentsLexer(ShellLexer), 
                auto_suggest=AutoSuggestFromHistory())
        
    @staticmethod
    def execute_cmd(command):
        try:
            # 使用 subprocess 执行命令，并传递环境变量
            process = subprocess.run(
                command,
                shell=True,
                env=env_vars,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # 输出命令的结果
            if process.stdout:
                print(process.stdout, end="")
            if process.stderr:
                print(process.stderr, end="", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}")

        
    def run(self):
        last_path = os.getcwd()
        while True:
            try:
                cmd = CmdWindow.print_prefix()
                for alias_name, alias_cmd in self.alias.items():
                    new_text_chars = []
                    i = 0
                    while i < len(cmd):
                        ''' Fixed: 在替换alias命令时，只替换开头为alias_name的命令，也包括``和$( )中开头的命令 '''
                        if cmd[i:].split(' ')[0] == alias_name and (i == 0 or cmd[i-1] in [' ', '\t', '`', '\n'] or cmd[i-2:i] in ['&&', '$(']):
                            while i < len(cmd) and cmd[i] not in [' ', '\n', '\t', '`']:
                                i += 1
                            new_text_chars.append(alias_cmd + ' ')
                        else:
                            new_text_chars.append(cmd[i])
                        i += 1
                    cmd = ''.join(new_text_chars)

                if cmd.strip() in ['quit', 'exit', 'q']:
                    print('Bye!')
                    break
                elif cmd.strip().startswith('cd '):
                    ''' Fixed: cd命令只补全目录，不补全文件名 '''
                    ori_path = cmd.split()[1]
                    path = normabs(ori_path)
                    if ori_path.strip() == '-':
                        path = last_path
                    elif not os.path.exists(path):
                        print(f"-bash: cd: {path}: No such file or directory")
                        continue
                    last_path = os.getcwd()
                    os.chdir(path)
                elif cmd.strip().startswith("export"):
                    ''' Fixed: 解决环境变量加载不了的问题 '''
                    key, value = parse_environment_command(cmd, export=True)
                    if key and value:
                        env_vars[key] = value
                elif is_assignment_command(cmd):
                    key, value = parse_environment_command(cmd)
                    if key and value:
                        env_vars[key] = value
                elif cmd.strip().startswith('unset'):
                    key = cmd.split()[1]
                    if key in env_vars:
                        del env_vars[key]
                else:
                    ''' Fixed: 解决ls和grep命令没有高亮问题 '''
                    split = cmd.split('|')[-1]
                    if ('ls' in split and '-ls' not in split) or 'grep' in split:
                        cmd += ' --color'
                    self.cmd_history.add(cmd)
                    CmdWindow.execute_cmd(cmd)
                    # os.system(cmd)
                    continue
                self.cmd_history.add(cmd)
            except KeyboardInterrupt:
                print()
                pass
            except EOFError:
                break

            
@bindings.add('tab', filter=True)
def complete_path(event):
    ori_text = CmdWindow.session.app.current_buffer.text      # 获取当前输入的命令
    ''' Fix: 解决Tab补全时，不同缓冲区的历史命令混淆问题，必须是缓冲区内容相同且连续按两次Tab才会显示建议列表 '''
    if CmdWindow.last_buffer is None:       
        CmdWindow.last_buffer = ori_text
    
    if CmdWindow.last_buffer != ori_text:
        CmdWindow.tab_two = False
    CmdWindow.last_buffer = ori_text
    
    document = CmdWindow.session.app.current_buffer.document
    cursor_position = document.cursor_position      # 获取光标位置
    current_text = ori_text[:cursor_position]   # 获取当前光标前面部分
    
    if not current_text:        # 如果当前什么也没有输入，则退出
        return
    if '"' in current_text:     # 如果当前输入中有双引号
        ori_path = current_text.split('"')[-1]     # 获取双引号后面的部分，即路径
    elif "'" in current_text:   # 如果当前输入中有单引号
        ori_path = current_text.split("'")[-1]     # 获取单引号后面的部分，即路径
    else:                       # 如果当前输入中没有引号
        ori_path = current_text.split()[-1]     # 获取当前输入的命令的最后一个参数，即路径
    
    ''' Fixed: 解决使用normabs后，原始路径末尾的/丢失问题 '''
    path = normabs(ori_path) + ('/' if ori_path.endswith('/') else '')                   # 规范化路径
    
    if False and path.strip().startswith("/workspace"):
        if not CmdWindow.suggestions:
            cmd = f"hdfs dfs -test -d {path} && echo $?"
            result = os.popen(cmd).read()
            if result.strip() == '0':
                path += '/'
            dirname = os.path.dirname(path)
            basename = os.path.basename(path)
            cmd = f"hdfs dfs -ls {dirname}"
            files = os.popen(cmd).read().split('\n')[1:]
            suggestions = []
            for file in files:
                if not file.strip():
                    continue
                name = file.split('/')[-1]
                is_dir = file.startswith('d')
                filepath = file.split(' ')[-1]
                if name.startswith(basename):
                    suggestions.append(HDFS_FILE(name, filepath, is_dir))
        else:
            suggestions = CmdWindow.suggestions
            basename = CmdWindow.basename
        
    else:
        ''' Fixed: 解决当缓存为a，路径下同时存在aaa/和aaa.py, 按下Tab后直接补全为aaa/的问题 '''
        if os.path.isdir(path) and sum(1 for file in os.listdir(os.path.dirname(path)) if file.startswith(os.path.basename(path))) == 1:
            path += '/'
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        if not os.path.exists(dirname):
            return
        files = os.scandir(dirname)
        suggestions = []
        
        for file in files:
            if ori_text.strip().startswith('cd '):     # cd只补全目录
                if file.is_dir() and file.name.startswith(basename):
                    suggestions.append(file)
            elif ori_text.strip().startswith('./') and ' ' not in ori_text.strip():    # 执行脚本只补全可执行文件，但不是参数
                if file.is_file() and is_executable(file.path) and file.name.startswith(basename):
                    suggestions.append(file)
            else:
                if file.name.startswith(basename):
                    suggestions.append(file)
                    
    if not ori_text.endswith('/') and os.path.isdir(path) and len(suggestions) == 1:
        CmdWindow.session.app.current_buffer.insert_text('/')
        return
    
    if not suggestions:                     # 如果没有文件名以base开头，则不补全
        return
    elif len(suggestions) == 1:             # 如果只有一个文件名以base开头，则直接补全
        CmdWindow.session.app.current_buffer.insert_text(suggestions[0].name[len(basename):])
        if suggestions[0].is_dir():
            if ori_text[-1] != '/':
                CmdWindow.session.app.current_buffer.insert_text('/')
        else:
            CmdWindow.session.app.current_buffer.insert_text(' ')
    else:
        ''' Fixed: 解决有多个suggestion时，直接显示suggestion，而不补全公共前缀的问题 '''
        common_prefix = longest_common_prefix([s.name for s in suggestions])
        if common_prefix and len(common_prefix) > len(basename):
            CmdWindow.session.app.current_buffer.insert_text(common_prefix[len(basename):])
        if CmdWindow.tab_two:
            display_files(suggestions)
            ''' Fixed: 解决在打印提示信息后，没有显示前缀提示信息的问题 '''
            print_formatted_text('', style=CmdWindow.style)
            CmdWindow.tab_two = False
            CmdWindow.suggestions = []
        else:
            CmdWindow.tab_two = True
            CmdWindow.suggestions = suggestions
            CmdWindow.basename = basename
        

# 定义粘贴快捷键 Ctrl+V
@bindings.add("c-v")
def paste(event):
    clipboard_content = pyperclip.paste() 
    CmdWindow.session.app.current_buffer.insert_text(clipboard_content)
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        os.chdir(normabs(sys.argv[1]))  
    cmd_window = CmdWindow()
    cmd_window.run()
