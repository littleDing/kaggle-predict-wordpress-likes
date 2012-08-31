import pickle
import logging
from tools import *
from conf import *
import json
import traceback

logging.basicConfig(level=logging.NOTSET,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

DUMP_PATH_BASE = TMP_DIR + '/pydumps/'

def load_blog_posts(filename,dumpname) :
	dump_path = DUMP_PATH_BASE + dumpname 
	blog_posts = {}
	try : 
		fin = open(dump_path)
		blog_posts = pickle.load(fin)
	except:
		logging.debug('\n'+traceback.format_exc())
		with open(DATA_DIR + filename) as fin :
			haha = LineLogger(name=filename)
			for line in fin :
				post = json.loads(line)
				blog = int(post['blog'])
				pid = int(post['post_id'])
				if blog in blog_posts :
					blog_posts[blog].append(pid)
				else :
					blog_posts[blog] = [pid]
				haha.inc()
			haha.end()
			with open(dump_path,'w') as fout :
				pickle.dump(blog_posts,fout)	
	return blog_posts

def load_blog_posts_train() :
	return load_blog_posts('trainPostsThin.json','blog_posts_train.pydump')

def load_blog_posts_test() :
	return load_blog_posts('testPostsThin.json','blog_posts_test.pydump')


def load_url_pid() :
	dump_path = TMP_DIR + '/pydumps/url_pid.pydump'
        url_pid = {}
        try :
                fin = open(dump_path)
                url_pid = pickle.load(fin)
        except:
		logging.debug('\n'+traceback.format_exc())
		with open(DATA_DIR + 'pid_url') as fin :
			for lin in fin :
			  try :
				sp = lin.split()
				pid = int(sp[0])
				url = sp[1]
				url_pid[url]=pid
			  except:
				pass
		with open(dump_path,'w') as fout :
			pickle.dump(url_pid,fout)
	return url_pid


def load_pid_lda() :
	dump_path = TMP_DIR + '/pydumps/pid_lda.pydump'
	posts = {}
	try :
		fin = open(dump_path)
		posts = pickle.load(fin)
	except: 
		logging.debug('\n'+traceback.format_exc())
		url_pid = load_url_pid()	
		with open(DATA_DIR + 'post_text.doc_topics') as fin :
			fin.readline()
			haha = LineLogger(name="pid_lda")
			for line in fin :
				sp = line.split()
				url = sp[1]
				if url in url_pid :
					pid = url_pid[url]
					posts[pid]={}
					for i in range(2,len(sp),2) :
						key = int(sp[i])
						value = float(sp[i+1])
						posts[pid][key]=value		
				haha.inc()
			haha.end()
		with open(dump_path,'w') as fout:
			pickle.dump(posts,fout)
	return posts

def main() :
	load_blog_posts_test()
	load_blog_posts_train()

if __name__ == '__main__' :
	main()


