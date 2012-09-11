import logging
from conf import *
from tools import *
import json
import pickle
from sklearn import svm
from sklearn.neighbors import KNeighborsRegressor
from sklearn import linear_model
from datas import *

logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')
WORD_BASE = 10007

def printPost(post,like) :
	ret = '0 '
	if like :
		ret = '1 '
	for word in post['tags'] :
		ret += str(word) + ':1 '
	for word in post['title'] :
		ret += str(word+WORD_BASE) + ':1 '
	return ret

def prepare_svm_input() :
	fav_blogs = {}
	haha = LineLogger(name='fav_blogs')
	dump_path = TMP_DIR+'/svm/fav_blog.pydump'
	try :
		fav_blogs = pickle.load(open(dump_path) )
	except :
		with open(DATA_DIR + 'kaggle-stats-users-20111123-20120423.json') as fin :
			for line in fin :
				user = json.loads(line)
				uid = int(user['user_id'])
				fav_blogs[uid] = []
				for blog in user['like_blog_dist'] :
					fav_blogs[uid] += [int(blog['blog_id'])]
				haha.inc()
			pickle.dump(fav_blogs,open(dump_path,'w'))
	haha.end()
	
	blog_posts_train = {}
	posts={}
	dump_path = TMP_DIR + '/svm/posts.pydump'
	try :
		with open(dump_path) as fin :
			posts = pickle.load(fin)
			blog_posts_train = pickle.load(fin)
			blog_posts_test = pickle.load(fin)
			fin.close()
		if False :
			for post in posts :
				post['title'] = list(set(post['title'])).sort()
				post['tags']  = list(set(post['tags'])).sort()
			with open(dump_path,'w') as fout :
				pickle.dump(posts,fout)
				pickle.dump(blog_posts_train,fout)
				pickle.dump(blog_posts_test,fout)
	except :
		with open(DATA_DIR + 'trainPosts.json') as fin :
			haha = LineLogger(name='trainPosts.json')
			for line in fin :
				post = json.loads(line)
				pid = int(post['post_id'])
				blogid = int(post['blog'])
				if blogid in blog_posts_train :
					blog_posts_train[blogid].append(pid)
				else :
					blog_posts_train[blogid] = [pid]
				posts[pid]={'tags':[],'title':[]}
				if post['tags'] != None :
					tmp = []
					for tag in post['tags'] :
						tmp.append(hash(tag) % WORD_BASE)
					posts[pid]['tags']=list(set(tmp))
					posts[pid]['tags'].sort()
				if post['title'] != None :
					tmp = []
					for word in post['title'].split() :
						tmp.append(hash(word) % WORD_BASE)
					posts[pid]['title']=list(set(tmp))
					posts[pid]['title'].sort()
				haha.inc()
		blog_posts_test = {}
		with open(DATA_DIR + 'testPosts.json') as fin :
			haha = LineLogger(name='testPosts.json')
			for line in fin :
				post = json.loads(line)
				pid = int(post['post_id'])
				blogid = int(post['blog'])
				if blogid in blog_posts_test :
					blog_posts_test[blogid].append(pid)
				else :
					blog_posts_test[blogid] = [pid]
				posts[pid]={'tags':[],'title':[]}
				if post['tags'] != None :
					tmp = []
					for tag in post['tags'] :
						tmp.append(hash(tag) % WORD_BASE)
					posts[pid]['tags']=list(set(tmp))
					posts[pid]['tags'].sort()
				if post['title'] != None :
					tmp = []
					for word in post['title'].split() :
						tmp.append(hash(word) % WORD_BASE)
					posts[pid]['title']=list(set(tmp))
					posts[pid]['title'].sort()
				haha.inc()
			haha.end()
		fout = open(dump_path,'w')
		pickle.dump(posts,fout)
		pickle.dump(blog_posts_train,fout)
		pickle.dump(blog_posts_test,fout)
		fout.close()

	with open(DATA_DIR + 'trainUsers.json') as fin :
		haha = LineLogger(name='trainUsers.json')
		for line in fin :
			user = json.loads(line)
			if user['inTestSet'] :
				uid = int(user['uid'])
				train_posts = []
				test_posts = []
				for blog in fav_blogs[uid] :
					try :
						train_posts += blog_posts_train[blog]
						test_posts += blog_posts_test[blog]
					except :
						pass
				like_posts = []
				for blog in user['likes'] :
					pid = int(blog['post_id'])
					like_posts.append(pid)
				with open(TMP_DIR+'/svm_input/svm_input_train.'+str(uid),'w') as fout :
					for pid in train_posts :
						fout.write(printPost(posts[pid],pid in like_posts)+'\n')	
				with open(TMP_DIR+'/svm_input/svm_input_test.' +str(uid),'w') as fout :
					for pid in test_posts :
						fout.write(printPost(posts[pid],False)+'\n')	
			haha.inc()
		haha.end()

def main():
	very_easy()

if __name__ == '__main__' :
	main()

