# object.py
import os
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


if __name__ == '__main__':
    STORAGE_URL = 'https://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_9ea3a098cb8e49468ac2332533065184'
    TOKEN_ID = 'gAAAAABl751bvzYtIVNp-JkDmj2XvF1QLGzSJ08kXAdMgqnMoHEm8hAlqrUieTYqMJcsjpMVGUF91rSeqGo7-VyjDnDBqwzlMwOLzXynIT0xYmAPeyHNA6eKhuZDi7QxEqutYjGA5ddjbSonaQmg3ZTk7YwitvoWyMIc8hItJgZXY2kdRF2HyZs'
    CONTAINER_NAME = 'cp-object-storage'
    OBJECT_NAME = 'index.html'
    OBJECT_PATH = r'C:\Users\USER\airflow'
    
    obj_service = ObjectService(STORAGE_URL, TOKEN_ID)

    obj_service.upload(CONTAINER_NAME, OBJECT_NAME, OBJECT_PATH)