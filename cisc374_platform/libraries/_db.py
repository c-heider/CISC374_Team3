import urllib2, urllib
_api = ''
import fix_json
import json

def query(action, data = ''):
    data = urllib.urlencode({'data' : json.dumps(data)})
    r = urllib2.urlopen(_api + action, data)
    r = r.read()
    r = json.loads(r)
    return r
    
def set_api_endpoint(url):
    global _api
    _api = url
    if _api[-1] != '/':
        _api = + _api + '/'