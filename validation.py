# -*- coding: utf-8 -*-
# ======================================
# @File    : validation.py
# @Time    : 2019/12/5 22:41
# @Author  : Rivarrl
# ======================================
import pickle
import os

# 验证程序

class DoubleArea:
    def __init__(self, x, y, l):
        self.x = x
        self.y = y
        self.l = l

    def include(self, other):
        if self.l <= other.l or self.x > other.x or self.y < other.y: return False
        distance = self.l - other.l
        return other.x - self.x < distance and other.y - self.y < distance

pk_dir_name = 'pickle'
pk_dir = './' + pk_dir_name
# 写入pickle
if not os.path.exists(pk_dir): os.mkdir(pk_dir_name)

for fn in range(2, 14):
    if os.path.exists(pk_dir + '/{}.pkl'.format(fn)): continue
    pk = set()
    with open('./result/{}.txt'.format(fn), 'r', encoding='utf-8') as f:
        line = f.readline().strip()
        while line:
            stline = [e.strip() for e in line.split(' ') if e.strip()]
            p_start, q_start = map(int, stline)
            pk.add(DoubleArea(p_start, q_start, fn))
            line = f.readline().strip()
    with open(pk_dir + '/{}.pkl'.format(fn), 'wb') as f:
        pickle.dump(pk, f)
print('写入完成')

# 读取pickle
pk = {i: list() for i in range(2, 14)}
for fn in range(2, 14):
    with open(pk_dir + '/{}.pkl'.format(fn), 'rb') as f:
        pk[fn] = pickle.load(f)

print('读取完成')

# 验证
from collections import defaultdict
error_dict = defaultdict(set)
for fn in range(2, 13):
    for ofn in range(fn + 1, 14):
        for other in pk[ofn]:
            for da in pk[fn]:
                if other.include(da):
                    # print('找到')
                    error_dict[other].add(da)
    pk.pop(fn)
print('验证完成')

with open(pk_dir + '/error_log.pkl', 'wb') as f:
    pickle.dump(error_dict, f)

with open(pk_dir + '/error_log.pkl', 'rb') as f:
    err = pickle.load(f)
    print("[length: left, right] -include-> [length: left, right]")
    for k, v in err.items():
        print("[{}: {}, {}] -> [{}: {}, {}]".format(k.l, k.x, k.y, v.l, v.x, v.y))
