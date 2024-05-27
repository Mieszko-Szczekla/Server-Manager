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

def get_hostname():
    return subprocess.run(['hostname'], stdout=-1, stderr=-1).stdout.decode().strip()

def set_hostname(new_name) -> int:
    return subprocess.run(['hostnamectl', 'set-hostname', f'{new_name}'], stdout=-1, stderr=-1).returncode
    

def ls(dir):
    cmd_res = subprocess.run(['ls', '-alh', dir], stdout=subprocess.PIPE).stdout
    return cmd_res.decode()
    
def whoami():
    return subprocess.run(['whoami'], stdout=subprocess.PIPE).stdout.decode().strip()

def mkdir(path):
    return subprocess.run(['mkdir', '-p', path], stdout=-1, stderr=-1).returncode

def rm(path):
    return subprocess.run(['rm', '-rf', path], stdout=-1, stderr=-1).returncode

def passwd(user, password):
    subprocess.Popen(['passwd', user], stdin=subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate(input=f'{password}\n{password}'.encode())

def user_list():
    def read_log(log):
        parts = log.split(':')
        if parts[-1] not in ('/usr/sbin/nologin', '/bin/false', '/bin/sync'):
            return parts[0]
    response = subprocess.run(['cat', '/etc/passwd'], stdout=-1, stderr=-1).stdout.decode()
    return list(filter(lambda x: x is not None, map(read_log, response.split('\n')[:-1])))
    
def add_user(username):
    return subprocess.run(['useradd', '--create-home', username], stdout=-1, stderr=-1).returncode == 0
  
def del_user(username):
    return subprocess.run(['userdel', '--remove', username], stdout=-1, stderr=-1).returncode == 0

if __name__ == '__main__':
    print(del_user('user2137'))
    print(users_list())

