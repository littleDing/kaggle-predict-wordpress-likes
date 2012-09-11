import pickle
import logging
from tools import *
from conf import *
import json
import traceback
import datas

logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

DUMP_PATH_BASE = TMP_DIR + '/plain_text/'

class Object():
	def read_from_line(self,line):
		pass
	def save_to_line(self)
		pass

class DataLoader() :
	def __init__(self,pass_head_line=0) :
		self.filename = ""
		self.dump_path = ""
		self.data = []
		self.pass_head_line = pass_head_line
	def load_data(self):
	def process_data(self,return_data=False):
		try:
			logging.info('loading data from saved text:' + self.dump_path )
			fin = open(self.dump_path)
			for line in fin :
				deal_saved_line(line)
		except :
			logging.info('load data fail! try to construct from :' + self.filename )
			with open(self.filename) as fin :
				haha = LineLogger(name = self.filename.split('/')[-1])
				self.preprocess()
				for i in range(0,self.pass_head_line) :
					fin.readline()
				for line in fin :
					obj = self.deal_raw_line(line)
					haha.inc()
				self.postprocess()
				haha.end()
			with open(self.dump_path,'w') as fout :
				logging.info('saving to dump file : '+self.dump_path)
				pickle.dump(self.data,fout)
		logging.info('load data finished!')
		if return_data :
			return self.data		
	def preprocess(self):
		pass
	def deal_raw_line(self,line):
		pass
	def postprocess(self):
		pass
	def deal_saved_line(self,line):
		pass
	























































	













