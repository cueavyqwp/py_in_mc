from __future__ import print_function
from __future__ import unicode_literals
from prompt_toolkit import prompt

from contextlib import redirect_stdout
from io import StringIO

import subprocess
import traceback
import threading
import os

home = os.getcwd()

s = subprocess.Popen("java -Xms1G -Xmx2G -jar server.jar nogui",stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

Run = True

def output() :
    code = None
    code_old = None
    while Run :
        try:
            out = s.stdout.readline().decode("utf-8")
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
                        while code[-3:] != "\r\\n":
                            code_ = "\\n" + s.stdout.readline().decode("utf-8").replace("\n","\\n")
                            code += code_
                        else:
                            code = code[:-4]
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
            print()
            print(e.args[0])
            print()
            print(traceback.format_exc())
            print()
    s.terminate()

output_thread = threading.Thread( target = output )
output_thread.start()

while Run :
    user_comm = prompt().strip()
    if len(user_comm) :
        if user_comm.lower() == 'q':
            Run = False
        elif ( len(user_comm) - 1 ) and user_comm[0] == "/" :
            s.stdin.write( ( user_comm + "\n" ).encode("utf-8") )
            s.stdin.flush()