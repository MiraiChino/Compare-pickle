import os
import pickle
import time
from functools import wraps
from pickletools import optimize

import _pickle as cPickle
from memory_profiler import memory_usage


def profile(filename):
    def _deco(func):
        def _wrapper(*args, **kwargs):
            start = time.perf_counter()
            max_mem_usage = max(memory_usage((func, args, kwargs)))
            end = time.perf_counter()
            filesize = os.path.getsize(filename) >> 20
            print(f"{func.__name__}, {max_mem_usage:.0f} MiB, {end - start:.2f} sec, {filename}, {filesize} MiB")
        return _wrapper
    return _deco

def gen_data(lines, list_size):
    for i in range(lines):
        yield {
            "id": i,
            "data": [f"data{i}{j}" for j in range(list_size)]
        }

def list_data(lines, list_size):
    return list(gen_data(lines, list_size))	

class Pickle:
    def __init__(self, pickle, protocol, name):
        self.pickle = pickle
        self.protocol = protocol
        self.name = name

    def dump(self, data, f):
        self.pickle.Pickler(f, protocol=self.protocol).dump(data)

    def dump_fast(self, data, f):
        pickler = self.pickle.Pickler(f, protocol=self.protocol)
        pickler.fast = True
        pickler.dump(data)

    def dump_opt(self, data, f):
        pickled = self.pickle.dumps(data, protocol=self.protocol)
        self.pickle.dump(optimize(pickled), f)

    def dump_gen(self, data, f):
        for x in data:
            self.pickle.Pickler(f, protocol=self.protocol).dump(x)

    def dump_gen_fast(self, data, f):
        pickler = self.pickle.Pickler(f, protocol=self.protocol)
        pickler.fast = True
        for x in data:
            pickler.dump(x)

    def dump_gen_opt(self, data, f):
        for x in data:
            self.dump_opt(x, f)

    def load(self, f):
        return self.pickle.load(f)

    def load_gen(self, f):
        unpickler = self.pickle.Unpickler(f)
        while True:
            try:
                yield unpickler.load()
            except:
                break

if __name__ == "__main__":
    pickle3 = Pickle(pickle, 3, "pickle3")
    pickle4 = Pickle(pickle, 4, "pickle4")
    cPickle3 = Pickle(cPickle, 3, "cPickle3")
    cPickle4 = Pickle(cPickle, 4, "cPickle4")

    list_data = list_data(500000, 100)
    gen_data = gen_data(500000, 100)

    for module in [pickle3, pickle4, cPickle3, cPickle4]:
        for dump in [module.dump, module.dump_fast, module.dump_opt]:
            filename = f"{dump.__self__.name}_{dump.__name__}.pkl".replace("_dump", "")
            
            @profile(filename=filename)
            @wraps(dump)
            def measure_dump():
                with open(filename, 'wb') as f:
                    dump(list_data, f)
            
            @profile(filename=filename)
            @wraps(module.load)
            def measure_load():
                with open(filename, 'rb') as f:
                    data = module.load(f)
                    for _ in data:
                        pass
            measure_dump()
            measure_load()

        for dump in [module.dump_gen, module.dump_gen_fast, module.dump_gen_opt]:
            filename = f"{dump.__self__.name}_{dump.__name__}.pkl".replace("_dump", "")
            
            @profile(filename=filename)
            @wraps(dump)
            def measure_dump_gen():
                with open(filename, 'wb') as f:
                    dump(list_data, f)
            
            @profile(filename=filename)
            @wraps(module.load_gen)
            def measure_load_gen():
                with open(filename, 'rb') as f:
                    data = module.load_gen(f)
                    for _ in data:
                        pass
            measure_dump_gen()
            measure_load_gen()
