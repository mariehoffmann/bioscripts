'''
	Split file containing multiple FASTA genomes into separate files.
	Header line will form new file name. Default output directory is current directory.
'''

import argparse
import os
import sys

def split(filename, output_dir):
	rx = r'>(.)'
	current_file = None
	with open(str(filename),'r') as f:
		for line in f.readlines():
			if (line.startswith(">")):
				pos = line.rfind('|')
				filename_new = os.path.join(output_dir, line[1:pos].rstrip() + '.fasta')
				print "pos = " + str(pos) + ", filename = " + filename_new
				if (current_file is not None):
					current_file.close()
				print "writing to current_file = " + filename_new
				current_file = open(filename_new, 'w')
			else:
				current_file.write(line)


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Split file of multiple FASTA genomes into separate files.')
	parser.add_argument('filename', type=str, help='give file name')
	parser.add_argument('-o', dest='output_dir', type=str, default='.', help='give output directory')
	args = parser.parse_args()
	if os.path.isfile(str(args.filename)) is False:
		print('input file does not exist: ' + str(args.filename))
		sys.exit(0)
	if os.path.isdir(args.output_dir) is False:
		print('output directory does not exist: ' + args.output_dir)
		sys.exit(0)
	split(args.filename, args.output_dir)
    
