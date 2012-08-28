import logging
from conf import *
from tools import *
import json
import pickle
logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

## Input: trainUsers.json
## Output: user_favblog.txt(user blogs...) 
##			the user and his most like blogs
def find_favouritei_blog():
	fin = open(DATA_DIR + "trainUsers.json")
	fout = open(DATA_DIR + "user_favblog.txt","w")
	line_index = 0
	for line in fin :
		user = json.loads(line)
		if user['inTestSet'] :
			posts = user['likes']
			blogs = {}
			for post in posts :
				blog = post['blog']
				if blog in blogs :
					blogs[blog] += 1
				else : 
					blogs[blog] = 1
			blogs = sorted(blogs.items(), reverse=True,key=lambda d: d[1]) 
			fout.write(user['uid']+" ")
			cnt = 0
			for blog in blogs :
				fout.write(blog[0]+" ")
				cnt +=1;
				if cnt ==100 :
					break
			fout.write("\n")
		line_index +=1
		if line_index % 1000 ==0 :
			logging.info(str(line_index)+" users loaded")
	fin.close()	
	fout.close()

def collect_blog_post() :
	fposts = open(DATA_DIR + "testPostsThin.json")
	fout = open(DATA_DIR + "blog_post.pydump","w")
	blogs = {}
	haha = LineLogger("blog data",interval=10000)
	for line in fposts :
		post = json.loads(line)
		blog = int(post['blog'])
		if blog in blogs :
			blogs[blog].append(post['post_id'])
		else :
	   		blogs[blog] = [post['post_id']]
		haha.inc()
	haha.end()
	pickle.dump(blogs,fout)
	fout.close()

def rec_post(filename='user_rec.txt',max_per_user=200) :
	fusers = open(DATA_DIR + "user_favblog.txt")
	fout = open(DATA_DIR + filename,"w")
#	collect_blog_post()
	fposts = open(DATA_DIR + "blog_post.pydump")
	blogs = pickle.load(fposts)
	fposts.close()

	haha = LineLogger(interval=1000)
	for line in fusers :
		user = line.split(' ')
		fout.write(str(user[0])+',')
		cnt = 0
		for i in range(1,len(user)-1) :
			blog = int(user[i])
			if blog in blogs :
				posts = blogs[blog]
				for post in posts :
					fout.write(' '+str(post))
					cnt+=1
					if cnt ==max_per_user :
						break
			if cnt == max_per_user :
				break
		fout.write('\n')
		haha.inc()
	haha.end()

	fusers.close()
	fout.close()


def stat_blog():
	blogs = {}
	with open(DATA_DIR + 'trainPostsThin.json') as fin :
		haha = LineLogger(interval=10000)
		for line in fin :
			post = json.loads(line)
			post_id = int(post['post_id'])
			blog = int(post['blog'])
			if blog in blogs :
				blogs[blog].append(post_id)
			else :
				blogs[blog]=[post_id]
			haha.inc()
		haha.end()
	pickle.dump(blogs,open(DATA_DIR + 'blog_posts',"w"))

def writeToFile(post,like,fout) :
	if like :
		fout.write('1')
	else :
		fout.write('0')
	for tag in post['tags'] :
		fout.write(' '+str(tag)+':1')
	for word in post['title'] :
		fout.write(' '+str(word+10007)+':1')
	fout.write('\n')

def prepare_svm():
	posts = {}
	with open(DATA_DIR + 'trainPosts.json') as fin :
		haha = LineLogger(interval=10000,name='trainPosts')
		for line in fin :
			obj = json.loads(line)
			post = {}
			post['tags']=[]
			if 'tags' in obj and obj['tags'] != None:
				for tag in obj['tags'] :
					post['tags'].append(hash(tag)%10007)
			post['title']=[]
			if 'title' in obj and obj['title'] != None:
				for word in obj['title'].split() :
					post['title'].append(hash(word)%10007)
			posts[int(obj['post_id'])] = post
			haha.inc()
		haha.end()
	logging.info("all posts ready")
	pickle.dump(posts,open(TMP_DIR+"/svm/posts.pydump",'w'))
	
	rec_post("user_rec200.txt",200)
	test_posts = {}
	with open(DATA_DIR + 'user_rec200.txt') as fin :
		for line in fin :
			rec = line.split(',')
			uid = int(rec[0])
			user = []
			for post in rec[1].split() :
				user.append(int(post))
			test_posts[uid] = user
	logging.info("test posts ready")
	pickle.dump(test_posts,open(TMP_DIR+"/svm/test_posts.pydump",'w'))
	
	blogs = {}
	with open(DATA_DIR + 'blog_posts') as fin :
		blogs = pickle.load(fin)
	logging.info("blogs posts ready")
	pickle.dump(test_posts,open(TMP_DIR+"/svm/blogs.pydump",'w'))
	
	fav_blogs = {}
	with open(DATA_DIR + 'user_favblog.txt') as fin :
		for line in fin :
			user = line.split(' ')
			uid = int(user[0])
			fav_blogs[uid] = []
			for i in range(1,len(user)-1) :
				blog = int(user[i])
				fav_blogs[uid].append(blog)
	logging.info("fav blogs ready")
	pickle.dump(test_posts,open(TMP_DIR+"/svm/fav_blogs.pydump",'w'))
					
def do_svm() :
	posts = {}
	with open(TMP_DIR+"/svm/posts.pydump") as fin :
		posts = pickle.load(fin)
	
	
	test_posts = {}
	with open(TMP_DIR+"/svm/test_posts.pydump") as fin :
		test_posts = pickle.load(fin)
	
	blogs = {}
	with open(TMP_DIR+"/svm/blogs.pydump") as fin :
		test_posts = pickle.load(fin)
	
	fav_blogs = {}
	with open(TMP_DIR+"/svm/fav_blogs.pydump") as fin :
		fav_blogs = pickle.load(fin)

	with open(DATA_DIR + 'trainUsers.json') as fin :
		haha = LineLogger(interval=1000,name='prepare svm data')
		for line in fin :
			user = json.loads(line)
			uid = int(user['uid'])
			if uid in test_posts :
				like_posts = []
				for post in user['likes'] :
					like_posts.append(int(post['post_id']))
				train_posts = []
				for blog in fav_blogs[uid] :
					train_posts += blog
				with open(TMP_DIR + 'svm_input.'+str(uid),"w") as fout :
					for post in train_posts :
						like = post in like_posts
						writeToFile(posts[post],like,fout)
			haha.inc()
		haha.end()
				
				
def main() :
#	find_favourite()
#	rec_post()
#	stat_blog()
	prepare_svm()
#	do_svm()

if __name__ == '__main__' :
	main()








































