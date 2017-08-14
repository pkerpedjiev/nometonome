COMMAND="./run.sh FROM_GENOME TO_GENOME NUM_READS READ_LENGTH NUM_DUPS BIN_SIZE"

trap "exit" INT

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

if [[ -z "$5" ]]; then
    echo "NUM_DUPS not provided"
    echo "$COMMAND"
    exit
fi

if [[ -z "$6" ]]; then
    echo "BIN_SIZE not provided"
    echo "$COMMAND"
    exit
fi

if [[ -z "&7" ]]; then
    echo "SEQUENCING_ERROR_RATE not provided"
    echo "$COMMAND"
    exit
fi

FROM_GENOME=$1
TO_GENOME=$2
NUM_READS=$3
READ_LENGTH=$4
NUM_DUPS=$5
BIN_SIZE=$6
SEQUENCING_ERROR_RATE=$7

echo "FROM_GENOME:" $FROM_GENOME
echo "TO_GENOME" $TO_GENOME
echo "NUM_READS" $NUM_READS
echo "READ_LENGTH" $READ_LENGTH
echo "NUM_DUPS" $NUM_DUPS
echo "BIN_SIZE" $BIN_SIZE
echo "SEQUENCING_ERROR_RATE" $SEQUENCING_ERROR_RATE


FILE_ID=${FROM_GENOME}.${TO_GENOME}.${READ_LENGTH}.${NUM_READS}.${NUM_DUPS}.${SEQUENCING_ERROR_RATE}

echo $FILE_ID

echo "$(date) Started ${FILE_ID}.contacts.genome" >> status

gzcat ~/data/genomes/${FROM_GENOME}.fa.gz \
   | python scripts/generate_reads.py \
   --read-length ${READ_LENGTH} \
   --num-reads ${NUM_READS}  - \
   | gzip > data/${FILE_ID}.fastq.gz
echo "$(date) Intermediate... generated reads ${FILE_ID}.contacts.genome" >> status

bwa aln -t 4 ~/data/genomes/${TO_GENOME}.fa.gz \
    data/${FILE_ID}.fastq.gz \
    | bwa samse -n ${NUM_DUPS} ~/data/genomes/${FROM_GENOME}.fa.gz - \
    data/${FILE_ID}.fastq.gz \
    | gzip > aligned/${FILE_ID}.sam.gz

gzcat aligned/${FILE_ID}.sam.gz \
    | python scripts/parse_sam.py - \
    ${FROM_GENOME} ${TO_GENOME} \
    | gzip > contacts/${FILE_ID}.contacts.gz

echo "$(date) Intermediate... parsed SAM ${FILE_ID}.contacts.genome" >> status

#workon py3

cooler makebins \
  ~/projects/negspy/negspy/data/${FROM_GENOME}/chromInfo.txt \
  ${BIN_SIZE} -o bins/${FROM_GENOME}.${BIN_SIZE}.bins

cooler csort --nproc 4 -c1 1 -p1 2 -s1 3 \
  -c2 4 -p2 5 -s2 6 \
  contacts/${FILE_ID}.contacts.gz \
  ~/projects/negspy/negspy/data/${FROM_GENOME}/chromInfo.txt \
  -o contacts/${FILE_ID}.contacts.sorted

cooler cload pairix \
  bins/${FROM_GENOME}.${BIN_SIZE}.bins \
  contacts/${FILE_ID}.contacts.sorted \
  coolers/${FILE_ID}.cool

cooler zoomify coolers/${FILE_ID}.cool --no-balance
