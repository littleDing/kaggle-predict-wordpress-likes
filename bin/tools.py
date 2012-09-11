from HTMLParser import HTMLParser
import logging
from threading import Timer
from operator import itemgetter

def sort_dic(d,reverse=False):
	return sorted(d.iteritems(), key=itemgetter(1), reverse=reverse)

class MLStripper(HTMLParser):
	def __init__(self):
		self.reset()
		self.fed = []
 	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ''.join(self.fed)
								
def strip_tags(html):
	s = MLStripper()      
	s.feed(html)
	return s.get_data()

class LineLogger():
	def __init__(self,name="",interval=10000,msg="lines loaded"):
		self.cnt =0
		self.interval = interval
		self.msg = msg
		if len(name) >0:
	   		name = name.split('/')
			name = name[-1]
		self.name=name
		logging.info(name+" begins")
	def end(self):
		logging.info(self.name+" ends")
	def inc(self):
		self.cnt += 1
		if self.cnt % self.interval == 0 :
			logging.info(self.name+' '+str(self.cnt) + " " + self.msg)

class LDFile() :
	def __init__(self,filename,open_tag='r') :
		self.filename = filename
		self.open_tag = open_tag
	def __enter__(self):
		self.fp = open(self.filename,self.open_tag)
		self.logger = LineLogger(self.filename)
		return self
	def __exit__(self, exc_type, exc_value, traceback):	
		self.logger.end()
		self.fp.close()
	def __iter__(self):
		for line in self.fp :
			self.logger.inc()
			yield line

def log_life():
	logging.info('i am alive')
	
def schedule_log_life():
	log_life()
	Timer(300,log_life)








