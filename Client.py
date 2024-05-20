from requests import get
import json
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from datetime import datetime
from functools import reduce
from operator import add


IP_ADDR = '192.168.64.13'
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

    '''def is_installed(self, package):
        response = get(self.name+'is_installed', params = {'package': package})
        if response.status_code != 200:
            raise ConnectionError(f'Response code {response.status_code}')
        content = json.loads(self.decrypted(response.content).decode())
        if content['result'] == 'Err':
            raise ValueError()
        return 'True' == content['result']'''

    def ls(self, path):
        result = rm.call_api_encrypted('ls', path=path)['result']
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

    def is_installed(self, package):
        return rm.call_api_encrypted('is_installed', package = package)['result']

    


if __name__=='__main__': # test
    rm = RemoteMachine(IP_ADDR, PORT)

    print(rm.ls(path='/home/mieszko/Desktop'))
    print(rm.is_installed('tree'))
    print(rm.is_installed('tldr'))
    print(rm.is_installed('non-existent-package'))
    print(rm.is_installed('man-db'))