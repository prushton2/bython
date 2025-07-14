"""
This is for looking at tokens
"""
import sys
import json
from tokenize import tokenize, tok_name, INDENT, DEDENT, NAME, TokenInfo
tokens = []
with open(sys.argv[1], 'rb') as tokenfile:
    tokens = list(tokenize(tokenfile.readline))
with open(sys.argv[2], 'w') as outfile:
    for i in tokens:
        outfile.write(str(i))
        outfile.write("\n")
