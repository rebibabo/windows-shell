
import re
import os
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Punctuation, Whitespace, Text, Comment, Operator, Keyword, Name, String, Number
    
class ShellLexer(RegexLexer):
    """
    Lexer for shell scripts.

    .. versionadded:: 1.0
    """

    name = 'Shell'
    aliases = ['shell', 'sh']
    filenames = ['*.sh', '*.bash', '*.zsh', '*.ksh']
    mimetypes = ['application/x-sh', 'application/x-shellscript', 'text/x-shellscript']

    def get_all_executed_commands(paths):
        cmds = []
        for path in paths:
            if not path:
                continue
            if path.endswith('.exe'):
                cmds.append(os.path.basename(path)[:-4])
            elif os.path.isdir(path):
                for file in os.listdir(path):
                    if file.endswith('.exe'):
                        cmds.append(file[:-4])
        return cmds
                
    import winreg as reg

    paths = os.getenv('path')
    cmds = get_all_executed_commands(paths.split(';'))

    key = reg.OpenKey(reg.HKEY_CURRENT_USER, r'Environment', 0, reg.KEY_READ)
    try:
        paths, regtype = reg.QueryValueEx(key, 'PATH')
        cmds.extend(get_all_executed_commands(paths.split(';')))
    finally:
        reg.CloseKey(key)

    cmds = sorted([re.escape(cmd) for cmd in set(cmds)])    # 去重+转义+排序，c++这种不转义会报错

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
            (rf'\b({"|".join(cmds)})(?=[\s)`])', Keyword),  
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
