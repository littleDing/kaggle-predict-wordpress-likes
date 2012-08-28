include=`dirname $0`
source $include/../conf/tools.conf

## Input: $1 => train data
##Output: $1.mallet => data imported into mallet
function train(){
local input=$1;
local input_file=${input##*/}
	#mkdir "${input}.sp";
	#split --verbose -d -a 6 -l 100000  ${input} ${input_file}
	#mv ${input_file}0* ${input}.sp   
	#$MALLET import-dir --input ${input}.sp --output ${input}.mallet   --keep-sequence --remove-stopwords --encoding gbk --print-output TRUE
	$MALLET import-file --input ${input} --output ${input}.mallet   --keep-sequence --remove-stopwords
	
	return ;
	$MALLET train-topics --input ${input}.mallet   --num-topics 100 --output-state topic-state.gz
	
}

train $DATA_DIR/post_text
