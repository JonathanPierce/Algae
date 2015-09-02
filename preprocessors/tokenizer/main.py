# -*- coding: utf-8 -*-

import sys
import tokenizer
import os
import re
import helpers.io as io

# just tokenizes the file
def simple(filepath):
    tok = tokenizer.Tokenizer(filepath)
    results = tok.full_tokenize()
    return " ".join(results)

# smartly tokenizes a function for modified token edit distance (MTED)
# tokenPath is the entry point (potentially a main file, if C++ templates are used)
# sources is an array of all of the paths we are actually interested in.
# If compres sis true, each token will be reduced to a single character. Good for edit distance!
def mted(tokenPath, sources, compress):
    tok = tokenizer.Tokenizer(tokenPath)
    functions = tok.split_functions(False)
    
    # sort them appropriately
    def comp(a,b):
        lena = len(a[1])
        lenb = len(b[1])
        if lena == lenb:
            # if lengths are tied, sort alphabetically based on function name
            if a[0] < b[0]:
                return -1
            else:
                return 1
        else:
            return lena - lenb
            
    functions.sort(comp)
    
    # compress and output
    results = ""
    for funct in functions:
        if funct[2] in sources:
            if compress:
                results += tokenizer.compress_tokens(funct[1])
            else:
                results += " ".join(funct[1])
    
    # return results
    return results