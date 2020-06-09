#! /usr/bin/env python3

import os, sys, tempfile
from re import search

class State:
    def __init__(self):
        self.cdir = os.environ["HOME"] + "/.config/compress-pdf"
        self.file = self.cdir + "/config"
        if not os.path.isdir(self.cdir):
            os.mkdir(self.cdir, 0o755)
        if not os.path.isfile(self.file):
            with open(self.file, 'w') as f:
                f.write("""RememberLastDir false
LastDir /home
OutputFilename auto""")
        self.outputfilename = self.getOutFileOpt()
        self.lastdirstat = self.getLastDirStat()
        self.lastdir = self.getLastDir()
       
    def getOpt(self, option):
        if option == "OutputFilename":
            option = '^' + option + " +(auto|manual) *\\n{0,1}"
        elif option == "RememberLastDir":
            option = '^' + option + " +(true|false) *\\n{0,1}"
        elif option == "LastDir":
            option = '^' + option + " +(.+) *\\n{0,1}"
        with open(self.file, 'r') as f:
            for line in f:
                val = search(option, line)
                if val != None:
                    return val.group(1).rstrip()
        return None
        
    def getOutFileOpt(self):
        tmp = self.getOpt("OutputFilename")
        if tmp == None:
            return "auto"
        return tmp
        
        
    def getLastDirStat(self):
        tmp = self.getOpt("RememberLastDir")
        if tmp == "true":
            return True
        else:
            return False
        
    def getLastDir(self):
        tmp = self.getOpt("LastDir")
        if tmp == None:
            return "/home"
        return tmp
        
    def setOpt(self, option, value):
        tmp = self.getOpt(option)
        if tmp == None:
            with open(self.file, 'a') as f:
                f.write(f"{option} {value}\n")
                return None
        if tmp == value:
            return None
        if option == "OutputFilename":
            option = '(^' + option + " +)(auto|manual) *\\n{0,1}"
        elif option == "RememberLastDir":
            option = '(^' + option + " +)(true|false) *\\n{0,1}"
        elif option == "LastDir":
            option = '(^' + option + " +)(.+) *\\n{0,1}"
        _f = None
        with open(self.file, 'r') as f:
            _f = tempfile.NamedTemporaryFile(delete=False)
            for line in f:
                val = search(option, line)
                if val != None:
                    _f.file.write(f"{val.group(1)}{value}\n".encode("utf-8"))
                    continue
                _f.file.write(line.encode("utf-8"))
        _f.close()
        shutil.move(_f.name, self.file)
        return None
    
    def togLastDirStat(self):
        tmp = self.getLastDirStat()
        if tmp:
            self.setOpt("RememberLastDir", "false")
            self.lastdirstat = False
        else:
            self.setOpt("RememberLastDir", "true")
            self.lastdirstat = True
    
    def setOutFileOpt(self, val):
        self.setOpt("OutputFilename", val)
        self.outputfilename = val
        
    def setLastDir(self, dir):
        if dir != "":
            self.setOpt("LastDir", dir)
            self.lastdir = dir
