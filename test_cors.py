import urllib.request
try:
    req = urllib.request.Request(
        'http://127.0.0.1:5000/login',
        method='OPTIONS',
        headers={'Origin': 'null', 'Access-Control-Request-Method': 'POST'}
    )
    res = urllib.request.urlopen(req)
    print("HEADERS:")
    for k, v in res.headers.items():
        print(f"{k}: {v}")
except Exception as e:
    print("ERROR:", e)
