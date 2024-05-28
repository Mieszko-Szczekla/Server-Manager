import configparser
import LocalSystem
from flask import Flask, jsonify, request
import json
from waitress import serve
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from functools import reduce
from operator import add
from random import choices
import string
import os

app = Flask(__name__)

def encrypted(data):
    return cipher.encrypt(pad(data, AES.block_size))

def decrypt_json(data):
    return json.loads(unpad(cipher.decrypt(data), AES.block_size).decode())

def encrypt_json(data):
    return cipher.encrypt(pad(json.dumps(data).encode(), AES.block_size))

def encrypted_traffic(func):
    def res(): 
        kwargs = decrypt_json(request.data)
        if not kwargs.pop('valid', False):
            return {'error': 'Invalid request'}
        result = func(**kwargs)
        result['valid'] = True
        print(f'{func.__name__}({kwargs}) -> {result}')
        return encrypt_json(result)
    res.__name__ = 'encrypted_'+func.__name__#reduce(add, choices(string.ascii_letters, k=40), '')
    return res

@app.route('/echo', methods=['GET'])
@encrypted_traffic
def get_echo():
    return {}

@app.route('/ls', methods=['GET'])
@encrypted_traffic
def get_ls(path):
    return {'is_dir':os.path.isdir(path), 'result': LocalSystem.ls(path)}

@app.route('/is_installed', methods=['GET'])
@encrypted_traffic
def get_is_installed(package):
    return {'result': LocalSystem.is_installed(package)}

@app.route('/install', methods=['GET'])
@encrypted_traffic
def get_install(package):
    response_code, stdout = LocalSystem.install(package)
    return {'response_code': response_code, 'success': LocalSystem.is_installed(package)}

@app.route('/purge', methods=['GET'])
@encrypted_traffic
def get_purge(package):
    response_code, stdout = LocalSystem.purge(package)
    return {'response_code': response_code, 'installed': LocalSystem.is_installed(package)}

@app.route('/rm', methods=['GET'])
@encrypted_traffic
def get_rm(path):
    return {'response_code': LocalSystem.rm(path)}

@app.route('/mkdir', methods=['GET'])
@encrypted_traffic
def get_mkdir(path):
    return {'response_code': LocalSystem.mkdir(path)}

@app.route('/hostname_get', methods=['GET'])
@encrypted_traffic
def get_hostname_get():
    return {'hostname': LocalSystem.get_hostname()}

@app.route('/hostname_set', methods=['GET'])
@encrypted_traffic
def get_hostname_set(hostname):
    return {'response_code': LocalSystem.set_hostname(hostname)}

@app.route('/user_list', methods=['GET'])
@encrypted_traffic
def get_user_list():
    return {'result': LocalSystem.user_list()}

@app.route('/user_del', methods=['GET'])
@encrypted_traffic
def get_user_del(username):
    return {'success': LocalSystem.del_user(username)}

@app.route('/user_add', methods=['GET'])
@encrypted_traffic
def get_user_add(username):
    return {'success': LocalSystem.add_user(username)}

@app.route('/passwd', methods=['GET'])
@encrypted_traffic
def get_passwd(username, password):
    LocalSystem.passwd(username, password)
    return {}

@app.route('/set_path')

def remove_padding(text):
    while(text[-1] == '/'):
        text = text[:-1]
    return text

@app.route('/push', methods=['GET'])
def get_push():
    data = unpad(cipher.decrypt(request.data), AES.block_size)
    path = remove_padding(data[:4096].decode())
    filecontent = data[4096:]

    with open(path, 'wb') as file:
        file.write(filecontent)
    LocalSystem.permit_access(path)
    return ''

@app.route('/pull', methods=['GET'])
def get_pull():
    path = unpad(cipher.decrypt(request.data), AES.block_size).decode()
    with open(path, 'rb') as file:
        return cipher.encrypt(pad(file.read(), AES.block_size))

if __name__ == '__main__':
    if LocalSystem.whoami() != 'root':
        print('You must run this software as root!')
        exit(-1)
    config_parser = configparser.RawConfigParser()
    config_path = './config.txt'
    config_parser.read(config_path)
    if 'SERVER' not in config_parser:
        print(f'Invalid config! Ensure that file "{config_path}" exists and see README!')
        exit(-2)
    if 'Host' not in config_parser['SERVER'] or 'PortNumber' not in config_parser['SERVER'] or 'Password' not in config_parser['SERVER']:
        print('Invalid config! See README!')
        exit(-2)
    host = config_parser['SERVER']['Host']
    try:
        port = int(config_parser['SERVER']['PortNumber'])
    except ValueError:
        print('Invalid config! Port number must be a number. See README!')
        exit(-2)
    password = config_parser['SERVER']['Password'].strip()

    cipher = AES.new(SHA256.new(data=password.encode()).digest()[:16], AES.MODE_ECB)
    serve(app, host=host, port=port)