#!/usr/bin/env python3
import os, subprocess, multiprocessing

HOME = os.path.expanduser('~')

def getShell():
    shell = os.environ.get('SHELL')
    if isinstance(shell, str):
        shell = shell.lower().split('/')[-1]
    return shell

def getFiles():
    return [i for i in subprocess.check_output(['locate', '/man/']).decode().split('\n') if len(i) > 3 and os.path.isfile(i) and i[-3:] == '.gz']

def genCompletionList(manPages):
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count() - 1)
    command = './run.sh '
    if getShell() == 'bash':
        command = 'BASH_NO_DESCRIPTIONS=1 ' + command
    pool.map_async(os.system, [command + i for i in manPages])
    pool.close()
    pool.join()
    
    print("Changing the permission of the files...")
    #  os.system("chmod -R +r completions")
        
def appendPath():
    shell = getShell()
    if shell == None:
        return

    added = False
    if shell == 'zsh':
        with open(HOME + '/.zshrc', 'r') as fin:
            for i in fin.readlines():
                if 'fpath+=({})'.format(os.getcwd() + '/completions/zsh/') == i.replace('\n', ''):
                    added = True
                    break
        if not added:
            with open(HOME + '/.zshrc', 'a') as fin:
                fin.write('\nfpath+=({})\n'.format(os.getcwd() + '/completions/zsh/'))

    elif shell == 'bash':
        with open(HOME + '/bashrc', 'r') as fin:
            for i in fin.readlines():
                if 'source {}/completions/bash/*'.format(os.getcwd()) == i.replace('\n', ''):
                    added = True
                    break

        if not added:
            with open(HOME + '/bashrc', 'a') as fin:
                fin.write('\nsource {}/completions/bash/*\n'.format(os.getcwd()))

if __name__ == '__main__':
    try:
        genCompletionList(getFiles())
        appendPath()
    except KeyboardInterrupt:
        exit(1)
