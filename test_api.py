import urllib.request
import json
import urllib.error

req = urllib.request.Request(
    'http://127.0.0.1:5000/login',
    method='POST',
    data=json.dumps({'email': 'leafcare@example.com', 'password': 'leaf123'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    res = urllib.request.urlopen(req)
    print("SUCCESS:", res.read().decode())
except urllib.error.HTTPError as e:
    print(f"FAILED (HTTP {e.code}):", e.read().decode())
except Exception as e:
    print("ERROR:", str(e))
