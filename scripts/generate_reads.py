#!/usr/bin/python

import Bio.SeqIO as bsio
import gzip
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
    parser.add_argument('--num-reads', default=100, type=int)
    #parser.add_argument('-o', '--options', default='yo',
    #					 help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')

    args = parser.parse_args()

    if args.fasta_file == '-':
        f = sys.stdin
    else:
        f = open(args.fasta_file, 'r')

    fseq = bsio.parse(f, 'fasta')
    records = list(fseq)
    total_length = sum([len(r.seq) for r in records])

    #print("total_length:", total_length)
    #print("num_reads:", args.num_reads)

    for record in records:
        #print("record:", record)
        #print("record:", record, "to_count:", args.num_reads * len(record.seq) / total_length)
        for i in range(int(args.num_reads * len(record.seq) / total_length)):
            #print("i:", i)
            chr_length = len(record.seq)
            read_start = random.randint(0, chr_length - args.read_length)
            strand = ['+','-'][random.randint(0,1)]
            read_id = record.id.split()[0] + '_' + strand + "_" + str(read_start+1)  #one-based reads
            read = record.seq[read_start:read_start + args.read_length]
            print('@' + read_id)
            print(read)
            print('+')
            print(''.join(['I' for i in range(args.read_length)])) # quality scores

if __name__ == '__main__':
    main()


