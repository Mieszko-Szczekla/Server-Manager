import configparser
import LocalSystem
from flask import Flask, jsonify, request
from waitress import serve
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES

KEY = b'_secret_example_'

app = Flask(__name__)


def encrypt(data):
    return cipher.encrypt(pad(data, AES.block_size))

@app.route('/is_installed', methods=['GET'])
def get_is_installed():
    package = request.args.get('package')
    if package is None:
        return jsonify({'result' : 'Err'})
    result = str(LocalSystem.is_installed(package))
    return jsonify({'result': result})

@app.route('/data', methods=['GET'])
def get_data():
    return cipher.encrypt(pad(b'random_data', AES.block_size))

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