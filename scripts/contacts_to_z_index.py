#!/usr/bin/python

import h5py 
import math
import negspy.coordinates as nc
import random
import sys
import argparse

#convert (x,y) to d
def xy2d (n, x, y):
    d=0;
    s = n // 2
    while s > 0:
        rx = (x & s) > 0
        ry = (y & s) > 0
        d += s * s * ((3 * rx) ^ ry);
        (x,y) = rot(s, x, y, rx, ry);
        s = s // 2

    return d;

#convert d to (x,y)
def d2xy(n, d):
    t=d;
    x = y = 0;
    s = 1
    while s < n:
        rx = 1 & (t//2);
        ry = 1 & (t ^ rx);
        (x,y) = rot(s, x, y, rx, ry);

        x += s * rx;
        y += s * ry;
        t = t // 4
        s *= 2
    return (x,y)

#rotate/flip a quadrant appropriately
def rot(n, x, y, rx, ry):
    if (ry == 0):
        if (rx == 1):
            x = n-1 - x;
            y = n-1 - y;

        #Swap x and y
        return (y,x)

    return (x,y)

def test(num):
    import random
    import contacts_to_z_index as ctz
    #x = int(random.randint(0, num-1))
    #y = int(random.randint(0, num-1))
    x = 3885975424
    y = 1516636338 
    d = ctz.xy2d(num, x, y)
    (nx,ny) = ctz.d2xy(num, d)
    print("num:", num, "x:", x, "y:", y, "d:", d, "nx:", nx, "ny:", ny)
    assert((x,y) == (nx,ny))

def main():
    parser = argparse.ArgumentParser(description="""
    
    python contacts_to_z_index.py file.contacts
""")

    parser.add_argument('input_file')
    parser.add_argument('from_assembly')
    parser.add_argument('to_assembly')
    parser.add_argument('--tile-resolution', default=256)
    parser.add_argument('--bin-size', default=256)
    #parser.add_argument('-o', '--options', default='yo',
    #					 help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')

    args = parser.parse_args()

    from_chrominfo = nc.get_chrominfo(args.from_assembly)
    to_chrominfo = nc.get_chrominfo(args.to_assembly)
    
    print("from_chrominfo", from_chrominfo.total_length)
    axis_length = max(from_chrominfo.total_length, to_chrominfo.total_length)
    print("axis_length:", axis_length)

    max_zoom = math.ceil(math.log(axis_length / (args.tile_resolution * args.bin_size)) / math.log(2))
    max_width = args.tile_resolution * args.bin_size * 2 ** max_zoom
    z_index_width = max_width // args.bin_size

    if args.input_file == '-':
        f = sys.stdin
    else:
        f = open(args.input_file, 'r')

    fout = h5py.File('/tmp/out.h5py', 'w')
    dset = fout.create_dataset('default', (max_width,max_width), compression='gzip')

    print("max_zoom:", max_zoom, max_width)
    for line in f:
        parts = line.strip().split()
        chr1 = parts[0]
        pos1 = int(parts[1])
        chr2 = parts[2]
        pos2 = int(parts[3])

        genome_pos1 = nc.chr_pos_to_genome_pos(chr1, pos1, args.from_assembly)
        genome_pos2 = nc.chr_pos_to_genome_pos(chr2, pos2, args.to_assembly)

        dset[genome_pos1][genome_pos2] += 1
        #d = xy2d(max_width, genome_pos1, genome_pos2 // args.bin_size)

        #assert(x == int(genome_pos1))
        #assert(y == int(genome_pos2))

if __name__ == '__main__':
    main()


