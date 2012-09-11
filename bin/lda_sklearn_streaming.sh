include=`dirname $0`
source $include/../conf/tools.conf


function streaming(){
HDFS_DIR="/user/apache/dingweijie/kaggle/wordpress/"
INPUT="${HDFS_DIR}/input.lda.sklearn"
OUTPUT="${HDFS_DIR}/lda_sklearn_SVR/output/"
	${HADOOP} fs -rmr $OUTPUT
	${STREAMING}  -D mapred.job.name='lda_sklearn_SVR' -numReduceTasks 30 \
		-input $INPUT -output $OUTPUT -mapper "cat" -reducer "python lda_sklearn_reduce.py" \
		-file lda_sklearn_reduce.py \
		-file conf.py -file tools.py 
}

streaming
