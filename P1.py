import time

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
E = 0.00001


def gen_matrix(n):
    a = []
    b = []
    for i in range(n):
        g = []
        for j in range(n):
            if i == j:
                g.append(2.0)
            else:
                g.append(1.0)
        a.append(g)
        b.append(n + 1)
    return a, b


def sep_by_lines(a, n):
    As = []
    t = len(a) // n
    i = 0
    while i != len(a):
        As.append(a[i:i + t])
        i += t
    return As


def matrix_apply(a, x):
    res = []
    for i in a:
        s = 0
        # for j, k in i, x:
        for j in range(len(i)):
            s += i[j] * x[j]
        res.append(s)
    return res


def matrix_minus(a, b):
    res = []
    for i in range(len(a)):
        res.append(a[i] - b[i])
    return res


def matrix_norm(a):
    res = 0
    for i in a:
        res += i ** 2
    return res ** .5


def matrix_sing_mul(r, a):
    res = []
    for i in a:
        res.append(r * i)
    return res


def f(a, b, x, xx, n, neg):
    if not neg:
        return matrix_minus(xx, matrix_sing_mul(0.1 / n, matrix_minus(matrix_apply(a, x), b)))
    else:
        return matrix_minus(xx, matrix_sing_mul(- 0.1 / n, matrix_minus(matrix_apply(a, x), b)))


def g(a, x, b):
    return matrix_norm(matrix_minus(matrix_apply(a, x), b)) / matrix_norm(b)


if rank == 0:
    N = 2 ** 12
    a, b = gen_matrix(N)
    As = sep_by_lines(a, size - 1)

    x = [0 for _ in range(N)]
    flag = True
    e = g(a, x, b)
    neg = False
    start_time = time.time()
    while flag:
        for i in range(1, size):
            comm.send([As[i - 1], b, x, True, neg], dest=i, tag=101)
        gg = []
        for i in range(1, size):
            res = comm.recv(source=i, tag=101)
            for j in res:
                gg.append(j)
        x = gg
        ne = g(a, x, b)
        if ne < 0.00001:
            flag = False
            for i in range(1, size):
                comm.send([As[i - 1], b, x, False, neg], dest=i, tag=101)
        elif ne > e:
            neg = not neg
        e = ne

    print(x)
    print(f"--- %s seconds for {size-1} kernels ---" % round(time.time() - start_time, 5))

else:
    flag = True
    while flag:
        a, b, x, flag, neg = comm.recv(source=0, tag=101)
        if not flag:
            break
        Bs = sep_by_lines(b, size - 1)
        Xs = sep_by_lines(x, size - 1)
        res = f(a, Bs[rank - 1], x, Xs[rank - 1], len(b), neg)
        comm.send(res, dest=0, tag=101)



