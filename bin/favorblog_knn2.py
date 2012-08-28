#!/usr/bin/python 

import time
import random
from collections import defaultdict 
import sys
import numpy as np
import logging
import scipy.sparse as sp
import scipy.io as sio
import scipy.linalg as linalg


logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

top_num = 3 #Top blog to rec

blog_score = {}

logging.info('loading the file blog-num_posts')
for line in file('blog-num_posts-num_likes.txt'):
    cols = line[:-1].split('\t')
    blogid = int(cols[0])
    num_posts = float(cols[1])
    num_likes = float(cols[2])
    score = num_posts / (num_likes + 10) * np.log(num_likes + 10)
    blog_score[blogid] = score

logging.info('blog_num: %d' % (len(blog_score)))

user_blog_count = {}
user_posts = {}

logging.info('loading the file ../svd_input/train')

for line in file('../svd_input/train'):
    cols = line[:-1].split('\t')
    userid = int(cols[0])
    blogid = int(cols[1])
    postid = int(cols[2])
    if userid not in user_posts:
        user_posts[userid] = set()
    user_posts[userid].add(postid)

    if userid not in user_blog_count:
        user_blog_count[userid] = {}
    if blogid not in user_blog_count[userid]:
        user_blog_count[userid][blogid] = 1
    else:
        user_blog_count[userid][blogid] += 1

user_likes = {}

valid_users = set()
blog_posts = {}
valid_posts = set()

logging.info('loading the file ../svd_input/valid')
for line in file('../svd_input/valid'):
    cols = line[:-1].split('\t')
    userid = int(cols[0])
    blogid = int(cols[1])
    postid = int(cols[2])
    valid_users.add(userid)
    valid_posts.add(postid)
    if userid not in user_likes:
        user_likes[userid] = list()
    user_likes[userid].append(postid)
    
    if blogid not in blog_posts:
        blog_posts[blogid] = set()
    blog_posts[blogid].add(postid)

valid_blogs = blog_posts.keys()

logging.info('valid num_users= %d, num_blogs= %d, num_posts= %d',len(valid_users),len(valid_blogs), len(valid_posts))


'''
load the lda topic dis matrix
'''

logging.info('loading the lda topic dis matrix..')
#post_topic_matrix = np.loadtxt('/home/lijiefei/match/kaggle/wordpress/Data/script/doc-topics-dis-r300.out.map',delimiter=' ')
post_topic_matrix = sio.loadmat('/home/lijiefei/match/kaggle/wordpress/Data/script/doc-topics-dis-k300.mat')['topic_dis_mat'].tocsr()
logging.info('loading done.')



def score(userid,x):
    if userid not in user_blog_count or x not in user_blog_count[userid]:
        return 0
    return user_blog_count[userid][x]

def cos_simi(postid_1,postid_2):
    return np.vdot(post_topic_matrix[postid_1].todense(),post_topic_matrix[postid_2].todense()) / (linalg.norm(post_topic_matrix[postid_1].todense()) * linalg.norm(post_topic_matrix[postid_2].todense()) )
#    return np.dot(post_topic_matrix[postid_1],post_topic_matrix[postid_2]) / (np.sqrt(np.dot(post_topic_matrix[postid_1],post_topic_matrix[postid_1]) * np.sqrt(np.dot(post_topic_matrix[postid_2],post_topic_matrix[postid_2]))))


def mean_max_simi(userid,postid):
    if userid not in user_posts:
        return 0.0
    mean_simi = 0.0
    max_simi = -10.0
    for like_post in user_posts[userid]:
        temp = cos_simi(like_post, postid)
        mean_simi += temp
        max_simi = max(max_simi, temp)

    return mean_simi / len(user_posts[userid]), max_simi

def sample_mean_max_simi(sample_likes_list,postid):
    mean_simi = 0.0
    max_simi = -10.0
    for like_post in sample_likes_list:
        temp = cos_simi(like_post, postid)
        mean_simi += temp
        max_simi = max(max_simi, temp)

    return mean_simi / len(sample_likes_list), max_simi


def ap(userid,rec_posts):
    ap = 0.0
    likes = user_likes[userid]
    pos_count = 0
    for i in range(min(len(rec_posts),100)):
        if rec_posts[i] in likes:
            pos_count += 1
            ap = ap + float(pos_count) / (i+1)
    
    ap /= min(100,len(likes))
    return ap

sum_ap = 0.0
num_user_done = 0

logging.info('Begin eval the MAP@100...')
s_time = time.time()
blog_weight = 2.0
sample_size = 10

for userid in valid_users:
    r_time = time.time()
    post_score = defaultdict(int)
    if userid not in user_blog_count:
        continue
    for blog,count in user_blog_count[userid].items():
        if blog not in blog_posts:
            continue
        for post in blog_posts[blog]:
            post_score[post] += blog_weight * count / len(blog_posts[blog])
    
    logging.info('step 1 cost %f.sec', (time.time() - r_time))
    r2_time = time.time()
    likes_posts = list(user_posts[userid])
    sample_likes = random.sample(likes_posts,min(sample_size,len(likes_posts)))

    for post in post_score:
#        mean_simi,max_simi = mean_max_simi(userid,post)
        mean_simi,max_simi = sample_mean_max_simi(sample_likes,post)
        post_score[post] += max_simi
    
    logging.info('step 2 cost %f.sec', (time.time() - r2_time))
#    r3_time = time.time()
#    if len(post_score) < 100:
#        for post in valid_posts:
#            #mean_simi,max_simi = mean_max_simi(userid,post)
#            mean_simi,max_simi = sample_mean_max_simi(sample_likes,post)
#            post_score[post] += mean_simi
#        logging.info('step 3 cost %f.sec', (time.time() - r3_time))
#
#    r3_time = time.time()
#    if len(post_score) < 100:
#        for blog in blog_posts:
#            for post in blog_posts[blog]:
#                post_score[post] += blog_score[blog] / len(blog_posts[blog])
#
#    logging.info('step 3 cost %f.sec', (time.time() - r3_time))
#
    rec_posts = map(lambda x:x[0],sorted(post_score.items(),key=lambda x:-x[1]))

    ap_ = ap(userid,rec_posts[0:min(100,len(rec_posts))])
    logging.info('user %d AP=%f cost %f sec.' % (userid, ap_,time.time() - r_time))
    sum_ap += ap_
    num_user_done += 1
    if num_user_done % 20 == 0:
        e_time = time.time()
        logging.info('%d/%d Cost %f sec. MAP@100=%f' % (num_user_done,len(valid_users),(e_time - s_time),sum_ap/num_user_done))
        #s_time = time.time()

print 'MAP@100: %f' % (sum_ap / len(valid_users))

 
