#!/usr/bin/env python
# encoding: utf-8

import hashlib

def get_sign(sign_type, data, private_key):
         return sign(data, private_key)



# 签名方式
def sign(data, private_key=''):
    keys = sorted(data.keys())
    temp = ''
    for key in keys:
        temp += data[key]
    md5 = hashlib.md5()
    temp += private_key
    md5.update(temp.encode(encoding='utf-8'))
    signature = md5.hexdigest()
    data['sign'] = signature
    return data
