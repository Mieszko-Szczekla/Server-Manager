from requests import get, put
import json
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from datetime import datetime
from functools import reduce
from operator import add


class RemoteMachine:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.name = f'http://{host}:{port}/'
        self.cipher = AES.new(SHA256.new(data=password.encode()).digest()[:16], AES.MODE_ECB)

    def decrypted(self, data):
        return unpad(self.cipher.decrypt(data), AES.block_size)

    def decrypt_json(self, data):
        return json.loads(unpad(self.cipher.decrypt(data), AES.block_size).decode())

    def encrypt_json(self, data):
        return self.cipher.encrypt(pad(json.dumps(data).encode(), AES.block_size))

    def call_api_encrypted(self, hook, **kwargs):
        kwargs['valid'] = True
        encrypted_kwargs = self.encrypt_json(kwargs)
        response = get(self.name+hook, data=encrypted_kwargs)# params = {'args': encrypted_kwargs})
        if response.status_code != 200:
            raise ConnectionError(f'Response code {response.status_code}')
        decrypted = self.decrypt_json(response.content)
        if 'valid' not in decrypted or not decrypted['valid']:
            raise ValueError('Invalid response')
        return decrypted

    def ls(self, path):
        answer = self.call_api_encrypted('ls', path=path)
        if not answer['is_dir']:
            return None
        result = answer['result']
        def parse_ls_line(line):
            values = line.split()
            try:
                date = datetime.strptime(f"{values[5]} {values[6]} {values[7]}", '%b %d %H:%M')
            except ValueError:
                date = None

            return {
                'permissions': values[0][1:],
                'is_directory': values[0][0] == 'd',
                'id': values[1],
                'user': values[2],
                'group': values[3],
                'size': values[4],
                'datetime': date,
                'filename': reduce(add, values[8:], '')
            }
        files = result.split('\n')[3:-1]
        return list(map(parse_ls_line, files))

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
    
    def passwd(self, username, password):
        return self.call_api_encrypted('passwd', username=username, password=password)['valid']
    
    def push(self, source, destination):
        path = destination.encode()
        path = path + b'/'*(4096-len(path))
        with open(source, 'rb') as file:
            get(self.name+'push', data = self.cipher.encrypt(pad(path+file.read(), AES.block_size)))

    def pull(self, source, destination):
        path = source.encode()
        response = get(self.name+'pull', data = self.cipher.encrypt(pad(path, AES.block_size)))
        filecontent = unpad(self.cipher.decrypt(response.content), AES.block_size)
        with open(destination, 'wb') as file:
            file.write(filecontent)

    def ping(self):
        try:
            self.call_api_encrypted('echo')
            return True
        except:
            return False