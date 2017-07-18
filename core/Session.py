import json
import zlib
import base64
from AESCipher import AESCipher
import config

class Session:
    DEFAULT = {
        'v': 1
    }

    def __init__(self, encoded_str = ''):
        if encoded_str:
            cipher = AESCipher(config.SESSION_SECRET_KEY)
            compressed_arr = cipher.decrypt(encoded_str)
            byte_arr = zlib.decompress(compressed_arr)
            json_str = byte_arr.decode('utf-8')
            dic = json.loads(json_str)
        else:
            dic = Session.DEFAULT
        for k, v in dic.items():
            self.__dict__[k] = v

    def delete(self, key):
        del self.__dict__[key]

    def encode(self):
        global SESSION_SECRET_KEY
        cipher = AESCipher(config.SESSION_SECRET_KEY)
        json_str = json.dumps(self.__dict__)
        byte_arr = json_str.encode('utf-8')
        compressed_arr = zlib.compress(byte_arr)
        base64_str = cipher.encrypt(compressed_arr)
        return base64_str
