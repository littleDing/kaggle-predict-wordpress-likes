import pickle
import logging
from tools import *
from conf import *
import json
import traceback
from datas import *

logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

class HadoopData():
	def make_output():
		pass


##Output: file(pid\tinTest author blog tags categories likes titles lda_feathue)
class HadoopData1(DataLoader):
	def __init__(self,filename,inTest,fout):
		DataLoader.__init__(self)
		self.filename = DATA_DIR + filename 
		self.inTest = str(inTest)
		self.fout = fout
	def preprocess(self):
		self.pid_tags = load_pid_tagid()
		self.pid_categories = load_pid_catid()
		self.pid_titles = load_pid_titleid()
		self.pid_lda = load_pid_lda()
#		with open(DATA_DIR+'pid_test_author_blog_tag_category_likes_title_lda','w') as fout :
	def deal_line(self,line):
		post = json.loads(line)
		pid = int(post['post_id'])
		if len(self.pid_tags[pid]) > 0 :
			tags  = ",".join([str(tag) for tag in self.pid_tags[pid]   ])
		else :
			tags  = "-1"
		if len(self.pid_titles[pid]) > 0 :
			title = ",".join([str(tag) for tag in self.pid_titles[pid]  ])
		else :
			title = "-1"
		if len(self.pid_categories[pid]) > 0 :
			cat   = ",".join([str(tag) for tag in self.pid_categories[pid]   ])
		else :
			cat = "-1"
		if 'like' in post and  post['like'] != None and len(post['like']) > 0 :
			likes = ",".join(like['uid'] for like in post['likes'] )
		else :
			likes = "-1"
		if pid in self.pid_lda :
			lda   = ",".join([str(w)   for w in self.pid_lda[pid]] )	
		else :
			lda   = "-1"
		outputs = [	str(pid)+"\t"+self.inTest, post['author'], post['blog'],tags,cat,likes,title,lda ]  
		self.fout.write(' '.join(outputs))
		self.fout.write('\n')

class HadoopDataJson(DataLoader):
	def __init__(self):
		DataLoader.__init__(self)
		self.filename = DATA_DIR+'pid_test_author_blog_tag_category_likes_title_lda' 






def make_output():
	fout = open(DATA_DIR+'pid_test_author_blog_tag_category_likes_title_lda','w')
	HadoopData1('trainPosts.json',0,fout).load_data()
	HadoopData1('testPosts.json',1,fout).load_data()

def main():
	make_output()
	pass	

if __name__ == '__main__' :
	main()
