#!/usr/bin/env python
import hashlib
import sys


class TreeNode(object):
    def __init__(self, data=None, left=None, right=None, parent=None):
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent


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
            _tmp.data = hashlib.sha256((_list_node[_count].data.encode("latin1"))+(_list_node[_count+1].data.encode("latin1"))).hexdigest()
            _tmp.left = _list_node[_count]
            _list_node[_count].parent = _tmp
            _tmp.right = _list_node[_count+1]
            _list_node[_count+1].parent = _tmp
            _count = _count+2
            _new_list.append(_tmp)
    else:
        while _count < num-2:
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
        _tmp.data = _list_node[num-1].data
        _tmp.left = _list_node[num-1]
        _list_node[num-1].parent = _tmp
        _new_list.append(_tmp)
    return _new_list


if __name__ == '__main__':
    row_argv = sys.argv
    list_0 = row_argv
    list_0.pop(0)  # pop the path of input
    list_1 = deal(list_0)
    n = len(list_1)

    list_node = list()
    for _ in range(0, n):
        tmp = TreeNode()
        tmp.data = hashlib.sha256(list_1[_].encode("latin1")).hexdigest()
        list_node.append(tmp)

        # print(list_node[_].data)
    while len(list_node) != 1:
        list_node = pair_hash(list_node)

    MTree = MerkleTree()
    MTree = list_node[0]
    # print(MTree.data)
#    for _ in range(0, len(list_node)):
#        print(list_node[_].data)

    list_node = list()
    list_next = list()
    list_node.append(MTree)
    fo = open("merkle.tree", "w")
    while len(list_node) != 0:
        out_num = len(list_node)
        for _ in range(0, out_num):
            fo.write(list_node[_].data+" ")
            if list_node[_].left is not None:
                list_node.append(list_node[_].left)
                if list_node[_].right is not None:
                    list_node.append(list_node[_].right)
        for _ in range(0, out_num):
            list_node.pop(0)
        fo.write("\n")
    fo.close()
