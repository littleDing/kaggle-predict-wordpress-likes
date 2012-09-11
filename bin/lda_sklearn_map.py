import pickle
import logging
from tools import *
from conf import *
import json
from sklearn import svm
from sklearn.neighbors import KNeighborsRegressor
from sklearn import linear_model
from sys import stdin
import random
import traceback
from datas import *

logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

def get_data(string):
	return [] if string == '-1' else [int(tag) for tag in string.split(',') ]

## Input   : stdin(pid_test_author_blog_tag_category_likes_title_lda)
## Output  : stdout(uid\t{inTest pid y [x...]}
def do_map():
	blog_likeusers = load_blog_likeusers()
	for line in stdin :
		sp = line.split()
		pid = int(sp[0])
		test = sp[1]	
		author = int(sp[2])
		bid = int(sp[3])
		tags = get_data(sp[4])
		cats = get_data(sp[5])
		likes = get_data(sp[6])
		title = get_data(sp[7])
		lda = get_data(sp[8])
		if bid in blog_likeusers :
			for uid in blog_likeusers[bid] :
				y = 1 if uid in likes else 0
				ldas = ' '.join([str(w) for w in lda])
				output = ' '.join([str(uid)+'\t'+test,str(pid),str(y),str(bid),str(author),ldas])
				print output

def main():
	do_map()


if __name__ == '__main__' :
	main()

