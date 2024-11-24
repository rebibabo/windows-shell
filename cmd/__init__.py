commands = ['ls', 'pwd','mkdir', 'touch', 'rm', 'cat', 'cp', 'mv', 'cd', 'kill', 'ps', 'wget', 'tar']
for command in commands:
    exec(f"from cmd.{command} import {command.capitalize()}Command")
    
import os

class Cmd:
    def __init__(self, cmd):
        type = cmd.split()[0]
        command = ' '.join(cmd.split()[1:])
        if type in commands:
            try:
                command = eval(f"{type.capitalize()}Command(command)")
                command.execute()
            except:
                pass
        else:
            os.system(cmd)
            