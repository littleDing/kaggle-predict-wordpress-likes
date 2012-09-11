import logging
from conf import *
from tools import *
import json
import pickle
from datas import *
import sys

def print_to_output(fout,filename,inTest):
	with LDFile(filename) as fin :
		for line in fin :
			obj = json.loads(line)
			obj['inTest'] = inTest
			fout.write(json.dumps(obj) + '\n')

def merge_test_train_post():
	with open(DATA_DIR+'allPosts.json','w') as fout :
		print_to_output(fout,DATA_DIR + 'trainPosts.json',False)
		print_to_output(fout,DATA_DIR + 'testPosts.json',True)

## Input : stdin(line)
## Output: stdout(uid inTest like post_feathures) 
def make_uid_posts():
	blog_likeusers = load_blog_likeusers()
	blog_posts_test = load_blog_posts_test()
	blog_posts_train = load_blog_posts_train()
	for line in sys.stdin :
		post = json.loads(line)
		bid = posts['blog']
		inTest = int(post['inTest']) 
		like_users = []
		for like in post['likes'] :
			like_users.append(like['uid'])
		if bid in blog_likeusers :
			for uid in blog_likeusers :
				like = int(uid in like_users) 
				print str(uid)+'\t',inTest,like,bid,author	


				
			



def main() :
	DUMP_PATH_BASE = './'
#	make_uid_posts()	
	merge_test_train_post()


if __name__ == '__main__' :
	main()



