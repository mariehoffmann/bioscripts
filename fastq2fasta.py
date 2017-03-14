from __future__ import print_function

__author__ = 'Marie Hoffmann ozymandiaz147@googlemail.com'

import re
import os
import argparse
import sys

import config

def handle_args():
    usage = ""
    usage += "Preprocessing Tool"
    parser = argparse.ArgumentParser(description = usage )
    parser.add_argument('-fastq_dir', dest='fastq_dir', default=config.fastq_dir, help='Path to folder containing FASTQ file [fastq]')
    parser.add_argument('-tmp_dir', dest='tmp_dir', default=config.tmp_dir, help='Path to temporary folder containing FASTA files and output')
    args = parser.parse_args(sys.argv[1:])
    return args

'''
    assume no newlines, no seq id after '+'
    reduce to fasta format and split into multiple files if necessary
    trim modes:     "all"    seq -> seq[left:right]
                    "indiv"  seq -> seq[seq.find(qual >= left):seq.rfind(qual >= right)]
'''
def fastq2fasta(path_in, basepath_out, file_regex, line_max=10000, trim_mode={"mode": "all", "left": 5, "right": 425}):
    file_regex = re.compile(file_regex)
    outdirs = {}
    for filename in os.listdir(path_in):
        mo = file_regex.match(filename)
        if mo is None:
            continue
        print("found matching file: ", filename)
        file_out_list = [filename.replace(".fastq", ".fasta")]
        line_ctr = 0
        # create subdirs for splitted files
        delim_pos1 = filename.find("_")
        delim_pos2 = filename.find("_", delim_pos1+1)
        path_out = os.path.join(basepath_out, filename[:delim_pos1].upper(), filename[delim_pos1+1:delim_pos2])
        if not os.path.isdir(path_out):
            os.makedirs(path_out)
        else:
            print("Output path already exists, files may be overwritten! Output path = ", path_out)
        f_out = open(os.path.join(path_out, file_out_list[-1]), "w")
        with open(os.path.join(path_in, filename), "r") as f_in:
            while True:
                id = f_in.readline()
                seq = f_in.readline()
                if not seq:
                    break
                if trim_mode["mode"] == "all":
                    f_out.writelines([">"+id[1:], seq[trim_mode["left"]:trim_mode["right"]]])
                line_ctr += 2
                delim = f_in.readline()
                if not delim.rstrip("\n") == "+":
                    print("Error: expected delimiter line, got ", delim)
                    break
                qual = f_in.readline()
                # start new file
                if line_ctr >= line_max:
                    f_out.close()
                    file_out_list.append(file_out_list[0].replace(".fasta", "_part" + str(len(file_out_list)+1) + ".fasta"))
                    f_out = open(os.path.join(path_out, file_out_list[-1]), "w")
                    line_ctr = 0
        outdirs[path_out] = file_out_list
        print("output directory: ", path_out)
        print("output files: ", str(file_out_list))
    return outdirs


if __name__ == '__main__':
    fastq2fasta(config.fastq_dir, config.tmp_dir, "Diatom_S\d+_L001.assembled.fastq", 10000)
