#!/usr/bin/env python
import hashlib
import sys
import math


class TreeNode(object):
    def __init__(self, data=None, left=None, right=None, parent=None, count=-1):
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent
        self.count = count  # how many leaves node it include


class MerkleTree(object):
    def __init__(self):
        self.root = TreeNode()


def deal(row_data):
    list_deal = row_data
    list_deal[0] = list_deal[0].split("[")[1]
    list_deal[len(list_deal) - 1] = list_deal[len(list_deal) - 1].split("]")[0]
    for _ in range(0, len(list_deal)):
        list_deal[_] = list_deal[_].split(",")[0]
        # print(len(list_deal[_]), list_deal[_])
    return list_deal


def pair_hash(_list_node):
    num = len(_list_node)
    _new_list = list()
    _count = 0
    if num % 2 == 0:
        while _count < num:
            _tmp = TreeNode()
            _tmp.data = hashlib.sha256(
                (_list_node[_count].data.encode("latin1")) + (_list_node[_count + 1].data.encode("latin1"))).hexdigest()
            _tmp.left = _list_node[_count]
            _list_node[_count].parent = _tmp
            _tmp.right = _list_node[_count + 1]
            _list_node[_count + 1].parent = _tmp
            _count = _count + 2
            _new_list.append(_tmp)
    else:
        while _count < num - 2:
            _tmp = TreeNode()
            _tmp.data = hashlib.sha256(
                (_list_node[_count].data.encode("latin1")) + (_list_node[_count + 1].data.encode("latin1"))).hexdigest()
            _tmp.left = _list_node[_count]
            _list_node[_count].parent = _tmp
            _tmp.right = _list_node[_count + 1]
            _list_node[_count + 1].parent = _tmp
            _count = _count + 2
            _new_list.append(_tmp)
        _tmp = TreeNode()
        _tmp.data = _list_node[num - 1].data
        _tmp.left = _list_node[num - 1]
        _list_node[num - 1].parent = _tmp
        _new_list.append(_tmp)
    return _new_list


def tree_generate(_list_in):
    _n = len(_list_in)
    _list_leaves = list()
    _list_node = list()
    for _ in range(0, _n):
        tmp = TreeNode()
        tmp.data = hashlib.sha256(_list_in[_].encode("latin1")).hexdigest()
        _list_leaves.append(tmp)
        _list_node.append(tmp)

        # print(list_node[_].data)
    while len(_list_node) != 1:
        _list_node = pair_hash(_list_node)
    return _list_node[0], _list_leaves


def file_tree_write(_root_node, _mode):
    _list_node = list()
    _list_next = list()
    _list_node.append(_root_node)
    fo = open("merkle.trees", _mode)
    while len(_list_node) != 0:
        out_num = len(_list_node)
        for _ in range(0, out_num):
            fo.write(_list_node[_].data + " ")
            if _list_node[_].left is not None:
                _list_node.append(_list_node[_].left)
                if _list_node[_].right is not None:
                    _list_node.append(_list_node[_].right)
        for _ in range(0, out_num):
            _list_node.pop(0)
        fo.write("\n")
    fo.close()
    return


def file_normal_write(_data, _mode):
    fo = open("merkle.trees", _mode)
    fo.write(_data)
    fo.close()


def prove_path(_m, _n,  _list):
    _k = int(math.log(_n, 2))
    _k = 2 ** _k
    if _m == _k:
        _list.append(_m)
        return
    elif _m < _k:
        _list.append(_k)
        prove_path(_m, _k-1, _list)
    elif _m > _k:
        _list.append(_m)
        prove_path(_k, _m, _list)


if __name__ == '__main__':
    row_argv = sys.argv
    list_0 = row_argv
    list_0.pop(0)  # pop the path of input
    # print(list_0)

    divide_point = -1
    for _ in range(1, len(list_0)):
        if list_0[_][0] == '[':
            divide_point = _
            break

    list_1 = list_0[:divide_point]
    list_1 = deal(list_1)

    list_2 = list_0[divide_point:]
    list_2 = deal(list_2)

    l_root = list()
    tmp_node, leaves_A = tree_generate(list_1)
    l_root.append(tmp_node)
    n_1 = len(list_1)

    tmp_node, leaves_B = tree_generate(list_2)
    l_root.append(tmp_node)
    n_2 = len(list_2)

    file_tree_write(l_root[0], "w")
    file_normal_write("----------\n", "a")
    file_tree_write(l_root[1], "a")

    # print(list_1, list_2)

    list_divide = list()
    prove_path(n_1, n_2, list_divide)
    list_divide.append(0)
    if list_divide[0] == n_2:
        list_divide.reverse()
    else:
        list_divide.reverse()
        list_divide.append(n_2)
    list_prove = list()

    for _ in range(1, len(list_divide)):  # generate consistent proof
        back = math.ceil(math.log(list_divide[_] - list_divide[_-1], 2))
        tmp_node = leaves_B[list_divide[_] - 1]
        for _ in range(0, back):
            tmp_node = tmp_node.parent
        list_prove.append(tmp_node)

    list_check = list()
    for _ in range(1, len(list_divide)):  # used to verify the old tree
        if list_divide[_] <= n_1:
            back = math.ceil(math.log(list_divide[_] - list_divide[_ - 1], 2))
            tmp_node = leaves_A[list_divide[_] - 1]
            for _ in range(0, back):
                tmp_node = tmp_node.parent

            list_check.append(tmp_node)
        else:
            break

    # check old
    flag_subset = True
    flag_consistency = False

    for _ in range(0, len(list_check)):
        if list_check[_].data != list_prove[_].data:
            flag_subset = False
            break

    if flag_subset is True:
        # check consistency
        list_test_node = list_prove[:]
        list_test_data = list()
        for _ in range(0, len(list_test_node)):
            if list_test_node[_].parent is not None:
                if list_test_node[_].parent.right is None:
                    list_test_node[_] = list_test_node[_].parent
            list_test_data.append(list_test_node[_].data)

        while len(list_test_node) != 1:
            count = 0
            while count < len(list_test_node) - 1:
                if list_test_node[count].parent.right == list_test_node[count+1]:
                    tmp_hash = hashlib.sha256((list_test_data[count].encode("latin1")) + (list_test_data[count+1].encode("latin1"))).hexdigest()
                    list_test_node.insert(count, list_test_node[count].parent)
                    list_test_node.pop(count+2)
                    list_test_node.pop(count+1)

                    list_test_data.insert(count, tmp_hash)
                    list_test_data.pop(count + 2)
                    list_test_data.pop(count + 1)
                else:
                    count = count+1
        if list_test_data[0] == l_root[1].data:
            flag_consistency = True
        else:
            flag_consistency = False

    if flag_subset and flag_consistency is True:
        str_path = ""
        for _ in list_prove:
            str_path = str_path + _.data + ", "
        if list_prove[0].data != l_root[0].data:
            str_path = l_root[0].data + ", " + str_path

        str_path = str_path + l_root[1].data
        str_path = "[" + str_path + "]"
        print("yes", str_path)
    else:
        print("no")
