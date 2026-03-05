import requests
try:
    r = requests.get('http://127.0.0.1:5000/api/network/data', timeout=10)
    print(r.status_code, r.text)
except Exception as e:
    print('request error', e)
