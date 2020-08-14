#! /usr/bin/env python
"""
A skeleton python script which reads from an input file,
writes to an output file and parses command line arguments
"""
from __future__ import print_function
import sys
import argparse
import os
import os.path as op
import subprocess as sp


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "ref1_fa", help="The first fasta",
    )
    parser.add_argument(
        "ref2_fa", help="The first fasta",
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
    sp.call(
        f"create_chrominfo.py {args.ref2_fa} > output/sizes2.chromsizes", shell=True,
    )
    sp.call(
        f"cat {args.ref1_fa} | python scripts/generate_reads.py \
        --read-length {args.read_length} \
        --num-reads {args.num_reads} \
        --sequencing-error-rate 0.00 - \
        | gzip > output/reads/fastq.gz",
        shell=True,
    )
    sp.call(
        f"bwa index -p output/ref2.index {args.ref2_fa}", shell=True,
    )
    sp.call(
        f"bwa aln -t 4 output/ref2.index output/reads/fastq.gz \
            | bwa samse -n {args.num_dups} output/ref2.index - \
            output/reads/fastq.gz | gzip > output/aligned.sam.gz",
        shell=True,
    )
    sp.call(
        f"gzcat output/aligned.sam.gz | python scripts/ntn_bam_to_contacts.py - \
            | gzip > output/contacts.gz",
        shell=True,
    )

    sp.call(
        """awk '{print $1 "\t" $NF }' output/sizes2.chromsizes \
            > output/sizes2.split.chromsizes""",
        shell=True,
    )

    sp.call(
        """awk '{print $1 "\t" $NF }' output/sizes1.chromsizes \
            > output/sizes1.split.chromsizes""",
        shell=True,
    )

    sp.call(
        f"cooler cload pairs -c1 1 -p1 2 -c2 4 -p2 5 \
            output/sizes1.split.chromsizes:{args.bin_size} \
            --bins2 output/sizes2.split.chromsizes:{args.bin_size} \
            output/contacts.gz output/out.cool",
        shell=True,
    )

    sp.call(
        f"cooler zoomify output/out.cool", shell=True,
    )


if __name__ == "__main__":
    main()
