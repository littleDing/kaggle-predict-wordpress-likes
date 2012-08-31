import logging
from conf import *
from tools import *
import json
import pickle
from datas import *
logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')
WORD_BASE = 10007

def printPost(post,like) :
	ret = '0 '
	if like :
		ret = '1 '
	keys = post.keys()
	keys.sort()	
	for key in keys :
		ret += ' '+str(key) + '  ' + post[key] + ' '
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
	
	posts = load_pid_lda()

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
	prepare_svm_input()

if __name__ == '__main__' :
	main()

