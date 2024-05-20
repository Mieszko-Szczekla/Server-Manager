import subprocess

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

def ls(dir):
    cmd_res = subprocess.run(['ls', '-alh', dir], stdout=subprocess.PIPE).stdout
    return cmd_res.decode()
    
def mkdir(path):
    ...

def push(path):
    ...


if __name__ == '__main__':
    print(install('python3-pip'))
    print(is_installed('tree'))

