# line display
#
import argparse

def printlines(filepath, from_line, to_line):
	with open(filepath, 'r') as f:
		i = 0
	    	for line in f:
	 		if i >= from_line and i <= to_line:
		    		print line
		    	if i > to_line:
		    		return
			i += 1


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', nargs='?',  dest='filepath', default='', type=str)
	parser.add_argument('-a', '--from', nargs='?',  dest='from_line', default=0, type=int)
	parser.add_argument('-b', '--too', nargs='?',  dest='to_line', default=10, type=int)
	args = parser.parse_args()
	if (args.filepath == ''):
		pass # print help
	else:
		printlines(args.filepath, args.from_line, args.to_line)
   
