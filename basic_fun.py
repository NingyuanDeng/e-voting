
import os
import pyDes
import base64
import hmac


def tls_handshake():  # only generate session key for 3DES
    _k_session = os.urandom(24)
    _method = pyDes.triple_des(_k_session, pyDes.CBC, IV=None, pad=None, padmode=pyDes.PAD_PKCS5)
    return _k_session, _method


def tls_handshake_2(_k_session):
    _method = pyDes.triple_des(_k_session, pyDes.CBC, IV=None, pad=None, padmode=pyDes.PAD_PKCS5)
    return _method


class TripleDes(object):
    def __init__(self, method=None):
        self.method = method

    def encrypt(self, pt):
        ct = self.method.encrypt(pt)
        ct = base64.b64encode(ct)
        return ct

    def decrypt(self, ct):
        pt = base64.b64decode(ct)
        pt = self.method.decrypt(pt)
        return pt


def file_read(_name, _mode):
    fo = open(_name, _mode)
    _str = fo.read()
    # print(_str)
    fo.close()
    return _str


def file_write(_name, _mode, _data):
    fo = open(_name, _mode)
    fo.write(_data)
    fo.close()


def challenge_response(_epass, _msg):
    _key = _epass
    h = hmac.new(_key, _msg, digestmod='MD5')

