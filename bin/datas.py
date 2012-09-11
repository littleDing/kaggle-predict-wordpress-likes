import pickle
import logging
from tools import *
from conf import *
import json
import traceback
from operator import itemgetter

logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

DUMP_PATH_BASE = TMP_DIR + '/pydumps/'
#DUMP_PATH_BASE = TMP_DIR + '/jsons/'


class DataLoader() :
	def __init__(self,pass_head_line=0) :
		self.filename = '/dev/null'
		self.dump_path = '/dev/null'
		self.data = []
		self.pass_head_line = pass_head_line
		self.data_source = None
	def load_data(self) :
		try:
			logging.info('loading data from :' + self.dump_path )
			fin = open(self.dump_path)
			self.data = pickle.load(fin)
		except :
			logging.info('load data fail! try to construct from :' + self.filename )
#			with open(self.filename) as fin :
			self.data_source = self.load_data_source()
			haha = LineLogger(name = self.filename.split('/')[-1])
			self.preprocess()
			for line in self.data_source :
				self.deal_line(line)
				haha.inc()
			self.postprocess()
			haha.end()
			with open(self.dump_path,'w') as fout :
				logging.info('saving to dump file : '+self.dump_path)
				pickle.dump(self.data,fout)
		logging.info('load data finished!')
		return self.data		
	def load_data_source(self) :
		fin = open(self.filename)
		for i in range(0,self.pass_head_line) :
			fin.readline()
		return fin
	def preprocess(self)  :
		pass
	def deal_line(self,line)  :
		pass
	def postprocess(self) :
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

class PidBasics(DataLoader):
	def __init__(self,filename) :
		DataLoader.__init__(self,1)
		self.dump_path = DUMP_PATH_BASE + "pid_basics_" + filename + '.pydump'
		self.filename = DATA_DIR + filename
		self.data = {}
	def deal_line(self,line) :
		post = json.loads(line)
		pid = int(post['post_id'])
		not_need = ('url','language','context','post_id')
		obj = {}
		for key in post :
			if not key in not_need :
				obj[key] = post[key]  
		self.data[pid]=obj

## Output: { post_id:{infors except context, url and content} }
def load_pid_basics(filename) :
	return PidBasics(filename).load_data()
def load_pid_basics_test():
	return load_pid_basics("testPosts.json")
def load_pid_basics_train():
	return load_pid_basics("trainPosts.json")
def load_pid_basics_all():
	ret = load_pid_basics_train()
	ret.update(load_pid_basics_test())
	return ret

class PidLda(DataLoader):
	def __init__(self,filename='pid_language_context.lda') :
		DataLoader.__init__(self,1)
		self.dump_path = DUMP_PATH_BASE + '/pid_lda.pydump'
		self.filename = DATA_DIR + filename
		self.data = {}
	def deal_line(self,line) :
		sp = line.split()
		pid = int(sp[0])
		self.data[pid]=[] 
		tmp = {}
		for i in range(2,len(sp),2) :
			key = int(sp[i])
			value = float(sp[i+1])
			tmp[key] = value
		tmp = sorted(tmp.iteritems(),key=itemgetter(1))	
		self.data[pid] = [ pa[1] for pa in tmp  ]   

## Output: { post_id:[weight] }
def load_pid_lda() :
	return PidLda().load_data()

class Pid(DataLoader):
	def __init__(self) :
		DataLoader.__init__(self,1)
		self.dump_path = DUMP_PATH_BASE + '/pids.pydump'
		self.filename = DATA_DIR + 'allPosts.json'
		self.data = []
	def deal_line(self,line) :
		post = json.loads(line)
		print post
		pid = int(post['post_id'])
		self.data.append(pid)

## Output: [post_id]
def load_pids() :
	return Pid().load_data()

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
## Output : { blog_id : [user_id] }
def load_blog_likeusers() :
	blog_users = {}
	fav_blogs = load_fav_blogs()
	for uid in fav_blogs :
		for bid in fav_blogs[uid] :
			if bid in blog_users :
				blog_users[bid].append(uid)
			else :
				blog_users[bid] = [uid]
	return blog_users

class Testuids(DataLoader):
	def __init__(self) :
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + '/testuid.pydump'
		self.filename = DATA_DIR + 'testUsers.json'
		self.data = []
	def deal_line(self,line) :
		uid = int(line)
		self.data.append(uid)

## Output : [user_id]
def load_testuids() :
	return Testuids().load_data()	
		
class Ans(DataLoader):
	def __init__(self,filename) :
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + filename + '.pydump'
		self.filename = DATA_DIR + filename
		self.data = {}.fromkeys(load_testuids())
	def deal_line(self,line) :
		sp = line.split()
		uid = int(sp[0])
		self.data[uid] = []
		for i in range(1,len(sp)) :
			self.data[uid].append(int(sp[i]))

## Output : { user_id : [post_id] }
def load_ans(filename) :
	return Ans(filename).load_data()		

def tran_ans(filename) :
	ans = load_ans(filename)
	with open(DATA_DIR + filename + '.submit','w') as fout :
		for uid in ans :
			fout.write(str(uid)+',')
			if ans[uid] != None :
				for pid in ans[uid] :
					fout.write(str(pid)+' ')
			fout.write('\n')


class PidFeathures(DataLoader):
	def __init__(self) :
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + '/testuid.pydump'
		self.filename = DATA_DIR + 'testUsers.json'
		self.data = []
	def deal_line(self,line) :
		uid = int(line)
		self.data.append(uid)

## Output : {pid:[feathures]}
pid_feathure_keys = ['author','blogid','date','title','tags','categories','lda']
def load_pid_feathures() :
	return PidFeathures().load_data()	

class PidTfIdf(DataLoader):
	def __init__(self) :
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + '/pid_tfidf.pydump'
		self.filename = DATA_DIR + ''
	def deal_line(self,line) :
		pass

def load_pid_tiidf() :
	pass

class PidWords(DataLoader):
	def __init__(self,filename,dumpname,attname,doSplit) :
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE  + dumpname + '.pydump'
		self.filename = DATA_DIR + filename
		self.data = {}
		self.attname = attname
		self.doSplit = doSplit
	def deal_line(self,line) :
		post = json.loads(line)
		pid = int(post['post_id'])
		self.data[pid] = []
		words = post[self.attname]
		if words != None :
			if self.doSplit :
				self.data[pid] = words.split()
			else :
				self.data[pid] = words 
def load_pid_words(dumpprefix,att,sp):
	pid_words_train = PidWords('trainPosts.json',dumpprefix+'_train',att,sp).load_data()
	pid_words_test = PidWords('testPosts.json',dumpprefix+'_test',att,sp).load_data()
	pid_words_train.update(pid_words_test)
	return pid_words_train
def load_pid_tags():
	return load_pid_words('pid_tags','tags',False)
def load_pid_titles():
	return load_pid_words('pid_title','title',True)
def load_pid_categories():
	return load_pid_words('pid_categories','categories',False)

class WordCount(DataLoader):
	def __init__(self,datasource_loader,dumpname):
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + dumpname + '.pydump'
		self.filename  = getattr(datasource_loader,'__name__')
		self.data = {}
		self.datasource_loader = datasource_loader
	def load_data_source(self):
		return self.datasource_loader()
	def deal_line(self,line):
		pid = line
		for word in self.data_source[pid] :
			if word in self.data :
				self.data[word] +=1
			else :
				self.data[word] = 1

def load_tag_count():
	return WordCount(load_pid_tags,'tag_count').load_data()
def load_title_count():
	return WordCount(load_pid_titles,'title_count').load_data()
def load_category_count():
	return WordCount(load_pid_categories,'category_count').load_data()

class WordId(DataLoader):
	def __init__(self,datasource_loader,dumpname):
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + dumpname + '.pydump'
		self.data = {}
		self.cnt = 0
		self.datasource_loader = datasource_loader
		self.filename = getattr(datasource_loader,'__name__')
	def load_data_source(self) :
		return self.datasource_loader()
	def deal_line(self,line):
		self.data[line] = self.cnt
		self.cnt += 1
def load_tag_id():
	return WordId(load_tag_count,'tag_id').load_data()
def load_category_id():
	return WordId(load_category_count,'category_id').load_data()
def load_title_id():
	return WordId(load_title_count,'title_id').load_data()

class PidWordid(DataLoader) :
	def __init__(self,idmap_loader,datasource_loader,dumpname):
		DataLoader.__init__(self)
		self.dump_path = DUMP_PATH_BASE + dumpname + '.pydump'
		self.data = {}
		self.idmap_loader = idmap_loader
		self.datasource_loader = datasource_loader
		self.filename = getattr(datasource_loader,'__name__')
	def preprocess(self) :
		self.idmap = self.idmap_loader()
	def load_data_source(self):
		return self.datasource_loader()
	def deal_line(self,line):
		pid = line
	   	post = self.data_source[pid]
		self.data[pid] = [self.idmap[tag] for tag in post]   

def load_pid_tagid() :
	return PidWordid(load_tag_id,load_pid_tags,'pid_tagid').load_data()
def load_pid_titleid() :
	return PidWordid(load_title_id,load_pid_titles,'pid_titleid').load_data()
def load_pid_catid() :
	return PidWordid(load_category_id,load_pid_categories,'pid_categoriesid').load_data()

def main() :
#	load_pid_lda()
#	load_blog_posts_train()
#	load_blog_posts_test()	
#	load_url_pid()
#	tran_ans('ans.lda_sklearn_KNN')
#	tran_ans('ans.lda_sklearn_BayesianRidge')
#	tran_ans('ans.lda_sklearn_SVR')
#	load_pid_basics_all()
#	load_pid_tags()
#	load_tag_count()
#	load_tag_id()	
#	load_pid_tagid()
#	load_pid_titleid()
#	load_pid_catid()
	load_pids()
	pass

if __name__ == '__main__' :
	main()


