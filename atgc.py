# -*- coding: utf-8 -*-
# ======================================
# @File    : atgc.py
# @Time    : 2019/12/3 20:53
# @Author  : Rivarrl
# ======================================
from collections import defaultdict
from copy import deepcopy
import time
import os

# mod = 2 ** 32
# 预先试出来的最大序列长度
max_ws = 13
min_ws = 2
# 四进制
a = 4
# A:0,T:1,G:2,C:3
atgc_dict = {"A":0, "T":1, "G":2, "C":3, "N":-1}
# 默认替换元素
trans_base = 0
atgc = ["A", "T", "G", "C"]
f = open('./dna.txt', 'r', encoding='utf-8')
mtdna = f.read().strip()
f.close()
dna = [atgc_dict[c] for c in mtdna]
rdna = dna[::-1]
N = len(dna)
result_path = 'result'
if not os.path.exists('./' + result_path): os.mkdir(result_path)


def timeit(f):
    # 测试运行时间用
    def wrapper(*args, **kwargs):
        t1 = time.time()
        r = f(*args, **kwargs)
        t2 = time.time()
        print("{0} runs: {1:.4f} sec".format(f.__name__, t2 - t1))
        return r
    return wrapper

def matrix_pretty_print(matrix):
    # 二维数组打印
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            print(matrix[i][j], end=' ')
        print()
    print()

def fetch(i, arr, t):
    # 从数组取数，N对应的-1用t替代
    if arr[i] == -1: return t
    return arr[i]

def find_unique_sub_sequence(n, arr):
    # rabin-karp
    # 第一次顺序查找所有同类子串并记录位置
    h = 0
    for i in range(n):
        h = h * a + arr[i]
    seen = defaultdict(list)
    seen[h].append(0)
    digit = pow(a, n-1)
    for i in range(1, N - n + 1):
        left, right = fetch(i-1, arr, trans_base), fetch(i+n-1, arr, trans_base)
        h = (h - left * digit) * a + right
        seen[h].append(i)
    return seen

def find_matching_sub_sequence(n, arr, need):
    # 第二次查找
    h = 0
    for i in range(n):
        h = h * a + arr[i]
    match_seen = defaultdict(list)
    if h in need: match_seen[h].append(0)
    digit = pow(a, n-1)
    for i in range(1, N - n + 1):
        left, right = fetch(i-1, arr, trans_base), fetch(i+n-1, arr, trans_base)
        h = (h - left * digit) * a + right
        if h in need: match_seen[h].append(i)
    return match_seen

# 解码字符串：找坐标字典比对
decode_str = lambda ilist: ''.join(list(map(lambda i: atgc[i], ilist)))

def encode_rk(arr):
    # 编码数组：rabin-karp
    h = 0
    for i in arr:
        h = h * a + i
    return h

def decode_rk(hash, n):
    # 解码数组：rabin-karp
    i = 0
    res = [0] * n
    while hash // (a ** i) > 0:
        j = (hash // (a ** i)) % a
        res[i] = j
        i += 1
    return res[::-1]

# 计算配对
calc_match = lambda arr: [{0:1, 1:0, 2:3, 3:2}[i] for i in arr]
# 获取镜像下标
mirror_i = lambda i: N-i

def duplicated_batch_finder(window_size):
    # 包含正反重叠的配对串
    seen = find_unique_sub_sequence(window_size, dna)
    need = set()
    seen_match_mappings = {}
    for h in seen:
        arr = decode_rk(h, window_size)
        rarr = calc_match(arr)
        rh = encode_rk(rarr)
        seen_match_mappings[h] = rh
        need.add(rh)
    match_seen = find_matching_sub_sequence(window_size, rdna, need)
    seen = {k:v for k, v in seen.items() if seen_match_mappings[k] in match_seen}
    return seen, match_seen, seen_match_mappings

def duplicate_check(x1, y1, x2, y2):
    # 重叠检测
    # 左闭右开区间[x, y)，所以2在1右侧且x2=y1的时候也不算重叠。
    if x1 > x2: duplicate_check(x2, y2, x1, y1)
    return x2 < y1

def filter_finder(window_size):
    seen, match_seen, seen_match_mappings = duplicated_batch_finder(window_size)
    seen_filter = {}
    for k in seen:
        d = seen_filter[k] = defaultdict(list)
        rk = seen_match_mappings[k]
        idxs, ridxs = seen[k], match_seen[rk]
        for i in idxs:
            for j in ridxs:
                double_points = i, i+window_size, mirror_i(j+window_size), mirror_i(j)
                if not duplicate_check(*double_points):
                    d[i].append(j)
        if not d: seen_filter.pop(k)
    return seen_filter

def generate_pairs(seen, ws):
    # 打印用
    pairs = []
    for k in seen:
        idxs = seen[k]
        for i in idxs:
            ridxs = idxs[i]
            for j in ridxs:
                pairs += [[i, mirror_i(j+ws)]]
    return pairs

@timeit
def exclusion_and_output():
    ban = defaultdict(int)
    dxy = ((0, 0, 0, 0), (-1, 0, -1, 0), (-1, 0, 0, 1), (0, 1, -1, 0), (0, 1, 0, 1))

    for ws in range(max_ws, min_ws-1, -1):
        seen_filter = filter_finder(ws)
        pairs = generate_pairs(seen_filter, ws)
        exclusion_pairs = []
        for s1, s2 in pairs:
            da = (s1, s1 + ws, s2, s2 + ws)
            for e in dxy:
                if tuple(da[i] + e[i] for i in range(4)) in ban: break
            else:
                exclusion_pairs.append("{:6d}\t{:6d}\n".format(s1, s2))
            if ws == min_ws: continue
            ban[da] = ws
        with open('./{}/{}.txt'.format(result_path, ws), 'w', encoding='utf-8') as f:
            f.writelines(exclusion_pairs)
        print(ws, 'Done')

@timeit
def exclusion_and_output_v2():
    ban = {i:set() for i in range(2, 14)}
    for ws in range(max_ws, min_ws-1, -1):
        seen_filter = filter_finder(ws)
        pairs = generate_pairs(seen_filter, ws)
        exclusion_pairs = []
        for s1, s2 in pairs:
            if (s1, s2) in ban[ws]: continue
            exclusion_pairs.append("{:6d}\t{:6d}\n".format(s1, s2))
            for window in range(2, ws):
                for i in range(ws-window+1):
                    for j in range(ws-window+1):
                        ban[window].add((s1+i, s2+j))
        with open('./{}/{}.txt'.format(result_path, ws), 'w', encoding='utf-8') as f:
            f.writelines(exclusion_pairs)
        print(ws, 'Done')

if __name__ == '__main__':
    # ws = 12
    # seen_filter = filter_finder(ws)
    # pairs = generate_pairs(seen_filter, ws)
    # matrix_pretty_print(pairs)
    exclusion_and_output_v2()