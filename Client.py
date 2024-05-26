from requests import get
import json
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from datetime import datetime
from functools import reduce
from operator import add
from bs4 import BeautifulSoup


IP_ADDR = '192.168.122.27'
PORT = 2137
KEY = b'_secret_example_'


class RemoteMachine:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.name = f'http://{host}:{port}/'
        self.cipher = AES.new(KEY, AES.MODE_ECB)

    def decrypted(self, data):
        return unpad(self.cipher.decrypt(data), AES.block_size)

    def decrypt_json(self, data):
        return json.loads(unpad(self.cipher.decrypt(data), AES.block_size).decode())

    def encrypt_json(self, data):
        return self.cipher.encrypt(pad(json.dumps(data).encode(), AES.block_size))

    def call_api_encrypted(self, hook, **kwargs):
        encrypted_kwargs = self.encrypt_json(kwargs)
        response = get(self.name+hook, data=encrypted_kwargs)# params = {'args': encrypted_kwargs})
        if response.status_code != 200:
            raise ConnectionError(f'Response code {response.status_code}')
        return self.decrypt_json(response.content)

    def ls(self, path):
        result = self.call_api_encrypted('ls', path=path)['result']
        def parse_ls_line(line):
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
        files = result.split('\n')[3:-1]
        return list(map(parse_ls_line, files))

    def package_search(term):
        querry = 'https://packages.debian.org/search?suite=stable&section=all&arch=any&searchon=names&keywords='+term.replace(' ', '+')
        html = BeautifulSoup(get(querry).text, 'html.parser')
        return list(map(lambda element: element.text[8:], html.select('h3')))

    def package_info(package):
        querry = 'https://packages.debian.org/bookworm/'+package
        html = BeautifulSoup(get(querry).text, 'html.parser')
        decriptions = html.select('.pdesc')[0].children
        return {'title': descriptions[0].text, 'description':description[1].text}

    def is_installed(self, package):
        return self.call_api_encrypted('is_installed', package = package)['result']

    def install(self, package):
        response = self.call_api_encrypted('install', package=package)
        if response['success']:
            return None
        return response['response_code']

    def purge(self, package):
        response = self.call_api_encrypted('purge', package=package)
        if not response['installed']:
            return None
        return response['response_code']

    def rm(self, path):
        response = self.call_api_encrypted('rm', path=path)
        return response['response_code'] == 0

    def mkdir(self, path):
        response = self.call_api_encrypted('mkdir', path=path)
        return response['response_code'] == 0

    hostname = property(
        fget= lambda self: self.call_api_encrypted('hostname_get')['hostname'], 
        fset= lambda self, new_hostname: self.call_api_encrypted('hostname_set', hostname = new_hostname)
    )
    
    def user_list(self):
        return self.call_api_encrypted('user_list')['result']
        
    def user_add(self, username):
        return self.call_api_encrypted('user_add', username=username)['success']

    def user_del(self, username):
        return self.call_api_encrypted('user_del', username=username)['success']

        


if __name__=='__main__': # test
    rm = RemoteMachine(IP_ADDR, PORT)
    '''
    print(rm.ls(path='/home/mieszko/Desktop'))
    print(rm.is_installed('tldr'), 'should be True')
    print(rm.is_installed('non-existent-package'), 'should be False')
    print(rm.is_installed('man-db'), 'should be True')

    print(rm.install('tree'), 'should be None')
    print(rm.install('non-existent-package'), 'should be 100')
    print(rm.is_installed('tree'), 'should be True')

    print(rm.purge('tree'), 'should be None')
    print(rm.purge('non-existent-package'), 'should be None')
    print(rm.is_installed('tree'), 'should be False')
    '''
    # print(RemoteMachine.package_info('firefox-esr'))
    rm.hostname = 'vm'
    while(True):
        try:
            print(eval(input('>> ')))
        except Exception as ex:
            print(ex)