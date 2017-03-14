#!/usr/bin/env python
from HTMLParser import HTMLParser
from urllib import urlopen
import argparse
import warnings
import sys
import os

# original version forked from https://github.com/inodb/biorhino-tools
# todos: query alternative server if no success on NCBI http://www.algaebase.org/search/species/detail/?species_id=32377
# todo: handle ambiguities

# key words in lower case, later match will be case insensitive
QUERY_BY_ID = "http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={tax_id}"
QUERY_BY_LITERAL = "http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?name={name}"
TAX_ID_LINE_START = '<em>taxonomy id: </em>'
TAX_ID_END = '<br'
LINEAGE_LINE = '<strong>lineage</strong>'
TOPNAME_LINE_START = '<table width="100%"><tbody>'
SPECIES_LINE = re.compile(u'<title>taxonomy browser \((\w \w\))</title>')
TOPNAME_END = '</h2>'
DEL = ';'
# Tax levels vary between organisms on the NCBI Taxonomy browser, to get the same number of columns for
# all given species this global constant is used.
TAX_LEVELS = ['no rank', 'superkingdom', 'superphylum', 'phylum', 'class', 'order', 'family', 'genus', 'species']


class NCBILineageParser(HTMLParser):
    def __init__(self):
        self.taxon_a = False
        self.taxon_lvl = None
        self.phylogeny = list()
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "title":
                    self.taxon_a = True
                    self.taxon_lvl = attr[1]

    def handle_data(self, data):
        if self.taxon_a:
            self.phylogeny.append((self.taxon_lvl, " ".join(data.split())))
            self.taxon_a = False


# todo: allow both cases topname is family, topname can be parsed as species name 
def contact_server(tax_id, name=None, print_header=False, print_table=False, print_taxid=False):
    #print('name is ' + name)
    if name is None:  #not is_name:
        filehandle = urlopen(QUERY_BY_ID.format(tax_id=tax_id))
    else:
        filehandle = urlopen(QUERY_BY_LITERAL.format(name=name).replace(' ', '+'))
        #print("request url is " + QUERY_BY_LITERAL.format(name=name).replace(' ', '+'))
        # http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?name=closterium
        #https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?name=closterium

    ctr = 0
    for line in filehandle:
        #if line.find('<table width="100%"><tbody><tr><td valign="top">') > -1:
        line = line.lower()
        if ctr > 75 and ctr < 84:
            print line
        if print_taxid and line.startswith(TAX_ID_LINE_START):
            print('ctr taxid = ' + str(ctr))
            taxid_line = line[len(TAX_ID_LINE_START):]
            sys.stdout.write(taxid_line[:taxid_line.find(TAX_ID_END)].strip() + "\t")
        elif line.startswith(TOPNAME_LINE_START):
            print('ctr topname = ' + str(ctr))
            topname_line = line[len(TOPNAME_LINE_START):]
            topname = topname_line[:topname_line.find(TOPNAME_END)].strip()
            print('topname found> ' + topname)
        elif line.find(LINEAGE_LINE) > -1: #line.startswith(LINEAGE_LINE_START):
            print('ctr lineage_line = ' + str(ctr))
            #print("found lineage line: " + line)
            nparser = NCBILineageParser()
            nparser.feed(line)

            if print_table:
                assert(len(set(TAX_LEVELS)) == len(TAX_LEVELS))

                # Print warning if each taxa does not appear only once, take
                # the one highest in the hierarchy
                # NOTE: no rank tends to appear twice, e.g. for id 290317
                taxa = [t for (t, v) in nparser.phylogeny]
                if not len(taxa) == len(set(taxa)):
                    warnings.warn("Non-unique taxa level name."
                                  "Taking highest in hierarchy. See: {taxa}"
                                  "".format(taxa=taxa))
                phyldict = dict(reversed(nparser.phylogeny))

                sys.stdout.write("\t".join(phyldict.setdefault(tl, "-") for tl in TAX_LEVELS))
                sys.stdout.write("\t" + topname + "\n")
            else:
                if print_header:
                    if print_taxid:
                        sys.stdout.write("taxonomy_id\t")
                    print("\t".join([t for (t, v) in nparser.phylogeny]) + "\ttopname")
                #topname = 'unknown topname' name = topname
                return DEL.join([v for (t, v) in nparser.phylogeny[1:]]) + DEL + name.title()
            return
        ctr += 1

    return ''
    #raise Exception('Line with lineage information not found.')

# parse family or species names from input file sheet or input args
def name_retrieval(args):
    #base_path = '/Users/troja/Data/Mueggelsee_Project/Analysis_TM/families_and_lineages'
    #f_name = 'families.txt'
    queries = set()
    
    # read names or taxids from file
    if args.file is not None:
        with open(args.file, 'r') as f:
            #print f.readline()
            for line in f.readlines():
                queries.add(line.strip())
                print line.strip()
        return sorted([query for query in queries])
    elif args.name is not None:
        return args.name
    elif args.taxids is not None:
        print args.taxids
        return args.taxids
    else:
        RaiseException('Excption raised', args)

def parse_lineages(queries, args):
    #base_path = '/Users/troja/Data/Mueggelsee_Project/Analysis_TM/families_and_lineages'
    
    #f_out = 'lineages.csv'
    unknowns = []
    count = 5
    lineages = []   # successful collected lineage strings
    unknowns = []   # names that returned unexpected query results 
    # fetch html queries for species/families
    print queries
    for name in queries[:5]:
        print('current family is ' + name)
        lineage = contact_server(0, name=name, print_header=args.header, print_table=args.table, print_taxid=args.printid)
        print lineage
        if len(lineage) < 1:
            unknowns.append(name)
        else:
            lineages.append(lineage)
            
    # write to standard output
    if args.output is None:
        print("Resolved lineages:\n")
        for lineage in lineages:
            print(lineage + "\n")
        if len(unknowns) > 0:
            print("UNRESOLVED lineages:\n")
            for name in queries:
                print(name + "\n")
            
    # write to file, assume path existing
    else:
        idx = args.output.rfind('/')
        
        base_path = args.file[:idx]
        f_out_unknown = 'lineages_unknown.txt'
        
        with open(args.output, 'w') as csv_file:
           for lineage in lineages:
                    csv_file.write(lineage + '\n')
        print("lineages written to " + args.output)
           
        with open(os.path.join(base_path, f_out_unknown), 'w') as csv_file:
            for unknown in unknowns:
                csv_file.write(unknown + '\n')
        print("unknown names written to " + os.path.join(base_path, f_out_unknown))
        
    
if __name__ == "__contact_server__":
    argparser = argparse.ArgumentParser(description="Output full linage from an NCBI Taxonomy ID in comma "
                                        "separated values. Last value is the name at the top of the page,"
                                        "usually a strain.")
    argparser.add_argument('--taxids', metavar='TaxonomyID', type=str, nargs='+',
                           help='One or more NCBI Taxonomy IDs. Can also be names if --name is supplied.')
    argparser.add_argument("--header", action="store_true", help="Print header for every record")
    argparser.add_argument("--table", action="store_true",
                           help="Print with equal number of taxonomic levels."
                           "Insert '-' if level is not available. NOTE this "
                           "does not include all possible taxonomic levels. "
                           "Prints {num} columns, i.e. {ranks}"
                           "".format(num=len(TAX_LEVELS), ranks=", ".join(TAX_LEVELS)))
                           
    argparser.add_argument("--name", action="store", help="Given ids are names")
    argparser.add_argument("--output", action="store", help="Give name for output file. Otherwise print to standard output.")
    argparser.add_argument("--file", action="store", help="Read newline separated family or species names or taxids from file.")
    
    #argparser.add_argument("--name", action="store_true", help="Given ids are names")
    argparser.add_argument("--printid", action="store_true", help="Prints Taxonomy ID as the first value")
    args = argparser.parse_args()
    print('args = ', args)

    if args.header and args.table:
        if args.printid:
            sys.stdout.write("taxonomy_id\t")
        print("\t".join(TAX_LEVELS) + "\ttopname")
    #for tid in args.tax_ids:
    names = name_retrieval(args)
    parse_lineages(names, args)
