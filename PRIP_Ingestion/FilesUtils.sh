

function split_file() {
  FILEPATH=$1
  NUM_BATCH=$2
  FILE_PREFIX=$3
  # TODO: Compute path
  split -l $NUM_BATCH  -d -a 3 $FILEPATH $FILE_PREFIX
  # Retrieve genrated files and return as a list
  SPLITTED_FILES=$(ls ${FILE_PREFIX}???)
  echo "$SPLITTED_FILES"
}

