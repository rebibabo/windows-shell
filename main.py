import os
os.system('cls')
from cmd import Cmd
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import print_formatted_text as print
import getpass
user = getpass.getuser()

class CmdHistory:
    def __init__(self, max_size=100):
        self.max_size = max_size
        self.history = []
        if not os.path.exists('history.txt'):
            with open('history.txt', 'w') as f:
                f.write('')
            return
        with open('history.txt', 'r') as f:
            for line in f:
                self.history.append(line.strip())
                
    def clear(self, left_num=0):
        if left_num == 0:
            self.history = []
        else:
            self.history = self.history[-left_num:] 
        with open('history.txt', 'w') as f:
            for cmd in self.history:
                f.write(cmd+'\n')     
                
    def add(self, cmd):
        self.history.append(cmd)
        with open('history.txt', 'a') as f:
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
    style = Style.from_dict({
        # User input (default text).
        # '':         '#ff0066',

        # Prompt.
        'username': '#20fe8b',
        'at':       '#20fe8b',
        'colon':    '#ffffff',
        'dollar':   '#ffffff',
        'host':     '#20fe8b',
        'path':     '#28a0ea underline',
    })
    
    def __init__(self):
        self.cmd_history = CmdHistory()
        history = InMemoryHistory(self.cmd_history.data)
        self.session = PromptSession(history=history)
        
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
                text = self.session.prompt(prefix, style=self.style, auto_suggest=AutoSuggestFromHistory())
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

if __name__ == '__main__':
    cmd_window = CmdWindow()
    cmd_window.run()