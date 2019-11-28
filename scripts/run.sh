set -e
set -x

COMMAND="./run.sh GENOME_PATH NUM_READS READ_LENGTH NUM_DUPS BIN_SIZE SEQUENCING_ERROR_RATE"

trap "exit" INT

if [[ -z "$1" ]]; then
    echo "GENOME_PATH"
    echo "$COMMAND"
    exit
fi

if [[ -z "$2" ]]; then
    echo "NUM_READS not provided"
    echo "$COMMAND"
    exit
fi

if [[ -z "$3" ]]; then
    echo "READ_LENGTH not provided"
    echo "$COMMAND"
    exit
fi

if [[ -z "$4" ]]; then
    echo "NUM_DUPS not provided"
    echo "$COMMAND"
    exit
fi

if [[ -z "$5" ]]; then
    echo "BIN_SIZE not provided"
    echo "$COMMAND"
    exit
fi

if [[ -z "$6" ]]; then
    echo "SEQUENCING_ERROR_RATE not provided"
    echo "$COMMAND"
    exit
fi

GENOME_PATH=$1
NUM_READS=$2
READ_LENGTH=$3
NUM_DUPS=$4
BIN_SIZE=$5
SEQUENCING_ERROR_RATE=$6

echo "SEQUENCING_ERROR_RATE:", $SEQUENCING_ERROR_RATE
echo $4
echo $5
echo $6
echo $7
echo $8

filename=$(basename -- "$GENOME_PATH")
extension="${filename##*.}"
filename="${filename%.*}"

GENOME_NAME=$filename

echo "GENOME_PATH:" $GENOME_PATH
echo "GENOME_NAME:" $GENOME_NAME
echo "NUM_READS" $NUM_READS
echo "READ_LENGTH" $READ_LENGTH
echo "NUM_DUPS" $NUM_DUPS
echo "BIN_SIZE" $BIN_SIZE
echo "SEQUENCING_ERROR_RATE" $SEQUENCING_ERROR_RATE


FILE_ID=${GENOME_NAME}.${BIN_SIZE}.${READ_LENGTH}.${NUM_READS}.${NUM_DUPS}.${SEQUENCING_ERROR_RATE}

echo $FILE_ID

echo "$(date) Started ${FILE_ID}.contacts.genome" >> status

if [ ! -f "${GENOME_PATH}.ann" ]; then
    bwa index ${GENOME_PATH}
fi

CHROMSIZES_FILE=/tmp/chrom.sizes

create_chrominfo.py ${GENOME_PATH} > ${CHROMSIZES_FILE}.raw
awk '{ print $1 "\t" $NF }' ${CHROMSIZES_FILE}.raw > ${CHROMSIZES_FILE}

if true; then
    gzcat ${GENOME_PATH} \
       | python scripts/generate_reads.py \
       --read-length ${READ_LENGTH} \
       --num-reads ${NUM_READS}  - \
       --sequencing-error-rate 0.02 \
       | gzip > data/${FILE_ID}.fastq.gz
    echo "$(date) Intermediate... generated reads ${FILE_ID}.contacts.genome" >> status


    bwa aln -t 4 ${GENOME_PATH} \
        data/${FILE_ID}.fastq.gz \
        | bwa samse -n ${NUM_DUPS} ${GENOME_PATH} - \
        data/${FILE_ID}.fastq.gz \
        | gzip > aligned/${FILE_ID}.sam.gz

    gzcat aligned/${FILE_ID}.sam.gz \
        | python scripts/parse_sam.py - \
        | gzip > contacts/${FILE_ID}.contacts.gz

    echo "$(date) Intermediate... parsed SAM ${FILE_ID}.contacts.genome" >> status

#workon py3

    cooler makebins \
        ${CHROMSIZES_FILE} \
      ${BIN_SIZE} -o bins/${GENOME_NAME}.${BIN_SIZE}.bins
fi

echo "Loading pairs"

cooler cload pairs \
  -c1 1 -p1 2 -c2 3 -p2 4 \
  bins/${GENOME_NAME}.${BIN_SIZE}.bins \
  contacts/${FILE_ID}.contacts.gz \
  coolers/${FILE_ID}.cool

echo "Zoomifying"

cooler zoomify coolers/${FILE_ID}.cool
