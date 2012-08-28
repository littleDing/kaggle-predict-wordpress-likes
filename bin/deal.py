from conf import * 
from tools import *
from os import system
import logging
import json


logging.basicConfig(level=logging.NOTSET);

def extract_text() :
	fin = open(DATA_DIR + "trainPosts.json")
	fout = open(DATA_DIR + "trainPosts.id_text","w")
	logging.info("starting...");
	line_cnt = 0;
	while True :
		line = fin.readline();
		if len(line)==0 :
			break
		else : 
			line_cnt = line_cnt + 1
			if line_cnt % 10000 ==0 :
				logging.info(str(line_cnt) + "record loaded");
			post = json.loads(line)
			try:
				text = strip_tags(post['content'])
			except (Exception),e :
				logging.error("error at line : "+str(line_cnt))
				logging.error(e)
#logging.error("raw text = "+post['content'])
			text = text.replace("\n"," ");
			text = text.replace("\r\n"," ");
			text = text.replace("\r"," ");
			to_write = post['post_id'] +u" x "+ text +u"\n" 
			fout.write(to_write.encode("utf-8"))
	logging.info("ending...");
	fin.close();
	fout.close();

def extract_text_feige() :
	with open('posts.mallet.input2','w') as fp:
		haha = LineLogger(interval=10000)
		for line in file(DATA_DIR + '/trainPosts.json'):
		    row = json.loads(line)
		    url = row['url']
		    langu = row['language']
		    content = row['content']
		    if content:
		        try:
		            text = strip_tags(content).encode('ascii','ignore').replace('\n',' ').replace('\r',' ')
		        except:
		            text = ''
		    else:
		        text = ''
		    print >> fp, ' '.join([url,langu,text])
		    haha.inc()
		haha.end()
		
		haha = LineLogger(interval=10000)
		for line in file(DATA_DIR + '/testPosts.json'):
		    row = json.loads(line)
		    url = row['url']
		    langu = row['language']
		    content = row['content']
		    if content:
		        try:
		            text = strip_tags(content).encode('ascii','ignore').replace('\n',' ').replace('\r',' ')
		        except:
		            text = ''
		    else:
		        text = ''
		    print >> fp, ' '.join([url,langu,text])
		    haha.inc()
		haha.end()



def make_LDA_for_file(filename) : 
	fin = open(filename)
	fout = open(filename + ".lda","w")
	




def main() :
#	extract_text()
	extract_text_feige()
	

if __name__ == '__main__' :
	main()
