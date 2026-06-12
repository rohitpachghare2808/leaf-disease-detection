import urllib.request
import urllib.parse
import json

try:
    # 1. Login
    login_data = json.dumps({"email": "leafcare@example.com", "password": "leaf123"}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:5000/login', data=login_data, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    # get cookie
    cookie = res.headers.get('Set-Cookie')

    # 2. Upload dummy image
    image_bytes = (
        b'\xff\xd8\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12'
        b'\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08'
        b'\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\x37\xff\xd9'
    )
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="test.jpg"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'
    ).encode('utf-8') + image_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    req2 = urllib.request.Request('http://127.0.0.1:5000/predict', data=body)
    req2.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req2.add_header('Cookie', cookie)

    res2 = urllib.request.urlopen(req2)
    print(res2.status)
    print(res2.read().decode('utf-8'))

except Exception as e:
    import traceback
    traceback.print_exc()
