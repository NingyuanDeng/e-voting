#!/usr/bin/env python
import sys
import os
import binascii
from Crypto.Cipher import AES
import basic_fun


class MyRSA(object):
    def __init__(self):
        self.p = -1
        self.q = -1
        self.n = -1
        self.l = -1
        self.e = -1
        self.d = -1


def aes_key():
    _key = os.urandom(16)
    _iv = binascii.hexlify(os.urandom(8))
    return _key, _iv


def add_to_16(text):
    if len(text.encode('utf-8')) % 16:
        add = 16 - (len(text.encode('utf-8')) % 16)
    else:
        add = 0
    text = text + ('\0' * add)
    return text.encode('utf-8')


def encrypt(_key, _iv, _mode, _plain):
    _plain = add_to_16(_plain)
    _crypto = AES.new(_key, _mode, _iv)
    _cipher_text = _crypto.encrypt(_plain)
    _cipher_text = binascii.hexlify(_cipher_text)

    return _cipher_text


def decrypt(_key, _iv, _mode, _cipher):
    _crypto = AES.new(_key, _mode, _iv)
    _plain_text = _crypto.decrypt(binascii.unhexlify(_cipher))
    _plain_text = bytes.decode(_plain_text).rstrip('\0')
    return _plain_text


def file_read(_name):
    fo = open(_name, "r", encoding='utf-8')
    _str = fo.read()
    # print(_str)
    fo.close()
    return _str


def file_write(_name, _data):
    fo = open(_name, "w")
    fo.write(_data)
    fo.close()


if __name__ == '__main__':
    row_argv = sys.argv
    list_0 = row_argv
    # list_0.pop(0)  # pop the path of input

    mode = list_0[1]   # -e or -d
    if mode == "-e":
        aes_key = aes_key()
        aes_mode = AES.MODE_CBC

        rsa_str = file_read(list_0[2])
        list_line = rsa_str.split("\n")
        rsa_n = int(list_line[0])
        rsa_e = int(list_line[1])
        # x = random.randrange(2, rsa_n)
        x_byte = os.urandom(24)
        x = int(binascii.hexlify(x_byte), 16)
        y = pow(x, rsa_e, rsa_n)
        tdes_method = basic_fun.tls_handshake_2(x_byte)
        tdes = basic_fun.TripleDes()
        tdes.method = tdes_method
        ea_key = tdes.encrypt(aes_key[0])
        ea_iv = tdes.encrypt(aes_key[1])
        #ea_key = pow(int.from_bytes(aes_key[0], 'little'), rsa_e, rsa_n)  # encrypted aes key
        #ea_iv = pow(int.from_bytes(aes_key[1], 'little'), rsa_e, rsa_n)  # encrypted iv
        msg_plain = file_read(list_0[3])

        t = encrypt(aes_key[0], aes_key[1], aes_mode, msg_plain)
        t = t.decode('utf-8')
        t = t + '\n' + ea_key.decode() + '\n' + ea_iv.decode() + '\n' + str(y)
        file_write(list_0[4], t)

    elif mode == "-d":
        aes_mode = AES.MODE_CBC

        rsa_str = file_read(list_0[2])
        list_line = rsa_str.split("\n")
        rsa_n = int(list_line[0])
        rsa_d = int(list_line[1])

        list_line = file_read(list_0[3]).split("\n")
        msg_cipher = list_line[0]
        ea_key = list_line[1].encode()
        ea_iv = list_line[2].encode()
        y = int(list_line[3])
        x = pow(y, rsa_d, rsa_n)
        x_byte = x.to_bytes((x.bit_length() + 7) // 8, 'big')
        tdes_method = basic_fun.tls_handshake_2(x_byte)
        tdes = basic_fun.TripleDes()
        tdes.method = tdes_method
        aes_key = [0, 0]
        aes_key[0] = tdes.decrypt(ea_key)
        aes_key[1] = tdes.decrypt(ea_iv)

        msg_plain = decrypt(aes_key[0], aes_key[1], aes_mode, msg_cipher)

        file_write(list_0[4], msg_plain)
        #print(msg_plain)

    #print(list_0)
    #print(t)