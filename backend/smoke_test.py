import json, urllib.request, urllib.error
base='http://127.0.0.1:5000'

def post(path,data,headers=None):
    url=base+path
    hdrs={'Content-Type':'application/json'}
    if headers:
        hdrs.update(headers)
    req=urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=hdrs)
    try:
        resp=urllib.request.urlopen(req, timeout=5)
        print(path, resp.getcode())
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(path, 'HTTP', e.code, e.read().decode())
        return None
    except Exception as e:
        print(path, 'ERR', e)
        return None

# Signup
post('/auth/signup', {'email':'test@example.com','password':'pass123'})
# Login
login=post('/auth/login', {'email':'test@example.com','password':'pass123'})
if not login or 'access_token' not in login:
    print('Login failed', login)
else:
    token=login['access_token']
    hdr={'Authorization':f'Bearer {token}'}
    create=post('/sops/', {'title':'Test SOP','content':'This is a test SOP content','department_id':None}, headers=hdr)
    try:
        req=urllib.request.Request(base+'/sops/', headers=hdr)
        resp=urllib.request.urlopen(req, timeout=5)
        print('/sops/ GET', resp.getcode(), resp.read().decode())
    except Exception as e:
        print('List sops failed', e)
    q=post('/questions/', {'sop_id':1,'question':'What is this SOP about?'}, headers=hdr)
    print('question', q)
