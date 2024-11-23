from cmd.ls import LsCommand
from cmd.pwd import PwdCommand
from cmd.mkdir import MkdirCommand
from cmd.touch import TouchCommand
from cmd.rm import RmCommand
from cmd.cat import CatCommand
from cmd.cp import CpCommand
from cmd.mv import MvCommand
from cmd.cd import CdCommand
from cmd.kill import KillCommand
from cmd.ps import PsCommand
from cmd.wget import WgetCommand
from cmd.tar import TarCommand
import os

class Cmd:
    def __init__(self, cmd):
        type = cmd.split()[0]
        command = ' '.join(cmd.split()[1:])
        try:
            command = eval(f"{type.capitalize()}Command(command)")
            command.execute()
        except:
            os.system(cmd)