import os
import re
from cmds import Cmd
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style, merge_styles
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from cmds.ls import LsCommand
from style import ShellLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import prompt

import getpass
user = getpass.getuser()
bindings = KeyBindings()
history_path = os.path.join(os.path.dirname(__file__), 'history.txt')
normabs = lambda x: os.path.normpath(os.path.abspath(x.replace('~', os.path.expanduser('~'))))

class CmdHistory:
    def __init__(self, max_size=100):
        self.max_size = max_size
        self.history = []
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
        
class CmdWindow:
    custom_style = Style.from_dict({
        'username': '#20fe8b',
        'at':       '#20fe8b',
        'colon':    '#ffffff',
        'dollar':   '#ffffff',
        'host':     '#20fe8b',
        'path':     '#28a0ea underline',
    })
    
    pygments_style = style_from_pygments_cls(get_style_by_name('manni'))
    style = merge_styles([custom_style, pygments_style])
    
    cmd_history = CmdHistory()
    history = InMemoryHistory(cmd_history.data)
    session = PromptSession(history=history)
    tab_two = False
        
    def __init__(self):
        os.system('cls')
        
    def run(self):
        while True:
            try:
                prefix = [
                    ('class:username',  user),
                    ('class:at',       '@'),
                    ('class:host',     'localhost'),
                    ('class:colon',    ':'),
                    ('class:path',      os.getcwd()),
                    ('class:pound',    '$ '),
                ]

                text = self.session.prompt(prefix, 
                                           style=self.style, 
                                           key_bindings=bindings, 
                                           lexer=PygmentsLexer(ShellLexer), 
                                           auto_suggest=AutoSuggestFromHistory())
                if text.strip() in ['quit', 'exit', 'q']:
                    print('Bye!')
                    break
                elif text.strip() == 'history':
                    print(self.cmd_history)
                else:
                    Cmd(text)
                self.cmd_history.add(text)
            except KeyboardInterrupt:
                print()
                pass
            except EOFError:
                break
            
    @bindings.add('tab', filter=True)
    def complete_path( event):
        current_text = CmdWindow.session.app.current_buffer.text      # 获取当前输入的命令
        
        document = CmdWindow.session.app.current_buffer.document
        cursor_position = document.cursor_position      # 获取光标位置
        current_text = current_text[:cursor_position]   # 获取当前光标前面部分
        
        if not current_text:        # 如果当前什么也没有输入，按下Tab键，则补全当前目录
            current_text = os.getcwd()
        ori_path = current_text.split()[-1]     # 获取当前输入的命令的最后一个参数，即路径
        path = normabs(ori_path)                # 规范化路径
        path = path.replace('~', os.path.expanduser('~'))
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        files_info = LsCommand(dirname).get_file_info_list(dirname)
        suggestions = []
        
        for file in files_info:
            filename = os.path.basename(file["fullpath"])
            if re.match(basename, filename):
                suggestions.append(filename)
        if not suggestions:                     # 如果没有文件名以base开头，则不补全
            return
        elif len(suggestions) == 1:             # 如果只有一个文件名以base开头，则直接补全
            CmdWindow.session.app.current_buffer.insert_text(suggestions[0][len(os.path.basename(path)):])
            if os.path.isdir(os.path.join(dirname, suggestions[0])):
                CmdWindow.session.app.current_buffer.insert_text('/')
            else:
                CmdWindow.session.app.current_buffer.insert_text(' ')
        else:
            if CmdWindow.tab_two:
                LsCommand(f"-a {path}*").execute()
            CmdWindow.tab_two = not CmdWindow.tab_two

if __name__ == '__main__':
    cmd_window = CmdWindow()
    cmd_window.run()