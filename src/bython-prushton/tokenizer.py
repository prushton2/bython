import sys
from tokenize import tokenize, tok_name, INDENT, DEDENT, NAME, TokenInfo
tokenfile = open(sys.argv[0], 'rb')
tokens = list(tokenize(tokenfile.readline))
print(tokens)