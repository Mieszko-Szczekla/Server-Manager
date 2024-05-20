import configparser
import LocalSystem
from flask import Flask, jsonify, request
import json
from waitress import serve
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from functools import reduce
from operator import add
from random import choices
import string

KEY = b'_secret_example_'
function_container = []

app = Flask(__name__)


def encrypted(data):
    return cipher.encrypt(pad(data, AES.block_size))

def decrypt_json(data):
    return json.loads(unpad(cipher.decrypt(data), AES.block_size).decode())

def encrypt_json(data):
    return cipher.encrypt(pad(json.dumps(data).encode(), AES.block_size))

def encrypted_traffic(func):
    res = lambda: encrypt_json(func(**decrypt_json(request.data)))
    res.__name__ = reduce(add, choices(string.ascii_letters, k=40), '')
    return res

@app.route('/ls', methods=['GET'])
@encrypted_traffic
def get_ls(path):
    files = LocalSystem.ls(path)
    print(files)
    return {'result': files}

@app.route('/is_installed', methods=['GET'])
@encrypted_traffic
def get_is_installed(package):
    return {'result': LocalSystem.is_installed(package)}


'''def get_is_installed():
    package = request.args.get('package')
    if package is None:
        result = 'Err'
    else:
        result = str(LocalSystem.is_installed(package))
    return encrypted(json.dumps({'result': result}).encode())'''

if __name__ == '__main__':
    cipher = AES.new(KEY, AES.MODE_ECB)
    config_parser = configparser.RawConfigParser()
    config_path = './config.txt'
    config_parser.read(config_path)
    if 'SERVER' not in config_parser:
        print(f'Invalid config! Ensure that file "{config_path}" exists and see README!')
        exit(-1)
    if 'Host' not in config_parser['SERVER'] and 'PortNumber' not in config_parser['SERVER']:
        print('Invalid config! See README!')
        exit(-1)
    host = config_parser['SERVER']['Host']
    try:
        port = int(config_parser['SERVER']['PortNumber'])
    except ValueError:
        print('Invalid config! Port number must be a number. See README!')
        exit(-1)
    serve(app, host=host, port=port)