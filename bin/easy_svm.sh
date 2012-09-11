include=`dirname $0`
source $include/../conf/tools.conf


python easy_svm.py > $LOG_DIR/stdout.easy_svm.py 2>$LOG_DIR/stderr.easy_svm.py &
