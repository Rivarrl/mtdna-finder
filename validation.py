# -*- coding: utf-8 -*-
# ======================================
# @File    : validation.py
# @Time    : 2019/12/5 22:41
# @Author  : Rivarrl
# ======================================
import pickle
import os
from atgc import timeit
# 验证程序

class DoubleArea:
    def __init__(self, x, y, l):
        self.x = x
        self.y = y
        self.l = l

    def include(self, other):
        if self.l <= other.l or self.x > other.x or self.y > other.y: return False
        distance = self.l - other.l
        return other.x - self.x < distance and other.y - self.y < distance

def include(self, sl, other, ol):
    if sl <= ol or self[0] > other[0] or self[1] > other[1]: return False
    distance = sl - ol
    return other[0] - self[0] < distance and other[1] - self[1] < distance


pk_dir_name = 'pickle'
pk_dir = './' + pk_dir_name

@timeit
def validation(start=2, rewrite=False, stop_point='v'):
    # 写入pickle
    if not os.path.exists(pk_dir): os.mkdir(pk_dir_name)
    for fn in range(start, 14):
        if rewrite == False and os.path.exists(pk_dir + '/{}.pkl'.format(fn)): continue
        pk = set()
        with open('./result/{}.txt'.format(fn), 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            while line:
                stline = [e.strip() for e in line.split(' ') if e.strip()]
                p_start, q_start = map(int, stline)
                pk.add((p_start, q_start))
                line = f.readline().strip()
        with open(pk_dir + '/{}.pkl'.format(fn), 'wb') as f:
            pickle.dump(pk, f)
    print('写入完成')
    if stop_point == 'w': return

    # 读取pickle
    pk = {i: list() for i in range(start, 14)}
    for fn in range(start, 14):
        with open(pk_dir + '/{}.pkl'.format(fn), 'rb') as f:
            pk[fn] = pickle.load(f)
    print('读取完成')

    # 验证
    from collections import defaultdict
    error_dict = defaultdict(set)
    for fn in range(start, 13):
        for ofn in range(fn + 1, 14):
            for other in pk[ofn]:
                for da in pk[fn]:
                    if include(other, ofn, da, fn):
                        # print('找到')
                        p, q = other + (ofn, ), da + (fn, )
                        error_dict[p].add(q)
        print(fn, 'Done')
        pk.pop(fn)

    # 保存验证结果
    with open(pk_dir + '/error_log.pkl', 'wb') as f:
        pickle.dump(error_dict, f)
    print('验证完成')
    if stop_point == 'v': return

def show():
    with open(pk_dir + '/error_log.pkl', 'rb') as f:
        err = pickle.load(f)
        print("[length: left, right] -include-> [length: left, right]")
        for p, v in err.items():
            for q in v:
                print("[{}: {}, {}] -> [{}: {}, {}]".format(p.l, p.x, p.y, q.l, q.x, q.y))

if __name__ == '__main__':
    validation(start=5)
    show()