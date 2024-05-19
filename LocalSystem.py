import subprocess
import re
from operator import add
from functools import reduce
from datetime import datetime

REGEX_LS = re.compile(r'')

def parse_command(command):
    match command[0]:
        case 'I':
            install(command[1:]) # -> bool
        case 'P':
            purge(command[1:]) # -> bool
        case 'i':
            is_installed(command[1:]) # -> bool
        case 'l':
            ls(command[1:]) # -> List[string]
        case 'r':
            rm_rf(command[1:]) # -> bool
        case 'p':
            push(command[1:]) # -> None / await
        case 'g':
            get(command[1:]) # -> file
        case 'h':
            get_hostname() # -> string
        case 'H':
            set_hostname(command[1:]) # -> None
        case 'c':
            cron.ls() # -> List[cron.task]
        case 'C':
            cron.add(command[1:]) # -> None
        case 'R':
            cron.remove(int(command[1:])) # -> None    

def run(cmd):
    sub = subprocess.run(['echo'] + cmd.split(), stdout=subprocess.PIPE)
    return (sub.returncode, sub.stderr, sub.stdout)

def runAs(user, command):
    return subprocess.run(['su', '-', user, '-c', command], stdout=subprocess.PIPE)

def is_installed(package):
    return subprocess.run(['dpkg', '-s', package], stdout=-1, stderr=-1).returncode == 0

def install(package):
    sub = subprocess.run(['apt', 'install', '-y', package], stdout=-1, stderr=-1)
    return (sub.returncode, sub.stdout)

def purge(package):
    sub = subprocess.run(['apt', 'purge', '-y', package], stdout=-1, stderr=-1)
    return (sub.returncode, sub.stdout)

def parse_ls_line(line):
    # print(f'[LINE] {line=}')
    values = line.split()
    return {
        'permissions': values[0][1:],
        'is_directory': values[0][0] == 'd',
        'id': values[1],
        'user': values[2],
        'group': values[3],
        'size': values[4],
        'datetime': datetime.strptime(f"{values[5]} {values[6]} {values[7]}", '%b %d %H:%M'),
        'filename': reduce(add, values[8:], '')
    }

def ls(dir):
    cmd_res = subprocess.run(['ls', '-alh', dir], stdout=subprocess.PIPE).stdout
    files = cmd_res.decode().split('\n')[3:-1]
    return list(map(parse_ls_line, files))
    
def mkdir(path):
    ...

def push(path):
    ...


if __name__ == '__main__':
    print(install('python3-pip'))
    print(is_installed('tree'))

