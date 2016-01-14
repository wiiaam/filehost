#!/usr/bin/env python3.3

import sys
import hashlib

def addPass(password):
    with open("auths") as f:
        passwords = [x.strip('\n') for x in f.readlines()]
    hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    if passwords.__contains__(hash) is False:
        with open("auths","a") as f:
            f.write(hash + "\n")
    print("Password added")

if len(sys.argv) > 1:
    if sys.argv[1] == "--addpass":
        if len(sys.argv) > 2:
            addPass(sys.argv[2])
        else:
           print("Please specify a password")

def chechPass(password):
    with open("auths") as f:
        passwords = [x.strip('\n') for x in f.readlines()]
    hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return passwords.__contains__(hash)
