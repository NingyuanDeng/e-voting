#!/usr/bin/python3

import basic_fun
import os

counter = 0
dir = os.getcwd()
list_cip = []
for root, dirs, files in os.walk(dir):
    for file in files:
        (filename, extension) = os.path.splitext(file)
        if extension == '.cip':
            counter = counter + 1
            list_cip.append(file)

data_cip = []

for i in list_cip:
    data_cip.append(basic_fun.file_read(i, "r"))

sys_order = "python ./buildmtree.py ["
for i in data_cip:
    tmp = i.split("\n")  # i=cipher+ea_key+ea_iv+y
    sys_order = sys_order+tmp[0]+", "
sys_order = sys_order[:-2]
sys_order = sys_order+"]"
p = os.system(sys_order)

