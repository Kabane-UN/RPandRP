import sys
from multiprocessing import Process, Manager
from random import randint
import time


def gen_div(n):
    for i in range(2, n + 1):
        if n % i == 0:
            yield i


def gen_matrix(n):
    a = []
    for i in range(n):
        b = []
        for j in range(n):
            b.append(randint(-1000000000, 1000000000))
        a.append(b)
    return a


def mul_matrix(x, y, name):
    rez = []

    def get_row(z, j):
        g = []
        for i in range(len(z)):
            g.append(z[i][j])
        return g

    def mul_lines(z, r):
        g = []
        for i in range(len(z)):
            g.append(z[i] * r[i])
        return g

    for i in range(len(x)):
        g = []
        for j in range(len(y[0])):
            g.append(sum(mul_lines(x[i], get_row(y, j))))
        rez.append(g)
    if name != '0':
        d[name] = rez
    else:
        return rez


def matrix_sepper(m, n, by_lines):
    rez = []
    t = len(m) // n
    i = 0
    if by_lines:
        while i != len(m):
            rez.append(m[i:i + t])
            i += t
    else:
        while i != len(m):
            g = []
            for j in m:
                g.append(j[i:i + t])
            rez.append(g)
            i += t
    return rez


def sep_mul(a, b):
    proc = []
    for i in range(len(a)):
        for j in range(len(b)):
            proc.append(Process(target=mul_matrix, args=(a[i], b[j], f"{i},{j}",), daemon=True))
    return proc


def join(dic, l1, l2):
    rez = []
    for i in range(l1):
        g = []
        for j in range(l2):
            if not g:
                for k in dic[f"{i},{j}"]:
                    g.append(k)
            else:
                u = dic[f"{i},{j}"]
                for k in range(len(u)):
                    g[k] += u[k]
        for j in g:
            rez.append(j)
    return rez


if __name__ == '__main__':
    par = True
    N = 300
    a = gen_matrix(N)
    b = gen_matrix(N)
    start_time = time.time()
    res = mul_matrix(a, b, '0')
    print(f"--- %s seconds for {1} process---" % round(time.time() - start_time, 5))

    for n in gen_div(N):
        manager = Manager()
        d = manager.dict()
        c = matrix_sepper(a, n, True)
        h = matrix_sepper(b, n, False)
        procs = sep_mul(c, h)
        start_time = time.time()
        for i in range(len(procs)):
            procs[i].start()
        for i in range(len(procs)):
            procs[i].join()
        print(f"--- %s seconds for {len(procs)} process---" % round(time.time() - start_time, 5))
        print(res == join(d, len(c), len(h)))
