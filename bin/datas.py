import pickle
import logging
from tools import *
from conf import *
import json
import traceback

logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

DUMP_PATH_BASE = TMP_DIR + '/pydumps/'

class DataLoader() :
	def __init__(self,pass_head_line=0) :
		self.filename = ""
		self.dump_path = ""
		self.data = []
		self.pass_head_line = pass_head_line
	def load_data(self) :
		try:
			logging.info('loading data from :' + self.dump_path )
			fin = open(self.dump_path)
			self.data = pickle.load(fin)
		except :
			logging.info('load data fail! try to construct from :' + self.filename )
			with open(self.filename) as fin :
				haha = LineLogger(name = self.filename.split('/')[-1])
				for i in range(0,self.pass_head_line) :
					fin.readline()
				for line in fin :
					self.deal_line(line)
					haha.inc()
				haha.end()
			with open(self.dump_path,'w') as fout :
				logging.info('saving to dump file : '+self.dump_path)
				pickle.dump(self.data,fout)
		logging.info('load data finished!')
		return self.data		
	def deal_line(self,line) :
		pass

class BlogPosts(DataLoader):
	def __init__(self,filename,dumpname) :
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + dumpname
		self.filename = DATA_DIR + filename
		self.data = {}
	def deal_line(self,line) :
		post = json.loads(line)
		blog = int(post['blog'])
		pid = int(post['post_id'])
		blog_posts = self.data
		if blog in blog_posts :
			blog_posts[blog].append(pid)
		else :
			blog_posts[blog] = [pid]

def load_blog_posts(filename,dumpname) :
	bp = BlogPosts(filename,dumpname)
	blog_posts = bp.load_data()
	return blog_posts

## Output: {blog_id:[post_id in train]}
def load_blog_posts_train() :
	return load_blog_posts('trainPostsThin.json','blog_posts_train.pydump')
## Output: {blog_id:[post_id in test]}
def load_blog_posts_test() :
	return load_blog_posts('testPostsThin.json','blog_posts_test.pydump')

class UrlPid(DataLoader):
	def __init__(self) :
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + '/url_pid.pydump'
		self.filename = DATA_DIR + 'pid_url'
		self.data = {}
	def deal_line(self,line) :
		try :
	   		sp = line.split()
			pid = int(sp[0])
			url = sp[1]
			self.data[url]=pid
		except : 
			pass
## Output:{ url:post_id }
def load_url_pid() :
	UP = UrlPid()
	return UP.load_data()

class PidLda(DataLoader):
	def __init__(self,filename='post_text.doc_topics') :
		DataLoader.__init__(self,1)
		self.dump_path = DUMP_PATH_BASE + '/pid_lda.pydump'
		self.filename = DATA_DIR + filename
		self.data = {}
		self.url_pid = UrlPid().load_data()
	def deal_line(self,line) :
		sp = line.split()
		url = sp[1]
		if url in self.url_pid :
			pid = self.url_pid[url]
			self.data[pid]={}
			for i in range(2,len(sp),2) :
				key = int(sp[i])
				value = float(sp[i+1])
				self.data[pid][key] = value	

## Output: { post_id:{ topic_index:weight } }
def load_pid_lda() :
	return PidLda().load_data()

class FavBlogs(DataLoader):
	def __init__(self) :
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + '/fav_blogs.pydump'
		self.filename = DATA_DIR + 'kaggle-stats-users-20111123-20120423.json'
		self.data = {}
	def deal_line(self,line) :
		user = json.loads(line)
		uid = int(user['user_id'])
		self.data[uid] = []
		for blog in user['like_blog_dist'] :
			self.data[uid] += [int(blog['blog_id'])]

## Output : { user_id : [blog_id] }
def load_fav_blogs() :
	return FavBlogs().load_data()
		
def main() :
#	load_pid_lda()
#	load_blog_posts_train()
#	load_blog_posts_test()	
#	load_url_pid()
	pass

if __name__ == '__main__' :
	main()


