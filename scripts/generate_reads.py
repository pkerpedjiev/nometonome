from __future__ import print_function
#!/usr/bin/python

import Bio.SeqIO as bsio
import gzip
import humanfriendly
import numpy as np
import random
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="""
    
    python generate_reads.py fasta_file.fa

    Generate a set of short reads to be aligned to a reference genome
    using a short read mapper.
""")

    #parser.add_argument('argument', nargs=1)
    parser.add_argument('fasta_file')
    parser.add_argument('--read-length', default=22, type=int)
    parser.add_argument('--num-reads', default=100, type=str)
    parser.add_argument('--sequencing-error-rate', default=0, type=float)
    #parser.add_argument('-o', '--options', default='yo',
    #					 help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')

    args = parser.parse_args()

    if args.fasta_file == '-':
        f = sys.stdin
    else:
        f = open(args.fasta_file, 'r')

    num_reads = humanfriendly.parse_size(args.num_reads)

    print("num_reads:", num_reads, file=sys.stderr)

    fseq = bsio.parse(f, 'fasta')
    records = list(fseq)
    total_length = sum([len(r.seq) for r in records])
    #print("records:", records, file=sys.stderr)

    #print("total_length:", total_length)
    #print("num_reads:", args.num_reads)

    for record in records:
        #print("record:", record)
        #print("record:", record, "to_count:", args.num_reads * len(record.seq) / total_length)
        num_reads_to_sample = int(num_reads * len(record.seq) / total_length)
        #print("num_reads_to_sample:", num_reads_to_sample, file=sys.stderr)

        chr_length = len(record.seq)
        start_positions = [int(i) for i in np.linspace(0, chr_length - args.read_length, num_reads_to_sample)]
        strand = '+'

        #print("start_positions:", start_positions, file=sys.stderr)

        for read_start in start_positions:
            strand = ['+','-'][random.randint(0,1)]
            read_id = record.id.split()[0] + '_' + strand + "_" + str(read_start+1)  #one-based reads
            read = record.seq[read_start:read_start + args.read_length]
            #print("read:", read, file=sys.stderr)

            if args.sequencing_error_rate and args.sequencing_error_rate > 0:
                read = "".join([r if random.random() > args.sequencing_error_rate else random.choice(['A','C','G','U']) for r in read])

            if read.find('N') >= 0:
                continue

            #print("read1:", read)
            print('@' + read_id)
            print(read)
            print('+')
            print(''.join(['I' for i in range(args.read_length)])) # quality scores

if __name__ == '__main__':
    main()


