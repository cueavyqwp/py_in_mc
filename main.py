from __future__ import unicode_literals
from __future__ import print_function
from prompt_toolkit import prompt

from contextlib import redirect_stdout
from io import StringIO

from time import sleep
import subprocess
import traceback
import threading
import os

home = os.getcwd()
s = subprocess.Popen("java -Xms1G -Xmx2G -jar server.jar nogui",stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
Run = True

def oos(S):
    ret = os.system(S+">a.txt")
    with open("a.txt",encoding="gbk") as f:
        print(f.read())
    if not ret :
        ret = ''
    return ret

def run_c(S):
    with open("a.c","w",encoding="utf-8") as f:
        f.write(S)
    ret = ""
    ret += oos("gcc a.c")
    ret += oos("a.exe")
    print(ret)
    return ret

def run_cpp(S):
    with open("a.cpp","w",encoding="utf-8") as f:
        f.write(S)
    ret = ""
    ret += oos("g++ a.cpp")
    ret += oos("a.exe")
    print(ret)
    return ret

def run_java(S):
    with open("a.java","w",encoding="utf-8") as f:
        f.write(S)
    ret = ""
    ret += oos("javac a.java")
    ret += oos("java a")
    print(ret)
    return ret

def output() :
    code = None
    code_old = None
    while Run :
        try:
            out = s.stdout.readline().decode("utf-8",errors="ignore")
            if out:
                print(out[:-1])
                code = out.split("block data: ")
                get = out.split("!run ")
                if len(get) -1 :
                    get = get[1][:-2]
                    s.stdin.write( ( f"data get block {get} Book\n" ).encode("utf-8") )
                    s.stdin.flush()
                if code :
                    if ( len(code) - 1 ) and code != code_old :
                        code_old = code
                        code = code[1].split("tag: ")[1].replace("pages","\"pages\"").replace('\\"','"')[:-1]
                        if code[-3:] != "}}\r" :
                            while ( code[-3:] != "\r\\n" ) :
                                code_ = "\\n" + s.stdout.readline().decode("utf-8").replace("\n","\\n")
                                code += code_
                            else :
                                code = code[:-4]
                        else :
                            code = code[:-2]
                        code = eval(code)["pages"]
                        block = ""
                        for i in code :
                            if i :
                                block += i
                                block += "\n"
                        f = StringIO()
                        with redirect_stdout(f) :
                            exec(block)
                        for i in f.getvalue().split("\n") :
                            if i :
                                s.stdin.write( ( f"say {i}\n" ).encode("utf-8") )
                                s.stdin.flush()
                        os.chdir(home)
        except Exception as e :
            error = traceback.format_exc()
            # print()
            # print(e.args[0])
            # print()
            # print(error)
            s.stdin.write( ( f"say {e.args[0]}\n" ).encode("utf-8") )
            s.stdin.flush()
            for i in error.split("\n"):
                if i :
                    s.stdin.write( ( f"say {i}\n" ).encode("utf-8") )
                    s.stdin.flush()
            print()
    s.terminate()

output_thread = threading.Thread( target = output )
output_thread.start()

while Run :
    user_comm = prompt().strip()
    if len(user_comm) :
        if user_comm.lower() == 'q':
            s.stdin.write( b"stop\n" )
            s.stdin.flush()
            sleep(10)
            Run = False
        elif ( len(user_comm.lower()) - 1 ) and user_comm[0] == "/" :
            s.stdin.write( ( user_comm + "\n" ).encode("utf-8") )
            s.stdin.flush()