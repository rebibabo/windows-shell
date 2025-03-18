
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Punctuation, Whitespace, Text, Comment, Operator, Keyword, Name, String, Number
import os
import re

def get_all_executed_commands(paths):
    cmds = []
    for path in paths:
        if not path:
            continue
        if os.path.isdir(path):  # 检查路径是否为目录
            for file in os.listdir(path):  # 遍历目录中的文件
                full_path = os.path.join(path, file)  # 获取文件的完整路径
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):  # 检查文件是否可执行
                    cmds.append(file)  # 添加到命令列表中
    return cmds

# 获取系统的 PATH 环境变量
paths = os.getenv('PATH').split(':')

# 获取所有可执行命令
commands = get_all_executed_commands(paths)
commands = sorted([re.escape(cmd) for cmd in set(commands)])
if not commands:
    commands = ['ls', 'cd', 'pwd', 'echo', 'cat', 'grep', 'find', 'cp', 'rm', 'rmdir', 'touch', 'ln', 'head', 'tail', 'date', 'cal', 'whoami', 'who', 'history', 'alias', 'unalias', 'jobs', 'kill', 'killall', 'bg', 'fg', 'exit', 'logout', 'clear', 'history', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis', 'which', 'whereis',]

class ShellLexer(RegexLexer):
    """
    Lexer for shell scripts.

    .. versionadded:: 1.0
    """

    name = 'Shell'
    aliases = ['shell', 'sh']
    filenames = ['*.sh', '*.bash', '*.zsh', '*.ksh']
    mimetypes = ['application/x-sh', 'application/x-shellscript', 'text/x-shellscript']

    tokens = {
        'root': [
            include('basic'),
            (r'`', String.Backtick, 'backticks'),
            include('data'),
            include('interp'),
        ],
        'interp': [
            (r'\$\(\(', Keyword, 'math'),
            (r'\$\(', Keyword, 'paren'),
            (r'\$\{#?', String.Interpol, 'curly'),
            (r'\$[a-zA-Z_]\w*', Name.Variable),  # user variable
            (r'\$(?:\d+|[#$?!_*@-])', Name.Variable),  # builtin
            (r'\$', Text),
        ],
        'basic': [
            (r'\b(if|fi|else|while|in|do|done|for|then|return|case|'
             r'select|continue|until|esac|elif)(\s*)\b',
             bygroups(Keyword, Whitespace)),
            (rf'\b({"|".join(commands)})\b', Keyword), 
            (r'\A#!.+\n', Comment.Hashbang),
            (r'#.*\n', Comment.Single),
            (r'\\[\w\W]', String.Escape),
            (r'(\b\w+)(\s*)(\+?=)', bygroups(Name.Variable, Whitespace, Operator)),
            (r'[\[\]{}()=]', Operator),
            (r'<<<', Operator),  # here-string
            (r'<<-?\s*(\'?)\\?(\w+)[\w\W]+?\2', String),
            (r'&&|\|\|', Operator),
        ],
        'data': [
            (r'(?s)"(.*?)"', String.Double),  # Double quoted string
            (r'(?s)\'(.*?)\'', String.Single),  # Single quoted string
            (r'(?s)\$"(.*?)"', String.Double),  # Variable inside double quotes
            (r'(?s)\$\'(.*?)\'', String.Single),  # Variable inside single quotes
            # Flags and parameters
            (r'(-{1,2}\w+)', Name.Tag),  # Hyphenated parameters (e.g., -s, --verbose)
            (r';', Punctuation),
            (r'\s+', Whitespace),
            (r'\d+', Number),
            (r'[^=\s\"\'`<>;]+', Text),
            (r'<|>', Text),  # Input/output redirection
        ],
        'math': [
            (r'\)\)', Keyword, '#pop'),
            (r'[-+*/%^|&]|\*\*|\|\|', Operator),
            (r'\d+#\d+', Number),
            (r'\d+#(?! )', Number),
            (r'\d+', Number),
            include('root'),
        ],
        'backticks': [
            (r'`', String.Backtick, '#pop'),
            include('root'),
        ],
        'curly': [
            (r'\}', String.Interpol, '#pop'),
            (r'\w+', Name.Variable),
            include('root'),
        ],
        'paren': [
            (r'\)', Keyword, '#pop'),
            include('root'),
        ],
    }

    def analyse_text(text):
        if text.startswith('#!'):
            return 1
        if text.startswith('$ '):
            return 0.2
