import time
import _pickle

def timeit(loop):
	def _deco(f):
		def _wrapper(*args, **kwargs):
			total_time = 0
			for i in range(loop):
				start = time.time()
				f(*args, **kwargs)
				end = time.time()
				total_time = total_time + (end - start)
			ave_time = total_time / loop
			print(f"{f.__name__}: {ave_time} sec")
		return _wrapper
	return _deco


def list_data(lines, list_size):
	data = []
	for i in range(lines):
		data += {
			"id": i,
			"data": [f"data{i}{j}" for j in range(list_size)]
		}
	return data

def gen_data(lines, list_size):
	for i in range(lines):
		yield {
			"id": i,
			"data": [f"data{i}{j}" for j in range(list_size)]
		}

@timeit(loop=1)
def dump_cPickle_gen(filename, data):
	with open(filename, 'wb') as f:
		pickler = _pickle.Pickler(f)
		for x in data:
			pickler.dump(x)

@timeit(loop=1)
def dump_cPickle_list(filename, data):
	with open(filename, 'wb') as f:
		_pickle.Pickler(f).dump(data)


dump_cPickle_gen("gen_data.pkl", gen_data(500000, 100))
dump_cPickle_list("list_data.pkl", list_data(500000, 100))

