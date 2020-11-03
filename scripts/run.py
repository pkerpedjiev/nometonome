#! /usr/bin/env python
"""
A skeleton python script which reads from an input file,
writes to an output file and parses command line arguments
"""
from __future__ import print_function

import argparse
import os
import os.path as op
import subprocess as sp
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "ref1_fa", help="The first fasta",
    )

    parser.add_argument("--bin-size", default=10000)
    parser.add_argument("--num-reads", default=5000)
    parser.add_argument("--read-length", default=32)
    parser.add_argument("--num-dups", default=100)

    args = parser.parse_args()

    cwd = os.getcwd()

    try:
        os.makedirs("output/reads")
    except Exception:
        pass

    sp.call(
        f"create_chrominfo.py {args.ref1_fa} > output/sizes1.chromsizes", shell=True,
    )

    cmd = f"cat {args.ref1_fa} | python scripts/generate_reads.py \
        --read-length {args.read_length} \
        --num-reads {args.num_reads} \
        --sequencing-error-rate 0.00 - \
        | gzip > output/reads/fastq.gz"
    sp.call(cmd,
        shell=True,
    )

    
    print("running minimap2")
    sp.call(
        f"minimap2 -ax map-pb -P {args.ref1_fa} output/reads/fastq.gz |  gzip > output/aligned.sam.gz",
        shell=True,
    )
    

    sp.call(
        f"gzcat output/aligned.sam.gz | python scripts/ntn_bam_to_contacts.py - \
            --read-length {args.read_length} \
            | gzip > output/contacts.gz",
        shell=True,
    )

    sp.call(
        """awk '{print $1 "\t" $NF }' output/sizes1.chromsizes \
            > output/sizes1.split.chromsizes""",
        shell=True,
    )

    cmd = f"gzcat output/contacts.gz | cooler cload pairs -c1 1 -p1 2 -c2 4 -p2 5 \
            --field count=7:agg=mean,dtype=float \
            --chunksize 50000000000 \
            output/sizes1.split.chromsizes:{args.bin_size} \
            - output/out.cool"
    print("cmd:", cmd)

    sp.call(
        cmd,
        shell=True,
    )

    sp.call(
        f"cooler zoomify --field count:agg=mean,dtype=float output/out.cool", shell=True,
    )


if __name__ == "__main__":
    main()
