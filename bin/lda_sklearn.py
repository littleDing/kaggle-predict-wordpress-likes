import logging
from conf import *
from tools import *
import json
import pickle
from datas import *
from sklearn import svm
logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

def prindtPost(post,like) :
	ret = '0 '
	if like :
		ret = '1 '
	keys = post.keys()
	keys.sort()	
	for key in keys :
		ret += ' '+str(key) + '  ' + str(post[key]) + ' '
	return ret
		
def make_data(posts,post_ids,likes) :
	data = {'x':[],'y':[],'pid':[]}
	for pid in post_ids :
		if pid in posts :
			post = posts[pid]
			if pid in likes :
				data['y'].append(1)
			else :
				data['y'].append(0)
			x = []
			for key in post.keys() :
				x.append(post[key])
			data['x'].append(x)
			data['pid'].append(pid)
	return data

def recommand(data):
	tmp = []
	for i in range(0,len(data['y'])) :
		tmp.append((data['y'][i],data['pid'][i]))
	tmp.sort()
	ret = []
	cnt = min(100,len(tmp))
	for i in range(0,cnt) :
		ret.append(tmp[i][1])
	return ret

def make_output() :
	
	fav_blogs = load_fav_blogs() 
	
	blog_posts_test = load_blog_posts_test()
	blog_posts_train = load_blog_posts_train()	
	posts = load_pid_lda()

	with open(DATA_DIR + 'trainUsers.json') as fin :
	  with open(DATA_DIR + 'ans.lda.sklearn.txt','w') as fout :
	  	haha = LineLogger(name='trainUsers.json')
		for line in fin :
			user = json.loads(line)
			if user['inTestSet'] :
			  	uid = int(user['uid'])
			  	fout.write(str(uid)+',');
			  	try:
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
					train_data = make_data(posts,train_posts,like_posts)
					test_data = make_data(posts,test_posts,like_posts)
					predictor = svm.SVR(kernel='rbf')	
					test_data['y'] = predictor.fit(train_data['x'],train_data['y']).predict(test_data['x'])	
					rec = recommand(test_data)
					for pid in rec :
						fout.write(str(pid)+' ')
			  	except:
			  		pass
			  	fout.write('\n')
			haha.inc()
		haha.end()

def main():
	make_output()

if __name__ == '__main__' :
	main()

