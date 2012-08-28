from HTMLParser import HTMLParser
import logging

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
	def __init__(self,name="",interval=1000,msg="lines loaded"):
		self.cnt =0
		self.interval = interval
		self.msg = msg
		self.name=name
		logging.info(name+" begins")
	def end(self):
		logging.info(self.name+" ends")
	def inc(self):
		self.cnt += 1
		if self.cnt % self.interval == 0 :
			logging.info(str(self.cnt) + " " + self.msg)


