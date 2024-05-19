import configparser
import LocalSystem
from flask import Flask, jsonify, request
from waitress import serve

KEY = b'_secret_example_'

app = Flask(__name__)


@app.route('/is_installed', methods=['GET'])
def get_is_installed():
    package = request.args.get('package')
    if package is None:
        return jsonify({'result' : 'Err'})
    result = str(LocalSystem.is_installed(package))
    return jsonify({'result': result})

if __name__ == '__main__':
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