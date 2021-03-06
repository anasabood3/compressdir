'''Compress and decompress files and directories.

Example:
    >>> from compressdir import compress
    >>> path = "/path/to/file/or/dir"
    >>> compress(path)
    >>> decompress(path + ".compressed")
'''

import os
import bz2
import pickle

def splitPath(path):
    pathsplit = []
    while True:
        path, part = os.path.split(path)
        if part != "":
            pathsplit.append(part)
        else:
            if path != "":
                pathsplit.append(path)
            pathsplit.reverse()
            return pathsplit

def dirToDict(path):
    pathlist = []
    for root, dirs, files in os.walk(path):
        for d in dirs:
            pathlist.append(os.path.join(root, d))
        for f in files:
            pathlist.append(os.path.join(root, f))
    tree = {}
    for thepath in pathlist:
        p = tree
        parts = splitPath(thepath)
        for part in parts:
            p = p.setdefault(part, {})
    for _ in range(len(splitPath(path)) - 1):
        tree = tree[list(tree.keys())[0]]
    return tree

def fileData(path, tree):
    for key in list(tree.keys()):
        if os.path.isdir(os.path.join(path, key)):
            tree[key] = fileData(os.path.join(path, key), tree[key])
        else:
            try:
                with open(os.path.join(path, key), "r") as f:
                    tree[key] = f.read()
            except:
                with open(os.path.join(path, key), "rb") as f:
                    tree[key] = f.read()
    return tree

def dictToDir(path, tree):
    for key in list(tree.keys()):
        if type(tree[key]) is type(str()):
            with open(os.path.join(path, key), "w") as f:
                f.write(tree[key])
        elif type(tree[key]) is type(bytes()):
            with open(os.path.join(path, key), "wb") as f:
                f.write(tree[key])
        elif type(tree[key]) is type(dict()):
            if not os.path.exists(os.path.join(path, key)):
                os.mkdir(os.path.join(path, key))
            dictToDir(os.path.join(path, key), tree[key])

def compressed(path, maximumCompression=False):
    '''Compress a file or directory.'''
    if os.path.isdir(path):
        tree = dirToDict(path)
        data = {list(tree.keys())[0]: fileData(path, list(tree.values())[0])}
    else:
        try:
            with open(path, "r") as f:
                data = {os.path.split(path)[1]: f.read()}
        except:
            with open(path, "rb") as f:
                data = {os.path.split(path)[1]: f.read()}
    pickled = pickle.dumps(data)
    if maximumCompression:
        data = bz2.compress(pickled)
        for i in range(1, 10):
            newdata = bz2.compress(pickled, compresslevel=i)
            if len(newdata) < len(data):
                data = newdata
    else:
        data = bz2.compress(pickled, compresslevel=9)
    return data

def compress(path, newpath=None, maximumCompression=False, ext=".compressed", deleteOld=False):
    '''Compress a file or directory and write it to a file.'''
    data = compressed(path, maximumCompression=maximumCompression)
    if newpath is None:
        newpath = os.path.join(os.path.split(path)[0], os.path.splitext(os.path.split(path)[1])[0] + ext)
    open(newpath, "wb").close()
    with open(newpath, "wb") as f:
        f.write(data)
    if deleteOld:
        os.remove(path)
    return newpath

def decompressed(data, newpath=None):
    '''Decompress a byte string compression of a file or directory.'''
    if newpath is None:
        newpath = os.getcwd()
    data = bz2.decompress(data)
    data = pickle.loads(data)
    dictToDir(newpath, data)
    return list(data.keys())[0]

def decompress(path, newpath=None, deleteOld=False):
    '''Decompress a compressed file or directory.'''
    if newpath is None:
        newpath = os.path.split(path)[0]
    with open(path, "rb") as f:
        data = f.read()
    newpath = decompressed(data, newpath)
    if deleteOld:
        os.remove(path)
    return newpath
