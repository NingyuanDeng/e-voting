#!/usr/bin/env python
import sys
import os
import binascii
import math
import random
from Crypto.Cipher import AES


def rabin_miller(n):
    s = n - 1
    t = 0
    while s % 2 == 0:
        s = s // 2
        t += 1
    k = 0
    while k < 128:
        a = random.randrange(2, n - 1)
        v = pow(a, s, n)
        if v != 1:
            i = 0
            while v != (n - 1):
                if i >= t - 1:
                    return False
                else:
                    i = i + 1
                    v = (v ** 2) % n
        k += 2
    return True


def prime_candidate():
    flag = False
    while flag is False:
        tmp = int(binascii.hexlify(os.urandom(128)), 16)
        flag = rabin_miller(tmp)
    return tmp


def e_generate():
    """while True:
        e = random.randrange(2, _l - 1)
        if math.gcd(_l, e) == 1:
            return e"""
    e = 65537
    return e


def ex_euclid(a, b, _list):
    if b == 0:
        _list[0] = 1
        _list[1] = 0
        _list[2] = a
    else:
        ex_euclid(b, a % b, _list)
        temp = _list[0]
        _list[0] = _list[1]
        _list[1] = temp - a // b * _list[1]


def mod_inverse(a, b):  # a=l, b=e
    # ax+by=gcd
    _list = [0, 0, 0]
    if a < b:
        temp = a
        a = b
        b = temp
    ex_euclid(a, b, _list)
    if _list[1] < 0:
        _list[1] = a + _list[1]
    return _list[1]


def d_generate(_e, _l):
    return mod_inverse(_e, _l)


class MyRSA(object):
    def __init__(self):
        self.e = e_generate()
        while True:
            self.p = prime_candidate()
            self.q = prime_candidate()
            self.n = self.p * self.q
            self.l = (self.p - 1) * (self.q - 1) // math.gcd(self.p - 1, self.q - 1)
            if math.gcd(self.l, self.e) == 1:
                break
        self.d = d_generate(self.l, self.e)


def key_output(name, rsa):
    string = name + ".pub"
    fo = open(string, "w")
    fo.write(str(rsa.n))
    fo.write("\n")
    fo.write(str(rsa.e))
    fo.write("\n")
    fo.close()

    string = name + ".prv"
    fo = open(string, "w")
    fo.write(str(rsa.n))
    fo.write("\n")
    fo.write(str(rsa.d))
    fo.write("\n")
    fo.close()


if __name__ == '__main__':
    row_argv = sys.argv
    list_0 = row_argv
    list_0.pop(0)  # pop the path of input
    var = MyRSA()

    key_output(list_0[0], var)
    """print(var.n)
    print(var.e)
    print(var.d)
    print((var.e * var.d) % var.l)
    """
