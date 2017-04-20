COMMAND="./run.sh FROM_GENOME TO_GENOME NUM_READS READ_LENGTH"

if [[ -z "$1" ]]; then
    echo "FROM_GENOME not provided"
    echo "$COMMAND"
    exit
fi

if [[ -z "$2" ]]; then
    echo "TO_GENOME not provided"
    echo "$COMMAND"
    exit
fi

if [[ -z "$3" ]]; then
    echo "NUM_READS not provided"
    echo "$COMMAND"
    exit
fi

if [[ -z "$4" ]]; then
    echo "READ_LENGTH not provided"
    echo "$COMMAND"
    exit
fi

FROM_GENOME=$1
TO_GENOME=$2
NUM_READS=$3
READ_LENGTH=$4
