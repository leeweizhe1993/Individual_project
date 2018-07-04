import os
from multiprocessing import Process
def run_proc(name):   #子进程要执行的代码
    print("Run child process %s (%s)..." % (name, os.getpid()))

if __name__ == '__main__':
    print("Parent process %s." % os.getpid())
    for i in range(5):
        p = Process(target = run_proc, args = (str(i), ))
        print("Child process will start")
        p.start()
    p.join()
    print("Child process end.")