#!/usr/bin/python

import negspy.coordinates as nc
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="""
    
    python create_offset_chromsizes.py chromsizes1 chromsizes2

    Recreate the second chromosome sizes as if they were offset from
    the origin of the first.
""")


    parser.add_argument('chrominfo1')
    parser.add_argument('chrominfo2')

    #parser.add_argument('argument', nargs=1)
    #parser.add_argument('-o', '--options', default='yo',
    #					 help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')

    args = parser.parse_args()

    chrom_info1 = nc.get_chrominfo_from_file(args.chrominfo1)
    chrom_info2 = nc.get_chrominfo_from_file(args.chrominfo2)


    total_length = sum([chrom_info1.chrom_lengths[c] for c in chrom_info1.chrom_order])

    for c in chrom_info2.chrom_order:
        print("{}\t{}".format(c, chrom_info2.chrom_lengths[c] + total_length))
    

if __name__ == '__main__':
    main()


