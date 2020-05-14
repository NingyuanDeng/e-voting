#!/usr/bin/env python
import hashlib
import sys


class TreeNode(object):
    def __init__(self, data=None, left=None, right=None, parent=None, state=None):
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent
        self.state = state # left node or right


class MerkleTree(object):
    def __init__(self):
        self.root = TreeNode()


if __name__ == '__main__':
    row_argv = sys.argv
    check_data = row_argv[1]
    # print(check_data)
    check_hash = hashlib.sha256(check_data.encode("latin1")).hexdigest()

    fo = open("merkle.tree", "r")
    _str = fo.read()
    # print(_str)
    fo.close()

    list_line = _str.split(" \n")
    layer_num = len(list_line) - 1

    MT = MerkleTree()
    MT.root.data = list_line[0]
    list_node = list()
    list_node.append(MT.root)
    for _ in range(1, layer_num):  # to build Merkle tree
        list_hash_layer = list_line[_].split(" ")
        limit = len(list_hash_layer)
        list_next_layer_node = list()
        count = 0
        for node in list_node:
            node.left = TreeNode()
            node.left.data = list_hash_layer[count]
            node.left.parent = node
            node.left.state = "left"
            list_next_layer_node.append(node.left)
            count = count + 1
            if count < limit:
                node.right = TreeNode()
                node.right.data = list_hash_layer[count]
                node.right.parent = node
                node.right.state = "right"
                list_next_layer_node.append(node.right)
                count = count + 1
        list_node = list_next_layer_node

    list_leaf = list_node  # after cycle, it includes all leaf nodes
    list_prove = list()
    list_prove_state = list()
    for _ in range(0, len(list_leaf)):
        if check_hash == list_leaf[_].data:
            node = list_leaf[_]
            while node != MT.root:
                if node.state == "left":
                    if node.parent.right is not None:
                        list_prove.append(node.parent.right.data)
                        list_prove_state.append("left")
                    else:
                        list_prove.append(node.parent.left.data)
                        list_prove_state.append("self")
                elif node.state == "right":
                    list_prove.append(node.parent.left.data)
                    list_prove_state.append("right")

                node = node.parent
            list_prove.append(node.data)  # now, it's root
            break

    output_str = "no"
    for _ in range(0, len(list_prove)-1):
        if list_prove_state[_] == "left":
            check_hash = hashlib.sha256(check_hash.encode("latin1")+list_prove[_].encode("latin1")).hexdigest()
        elif list_prove_state[_] == "right":
            check_hash = hashlib.sha256(list_prove[_].encode("latin1")+check_hash.encode("latin1")).hexdigest()
        if list_prove_state[_] == "self":
            # check_hash = hashlib.sha256(check_hash.encode("latin1")).hexdigest()
            check_hash = check_hash

    if check_hash == MT.root.data:
        output_str = "yes ["
        for _ in range(0, len(list_prove)-1):
            if list_prove_state[_] != "self":
                output_str = output_str + list_prove[_] + ", "
        output_str = output_str + list_prove[len(list_prove)-1] + "]"
    print(output_str)
