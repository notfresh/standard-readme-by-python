#! /usr/local/bin/python3
#coding=utf-8

import sys, os

# file_path = ''
# file_path = sys.argv[1]
#
import sys, os


def check_file_path(file_path):
    cwd = os.getcwd()
    if os.path.exists(file_path):
        file_path = file_path
    elif os.path.exists(os.path.join(cwd, file_path)):
        file_path = os.path.join(cwd, file_path)
    else:
        print("md file not exist")
        sys.exit(1)


def is_alpha(c):
    return ord(c) >= 65 and ord(c) < 97 + 26

def is_ascii(c):
    """
    判断一个字符是不是 ascii 码,比如 asci('a') =  "'a'"
    :param c:
    :return:
    """
    return ascii(c)[1:-1] == c

def is_space(c):
    return c == ' '



def update(str1):
    i = 0
    lens = len(str1)
    letters = []
    while i < lens:
        if is_ascii(str1[i]) and not is_space(str1[i]): # $2
            tmp = [i]
            i += 1
            while i < lens and is_ascii(str1[i]) and not is_space(str1[i]):
                i += 1
            tmp.append(i)
            letters.append(tmp) # $+7
        i += 1 # $+8
    # print(letters)
    ls1 = list(str1) # str1 = '和py啊a'
    space_pos = []
    for item in letters:
        if(item[0] > 0 and not is_space( str1[item[0]-1] )):
            space_pos.append(item[0])
        if (item[1] < lens and not is_space(str1[item[1]])):
            space_pos.append(item[1])
    i = 0
    # print(space_pos)
    while i < len(space_pos):
        space_pos[i] += i
        i += 1
    # print(space_pos)
    for ind in space_pos:
        ls1.insert(ind, ' ')
    ret = ''.join(ls1)
    return ret

def update_space(file_path):
    check_file_path(file_path)
    with open(file_path,encoding='utf-8') as f:
        lines = f.readlines()
    # str1 = '了解python的re 模块,你说呢?'
    lines = [update(line) for line in lines]
    with open(file_path, encoding='utf-8' ,mode='w+') as f:
        f.writelines(lines)
    print('file url update success')



