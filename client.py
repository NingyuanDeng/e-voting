import hashlib
import sys
import os
import math
import random
import base64
import basic_fun
import time
import genkeys

sys.setrecursionlimit(1000000)


def tds_msg(_msg, _method):
    _tdes = basic_fun.TripleDes()
    _tdes.method = _method
    _msg = _tdes.encrypt(_msg)
    _msg = base64.b64encode(_msg)
    return _msg


if __name__ == '__main__':
    row_argv = sys.argv
    list_0 = row_argv
    action = list_0[1]
    # 已经完成握手
    k_session, method = basic_fun.tls_handshake()
    basic_fun.file_write("k_session.txt", "wb", k_session)

    if action == "1":  # register
        pid = list_0[2]
        pwd = list_0[3]
        # output = base64.b64encode(bytes(action+"\n"+pid, "utf-8"))
        ps_hash = hashlib.sha256((pwd + pid).encode("latin1")).hexdigest()
        msg = bytes(action + "\n" + pid + "\n" + ps_hash, "utf-8")
        msg = tds_msg(msg, method)
        basic_fun.file_write("message_sec.txt", "wb", msg)

        if os.path.exists("register_state.txt"):
            os.remove("register_state.txt")
        time.sleep(10)
        print("registration " + basic_fun.file_read("register_state.txt", "r"))

    elif action == "2":  # vote # pwd correct, state is false-->able to vote
        pid = list_0[2]
        uid = list_0[3]  # via UID to hidden PID
        pwd = list_0[4]
        vote = list_0[5]
        ps_hash = hashlib.sha256((pwd + pid).encode("latin1")).hexdigest()  # PID won't be send
        msg = bytes(action + "\n" + uid + "\n" + ps_hash + "\n" + vote, "utf-8")
        msg = tds_msg(msg, method)
        basic_fun.file_write("message_sec.txt", "wb", msg)
        if os.path.exists("login_state.txt"):
            os.remove("login_state.txt")
        time.sleep(10)
        print("login " + basic_fun.file_read("login_state.txt", "r"))

        msg_2 = bytes(uid + "\n" + vote, "utf-8")
        rsa_str = basic_fun.file_read("rsa_for_blind.pub", "r")
        list_line = rsa_str.split("\n")
        rsa_n = int(list_line[0])
        rsa_e = int(list_line[1])
        while 1:
            r = random.randrange(2, rsa_n - 1)
            if math.gcd(rsa_n, r) == 1:
                inverse_r = genkeys. d_generate(r, rsa_n)
                break

        blind_m = int.from_bytes(msg_2, 'little') * pow(r, rsa_e, rsa_n)
        blind_m = blind_m.to_bytes((blind_m.bit_length() + 7) // 8, 'little')
        blind_m = tds_msg(blind_m, method)
        if os.path.exists("blind_msg_client.txt"):
            os.remove("blind_msg_client.txt")
        basic_fun.file_write("blind_msg_client.txt", "wb", blind_m)
        time.sleep(10)

        b_sig = basic_fun.file_read("blind_msg_server.txt", "rb")
        b_sig = base64.b64decode(b_sig)

        tdes = basic_fun.TripleDes()
        tdes.method = method
        b_sig = tdes.decrypt(b_sig)
        b_sig = int.from_bytes(b_sig, 'little')
        sig = (b_sig * inverse_r) % rsa_n  # signature of vote

        rsa_str = basic_fun.file_read("rsa_for_blind.prv", "r")
        list_line = rsa_str.split("\n")
        rsa_n = int(list_line[0])
        rsa_d = int(list_line[1])

        if sig == pow(int.from_bytes(msg_2, 'little'), rsa_d, rsa_n):
            print("yes")

        tmp = uid+"-receipt.txt"
        tid = uid
        basic_fun.file_write(tmp, "w", tid + "\n" + str(sig))
        # if want to sure, send your msg and sig to server

    elif action == "3":  # query
        pid = list_0[2]
        uid = list_0[3]  # via UID to hidden PID
        tid = uid  # just assume
        pwd = list_0[4]
        vote = list_0[5]
        basic_fun.file_read("rsa_for_blind.prv", "r")
        ps_hash = hashlib.sha256((pwd + pid).encode("latin1")).hexdigest()  # PID won't be send
        msg = bytes(action + "\n" + uid + "\n" + ps_hash + "\n" + vote, "utf-8")
        msg = tds_msg(msg, method)
        basic_fun.file_write("message_sec.txt", "wb", msg)

        """msg_2 = bytes()
        msg_2 = tds_msg(msg_2, method)
        basic_fun.file_write("signature.txt", "wb", msg)"""

        print()