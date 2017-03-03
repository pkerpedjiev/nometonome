#!/usr/bin/python

import collections as col
import h5py 
import negspy.coordinates as nc
import math
import sys
import argparse

def num_to_bytes(num, num_bytes):
    '''
    Break up a number into num_bytes bytes.

    Args:

    num (unsigned int): Any number
    num_bytes (unsigned int): The number of bytes to break the number up into

    Returns:

    array: The bytes used to represent this number
    '''
    b = []
    while num_bytes:
        b += [num & 255]
        num = num >> 8

        num_bytes -= 1
    return b[::-1]
        

def main():
    parser = argparse.ArgumentParser(description="""
    
    python z_index_to_aggregated_hdf5.py z-index-file  from-assembly to-assembly

    Input file:

    123123  1
""")

    parser.add_argument('input_file')
    parser.add_argument('from_assembly')
    parser.add_argument('to_assembly')

    #parser.add_argument('-o', '--options', default='yo',
    #					 help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')

    args = parser.parse_args()

    parser.add_argument('--tile-resolution', default=256)
    parser.add_argument('--bin-size', default=256)
    parser.add_argument('--output-file', default='/tmp/out.hdf5')
    #parser.add_argument('-o', '--options', default='yo',
    #					 help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')

    args = parser.parse_args()

    from_chrominfo = nc.get_chrominfo(args.from_assembly)
    to_chrominfo = nc.get_chrominfo(args.to_assembly)
    
    #print("from_chrominfo", from_chrominfo.total_length)
    axis_length = max(from_chrominfo.total_length, to_chrominfo.total_length)
    #print("axis_length:", axis_length)

    max_zoom = math.ceil(math.log(axis_length / (args.tile_resolution * args.bin_size)) / math.log(2))
    max_width = args.tile_resolution * args.bin_size * 2 ** max_zoom
    z_index_width = max_width // args.bin_size

    if args.input_file == '-':
        f = sys.stdin
    else:
        f = open(args.input_file, 'r')

    #  the number of bytes used to represent the z-indeces
    num_bytes = 16

    data_buffers = [[] for i in range(max_zoom+1)]
    byte_buffers = [[[] for i in range(num_bytes)] for j in range(max_zoom+1)]


    # the output hdf file will have groups for each zoom level
    f_out = h5py.File(args.output_file, 'w')
    groups = [f_out.create_group('zoom_{}'.format(i)) for i in range(max_zoom+1)]

    meta = f_out.create_dataset('meta', (1,), dtype='f')

    meta.attrs['max-width'] = max_width
    meta.attrs['max-zoom'] = max_zoom

    # the datasets containing the z-index bytes and values
    dsets = col.defaultdict(dict) 

    # the data will be stored in columns for the bytes for the z index and 
    # a column for the values
    for i in range(max_zoom+1):
        for j in range(num_bytes):
            dsets[i]['bytes_' + str(j)] = groups[i].create_dataset('bytes_' + str(j), (2 ** (max_zoom - i),), dtype='uint8', compression='gzip')
        dsets[i]['values'] = groups[i].create_dataset('values', (2 ** (max_zoom - i),), dtype='float', compression='gzip')

    for line in f:
        parts = line.strip().split()
        print("parts:", parts)
        zindex = int(parts[0])
        value = int(parts[1])

        zindex_bytes = num_to_bytes(zindex, num_bytes)

        curr_zoom = max_zoom
        done = False

        while curr_zoom >= 0 and not done:
            if len(data_buffers[curr_zoom]) > 0 and data_buffers[curr_zoom][-1][0] == zindex:
                # we've already encountered this index so we have to add the current value to it
                data_buffers[curr_zoom][-1][1] += value
                done = True
            else:
                data_buffers[curr_zoom] += [[zindex, value]]

            zindex = zindex // 4
            curr_zoom -= 1

        for i,b in enumerate(zindex_bytes):
            byte_buffers[max_zoom][i] += [b]

    print("data_buffers:", data_buffers[0])

    for i in range(num_bytes):
        dsets[max_zoom]['bytes_' + str(i)] = byte_buffers[max_zoom][i]

    dsets[max_zoom]['values'] = [d[1] for d in data_buffers[max_zoom]]
    print("values:", dsets[max_zoom]['values'])

if __name__ == '__main__':
    main()


