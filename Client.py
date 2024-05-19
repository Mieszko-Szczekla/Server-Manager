from requests import get
import json


IP_ADDR = '172.25.84.29'
PORT = 2137
KEY = b'_secret_example_'


class RemoteMachine:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.name = f'http://{host}:{port}/'

    def is_installed(self, package):
        response = get(self.name+'is_installed', params = {'package': package})
        if response.status_code != 200:
            raise ConnectionError(f'Response code {response.status_code}')
        content = json.loads(response.content)
        if content['result'] == 'Err':
            raise ValueError()
        return 'True' == content['result']


if __name__=='__main__': # test
    rm = RemoteMachine(IP_ADDR, PORT)
    print(rm.is_installed('tree'))
    print(rm.is_installed('tldr'))
    print(rm.is_installed('non-existent-package'))
    print(rm.is_installed('man-db'))