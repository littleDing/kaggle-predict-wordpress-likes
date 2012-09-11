import pickle
import logging
from tools import *
from conf import *
import json
from sklearn import svm
from sklearn.neighbors import KNeighborsRegressor
from sklearn import linear_model
from sys import stdin
import random
import traceback

logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')


data_fields = ['x','y','pid']
def insert(tdata,sdata,index):
	for field in data_fields :
		tdata[field].append(sdata[field][index])
		
def add_to(data,sp) :
	data['pid'].append(int(sp[2]))
	data['y'].append(int(sp[3]))
	x = []
	for i in range(4,len(sp)) :
		x.append(float(sp[i]))
	data['x'].append(x)

def recommand(data):
	tmp = []
	for i in range(0,len(data['y'])) :
		tmp.append((data['y'][i],data['pid'][i]))
	tmp.sort(reverse=True)
	ret = []
	cnt = min(100,len(tmp))
	for i in range(0,cnt) :
		ret.append(tmp[i][1])
	return ret

def sampling(data):
	sampling_theta = 10000
	if len(data['y']) < sampling_theta :
		return data
	else :
		ret = {'x':[],'y':[],'pid':[]}
		index = []
		for i in range(0,len(data['y'])) :
			if data['y'][i] == 1 :
				insert(ret,data,i)
			else :
				index.append(i)
		left = len(data['y']) - len(ret['y']) 
		if left < sampling_theta :
			return data
		else :
			sel = random.sample(index,sampling_theta)
			for i in sel :
				insert(ret,data,i)
			return ret
		
def output(uid,train_data,test_data) :
	if uid != -1 :
		logging.info("culculating for user "+str(uid))
		train_data = sampling(train_data)
		to_print = str(uid)+'\t'
		try :
			predictor = svm.SVR(kernel='rbf')
			#predictor = KNeighborsRegressor(n_neighbors=0.01*len(train_data['y']))
			#predictor = linear_model.BayesianRidge()
			test_data['y'] = predictor.fit(train_data['x'],train_data['y']).predict(test_data['x'])	
			rec = recommand(test_data)
			for pid in rec :
				to_print += str(pid)+' '
		except:
			pass	
		logging.info("culculate for user "+str(uid) +" seccuss!")
		print to_print

## Input  : stdin(uid\t{inTest pid y [x...]}
## Output : stdout(uid\t[pid...]) 
def do_reduce():
	schedule_log_life
	try : 
		last_uid = -1
		train_data = []
		test_data = []
		while True :
			line = stdin.readline()
			if len(line) == 0 :
				output(last_uid,train_data,test_data)
				break
			sp = line.split()
			uid = int(sp[0])
			if uid != last_uid :
				output(last_uid,train_data,test_data)
				test_data =  {'x':[],'y':[],'pid':[] }
				train_data = {'x':[],'y':[],'pid':[] }
			inTest = int(sp[1])
			if inTest == 0 :
				add_to(train_data,sp)
			else :
				add_to(test_data,sp)
			last_uid = uid
	except EOFError :
		output(last_uid,train_data,test_data)
	except :
		traceback.print_exc()
		with open('core.dump','w') as fout:
			pickle.dump({'uid':last_uid,'test_data':test_data,'train_data':train_data},fout)

def main():
	do_reduce()


if __name__ == '__main__' :
	main()

