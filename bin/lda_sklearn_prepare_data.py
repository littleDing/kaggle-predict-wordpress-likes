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

def make_hadoop_input(data,index,tag):
	ret = str(tag) + ' ' + str(data['pid'][index]) + ' '+str(data['y'][index])
	for x in data['x'][index]:
		ret += ' ' + str(x)	
	return ret

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


## Output : file(uid\t{inTest pid y [x...]}
def make_output() :
	fav_blogs = load_fav_blogs() 
	
	blog_posts_test = load_blog_posts_test()
	blog_posts_train = load_blog_posts_train()	
	posts = load_pid_lda()

	with open(DATA_DIR + 'trainUsers.json') as fin :
	  with open(DATA_DIR + 'input.lda.sklearn','w') as fout :
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
				train_data = make_data(posts,train_posts,like_posts)
				test_data = make_data(posts,test_posts,like_posts)
				for index in range(0,len(train_data['x'])) :
					s = make_hadoop_input(train_data,index,0)
					fout.write(str(uid)+'\t'+s+'\n')
				for index in range(0,len(test_data['x'])) :
					s = make_hadoop_input(test_data,index,1)
					fout.write(str(uid)+'\t'+s+'\n')
			haha.inc()
		haha.end()

def main():
	make_output()

if __name__ == '__main__' :
	main()

