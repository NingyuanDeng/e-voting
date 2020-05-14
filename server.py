import hashlib
import sys
import os
import binascii
import base64
import basic_fun
import pymysql
import time


def tds_msg(_msg, _method):
    _tdes = basic_fun.TripleDes()
    _tdes.method = _method
    _msg = _tdes.encrypt(_msg)
    _msg = base64.b64encode(_msg)
    return _msg


def init_db():
    db = pymysql.connect("localhost", "root", "root", "new_schema")
    cursor = db.cursor()
    sql = """CREATE TABLE IF NOT EXISTS `new_schema`.`status` (
  `PID` VARCHAR(45) NOT NULL,
  `UID` VARCHAR(45) NOT NULL,
  `state` VARCHAR(45) NULL,
  `salt` VARCHAR(45) NULL,
  `server_hash` VARCHAR(100) NULL,
  UNIQUE INDEX `PID_UNIQUE` (`PID` ASC) VISIBLE,
  UNIQUE INDEX `UID_UNIQUE` (`UID` ASC) VISIBLE,
  PRIMARY KEY (`UID`));"""
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()
    return


def pid_authenticate(_pid):
    state = -1
    state = 1
    return state


if __name__ == '__main__':
    row_argv = sys.argv
    list_0 = row_argv
    mode = list_0[1]
    if mode == "mtree_build":
        sys_order = "python ./data_collection.py"
        p = os.system(sys_order)
    elif mode == "server":
        db = pymysql.connect("localhost", "root", "root", "new_schema")
        cursor = db.cursor()
        init_db()

        k_session = basic_fun.file_read("k_session.txt", "rb")
        tdes = basic_fun.TripleDes()
        tdes.method = basic_fun.tls_handshake_2(k_session)

        msg = basic_fun.file_read("message_sec.txt", "rb")
        msg = base64.b64decode(msg)
        msg = tdes.decrypt(msg)
        list_msg = str(msg, "utf-8").split("\n")
        action = list_msg[0]
        if action == "1":  # register
            pid = list_msg[1]
            pwd_hash = list_msg[2]
            allow = pid_authenticate(pid)
            if allow == 1:
                sql = "select * from status where PID = \"%s\"" % pid
                cursor.execute(sql)
                result = cursor.fetchall()
                if result.__len__() == 0:  # when not exist
                    sql = "select count(*) from status"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    uid = str(result[0][0])
                    salt = str(binascii.hexlify(os.urandom(8)), "utf-8")
                    server_hash = hashlib.sha256((pwd_hash + salt).encode("latin1")).hexdigest()
                    sql = "insert into status (PID, UID, state, salt, server_hash) values (\"%s\", \"%s\", \"%s\", " \
                          "\"%s\", \"%s\");" % (pid, uid, "false", salt, server_hash)
                    cursor.execute(sql)
                    db.commit()

                    basic_fun.file_write("register_state.txt", "w", "success")
                else:#exist
                    basic_fun.file_write("register_state.txt", "w", "fail")
        # after registration, remove PID row in db to hidden the relationship between PID and UID
        # can keep all removed PID in a new table, to decide  whether someone has registered or not
        elif action == "2":  # vote
            uid = list_msg[1]  # via UID to hidden PID
            pwd_hash = list_msg[2]
            vote = list_msg[3]  # here, vote is sent to vote server
            sql = "select * from status where UID = \"%s\"" % uid
            cursor.execute(sql)
            result = cursor.fetchall()
            if result.__len__() != 0:  # when exist
                salt = result[0][3]
                server_hash = result[0][4]
                state = result[0][2]
                new_hash = hashlib.sha256((pwd_hash + salt).encode("latin1")).hexdigest()
                if server_hash == new_hash:  # pwd correct
                    if state == "true":
                        basic_fun.file_write("login_state.txt", "w", "login success, no repeat vote")
                    else:
                        basic_fun.file_write("login_state.txt", "w", "login success, can vote")

                        time.sleep(10)
                        # blind signature is achieved by third part indeed, not vote server
                        rsa_str = basic_fun.file_read("rsa_for_blind.prv", "r")
                        list_line = rsa_str.split("\n")
                        rsa_n = int(list_line[0])
                        rsa_d = int(list_line[1])

                        b_msg = basic_fun.file_read("blind_msg_client.txt", "rb")
                        b_msg = base64.b64decode(b_msg)
                        b_msg = tdes.decrypt(b_msg)
                        b_msg = int.from_bytes(b_msg, 'little')
                        blind_signature = pow(b_msg, rsa_d, rsa_n)
                        blind_signature = blind_signature.to_bytes((blind_signature.bit_length() + 7) // 8, 'little')
                        blind_signature = tds_msg(blind_signature, tdes.method)
                        if os.path.exists("blind_msg_server.txt"):
                            os.remove("blind_msg_server.txt")
                        basic_fun.file_write("blind_msg_server.txt", "wb", blind_signature)
                        time.sleep(10)  # wait for real signature

                        # UID associate with vote
                        transaction_ID = str(uid)  # indeed, will achieve by a counter or statistics
                        # to mark leaf node， TID is part of client receipt
                        sig = basic_fun.file_read(str(uid)+"-receipt.txt", "r").split("\n")[1]
                        msg_tmp = bytes(transaction_ID + "\n" + sig, "utf-8")
                        basic_fun.file_write(transaction_ID+".txt", "wb", msg_tmp)

                        sys_order = "python ./crypt.py -e rsa_for_aes.pub "+transaction_ID+".txt "+transaction_ID+".cip"
                        p = os.system(sys_order)

                        """sys_order = "python ./crypt.py -d rsa_for_aes.prv "+transaction_ID+".cip "+transaction_ID+"secret.txt"
                        p = os.system(sys_order)"""

                        state = "true"
                else:
                    basic_fun.file_write("login_state.txt", "w", "login fail")

        elif action == "3":  # query
            uid = list_msg[1]  # via UID to hidden PID
            pwd_hash = list_msg[2]
            vote = list_msg[3]  # here, vote is sent to vote server
            sql = "select * from status where UID = \"%s\"" % uid
            cursor.execute(sql)
            result = cursor.fetchall()
            if result.__len__() != 0:  # when exist
                salt = result[0][3]
                server_hash = result[0][4]
                state = result[0][2]
                new_hash = hashlib.sha256((pwd_hash + salt).encode("latin1")).hexdigest()
                if server_hash == new_hash:  # pwd correct
                    tmp = uid+"-receipt.txt"
                    [tid, sig] = basic_fun.file_read(tmp, "r").split("\n")
                    rsa_str = basic_fun.file_read("rsa_for_blind.prv", "r")
                    list_line = rsa_str.split("\n")
                    rsa_n = int(list_line[0])
                    rsa_d = int(list_line[1])

                    test_msg = bytes(uid + "\n" + vote, "utf-8")
                    test_msg = int.from_bytes(test_msg, 'little')
                    test_signature = pow(test_msg, rsa_d, rsa_n)
                    if str(test_signature == sig):
                        query = tid + "\n" + sig
                        query_byte = bytes(query, "utf-8")

                        sys_order = "python ./crypt.py -d rsa_for_aes.prv "+tid+".cip "+tid+"_test.txt"
                        p = os.system(sys_order)
                        tmp = basic_fun.file_read(tid+"_test.txt", "r")
                        if query == tmp:  # exist
                            q_2 = basic_fun.file_read(tid+".cip", "r")
                            sys_order = "python ./checkinclusion.py "+q_2
                            p = os.system(sys_order)
                    print()

