
import multiprocessing as mp
import math
import cProfile


def poly(x):
    x = float(x)
    for i in range(1000):
        n = math.sqrt(math.pi)
    return x**2 + math.sqrt(math.pi * n)


def compute():
    pool = mp.Pool(processes=2)
    results = [pool.apply_async(poly, args=(x,)) for x in range(40000)]
    polys = [r.get() for r in results]
    return polys


if __name__ == '__main__':
    cProfile.run('compute()')
