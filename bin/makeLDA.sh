include=`dirname $0`
source $include/../conf/tools.conf

## Input: $1 => train data
##Output: $1.mallet => data imported into mallet
function train(){
local input=$1;
local input_file=${input##*/}
	$MALLET import-file --input ${input} --output ${input}.mallet   --keep-sequence --remove-stopwords
	$MALLET train-topics --input ${input}.mallet --num-topics 200 --output-state ${input}.state --num-threads 8 --output-doc-topics ${input}.lda 
}

train $DATA_DIR/pid_language_context >$LOG_DIR/stdout.makeLDA 2>$LOG_DIR/stderr.makeLDA
