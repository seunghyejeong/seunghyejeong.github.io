import json
import requests

class ObjectService:
    def __init__(self, storage_url, token_id):
        self.storage_url = storage_url
        self.token_id = token_id

    def _get_url(self, container, object):
        return '/'.join([self.storage_url, container, object])

    def _get_request_header(self):
        return {'X-Auth-Token': self.token_id}

    def upload(self, container, object, object_path):
        req_url = self._get_url(container, object)
        req_header = self._get_request_header()

        path = '/'.join([object_path, object])
        with open(path, 'rb') as f:
            return requests.put(req_url, headers=req_header, data=f.read())

def get_token(auth_url, tenant_id, username, password):
    token_url = auth_url + '/tokens'
    req_header = {'Content-Type': 'application/json'}
    req_body = {
        'auth': {
            'tenantId': tenant_id,
            'passwordCredentials': {
                'username': username,
                'password': password
            }
        }
    }

    response = requests.post(token_url, headers=req_header, json=req_body)
    return response.json()


if __name__ == '__main__':
    AUTH_URL = 'https://api-identity-infrastructure.nhncloudservice.com/v2.0'
    TENANT_ID = '9ea3a098cb8e49468ac2332533065184'
    USERNAME = 'minkyu.lee'
    PASSWORD = 'PaaS-TA@2024!'

    token = get_token(AUTH_URL, TENANT_ID, USERNAME, PASSWORD)
    token_value=(token["access"]["token"]["id"])
    print(type(token_value))
    
    

  #  jsondata = json.dumps(token, indent=2),
   
 #   print(jsondata)
    
    

    # print(tokenGetFromJson)
    
