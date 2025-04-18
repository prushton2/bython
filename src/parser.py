import re
import os
from tokenize import tokenize, tok_name, INDENT, DEDENT, NAME, TokenInfo
from tokenize import open as topen;
"""
Python module for converting bython code to python code.
"""

def _ends_in_by(word):
    """
    Returns True if word ends in .by, else False

    Args:
        word (str):     Filename to check

    Returns:
        boolean: Whether 'word' ends with 'by' or not
    """
    return word[-3:] == ".by"


def _change_file_name(name, outputname=None):
    """
    Changes *.by filenames to *.py filenames. If filename does not end in .by, 
    it adds .py to the end.

    Args:
        name (str):         Filename to edit
        outputname (str):   Optional. Overrides result of function.

    Returns:
        str: Resulting filename with *.py at the end (unless 'outputname' is
        specified, then that is returned).
    """

    # If outputname is specified, return that
    if outputname is not None:
        return outputname

    # Otherwise, create a new name
    if _ends_in_by(name):
        return name[:-3] + ".py"

    else:
        return name + ".py"


def parse_imports(filename):
    """
    Reads the file, and scans for imports. Returns all the assumed filename
    of all the imported modules (ie, module name appended with ".by")

    Args:
        filename (str):     Path to file

    Returns:
        list of str: All imported modules, suffixed with '.by'. Ie, the name
        the imported files must have if they are bython files.
    """
    infile = open(filename, 'r')
    infile_str = ""

    for line in infile:
        infile_str += line


    imports = re.findall(r"(?<=import\s)[\w.]+(?=;|\s|$)", infile_str)
    imports2 = re.findall(r"(?<=from\s)[\w.]+(?=\s+import)", infile_str)

    imports_with_suffixes = [im + ".by" for im in imports + imports2]

    return imports_with_suffixes


def parse_file(infilepath, outfilepath, parsetruefalse,  utputname=None, change_imports=None):
    """
    Converts a bython file to a python file and writes it to disk.

    Args:
        filename (str):             Path to the bython file you want to parse.
        add_true_line (boolean):    Whether to add a line at the top of the
                                    file, adding support for C-style true/false
                                    in addition to capitalized True/False.
        filename_prefix (str):      Prefix to resulting file name (if -c or -k
                                    is not present, then the files are prefixed
                                    with a '.').
        outputname (str):           Optional. Override name of output file. If
                                    omitted it defaults to substituting '.by' to
                                    '.py'    
        change_imports (dict):      Names of imported bython modules, and their 
                                    python alternative.
    """

    infile = open(infilepath, 'r')
    outfile = open(outfilepath, 'w')
    
    tokenfile = open(infilepath, 'rb')
    tokens = list(tokenize(tokenfile.readline))

    # for i in tokens:
    #     print(i)

    tokens.pop(0) #this is the encoding scheme which i dont care about (hopefully)

    newTokens = parse_indentation(tokens)
    
    newTokens = parse_and_or(newTokens)

    if(parsetruefalse):
        newTokens = parse_true_false(newTokens)


    for(i, j) in enumerate(newTokens):
        outfile.write(j.string)
        if(j.type == 1):
            outfile.write(" ")

    infile.close()
    outfile.close()

def gen_indent(indentationLevel):
    arr = []
    for i in range(indentationLevel):
        arr.append(
            TokenInfo(
                type=5,
                string='    ',
                start=(),
                end=(),
                line=""
            )
        )
    
    return arr

def parse_indentation(tokens):
    newTokens = []
    indentationLevel = 0
    mapdepth = 0
    fstringdepth = 0

    for i, j in enumerate(tokens):
        
        # We find the start of a map. We need to set depth to 1, add the { token, and done
        if( i >= 2 and tokens[i-2].type == 1 and tokens[i-1].string == "=" and j.string == "{"):
            mapdepth = 1
            newTokens.append(j)
            continue

        # We're inside a map, so we add the token
        if(mapdepth >= 1):
            newTokens.append(j)

        # We update how deep we are in the map. If this changes, we're done 
        if( i >= 2 and mapdepth >= 1 and tokens[i].string == "{"):
            mapdepth += 1
            continue
        if( i >= 2 and mapdepth >= 1 and tokens[i].string == "}"):
            mapdepth -= 1
            continue

        # if we're inside a map, we've added the token and we have to ignore the curlies, so we're done
        if(mapdepth != 0):
            continue

        # Similar logic for fstrings: We check for entry, check if inside to push the token, and check for exit
        # Im not sure if this is the best way to do it, but it works

        if(j.type == 59):
            fstringdepth += 1
        
        if(fstringdepth >= 1):
            newTokens.append(j)
        
        if(j.type == 61):
            fstringdepth -= 1
            # newTokens.append(j)
            continue

        if(fstringdepth != 0):
            continue

        if (j.string == "{"):
            indentationLevel += 1
            newTokens.append(
                TokenInfo(
                    type=55,
                    string=":",
                    start=j.start,
                    end=j.end,
                    line=j.line
                )
            )
            newTokens.extend(gen_indent(indentationLevel))
            continue

        if(j.string == "}"):
            indentationLevel -= 1
            continue
        

        newTokens.append(j)

        if(newTokens[-1].string == "\n"):
            newTokens.extend(gen_indent(indentationLevel))
    
    return newTokens


def parse_and_or(tokens):
    # print(tokens)
    newTokens = []

    for i, j in enumerate(tokens):
        if(j.string == "&" and tokens[i+1].string == "&"):
            newTokens.append(
                TokenInfo(
                    type=1,
                    string="and",
                    start=(),
                    end=(),
                    line=""
                )
            )
            continue
        if(j.string == "&" and tokens[i-1].string == "&"):
            continue
        
        if(j.string == "|" and tokens[i+1].string == "|"):
            newTokens.append(
                TokenInfo(
                    type=1,
                    string="or",
                    start=(),
                    end=(),
                    line=""
                )
            )
            continue
        if(j.string == "|" and tokens[i-1].string == "|"):
            continue

        newTokens.append(j)
    return newTokens



def parse_true_false(tokens):
    newTokens = []

    for i, j in enumerate(tokens):
        if(j.string == "true"):
            newTokens.append(
                TokenInfo(
                    type=1,
                    string="True",
                    start=(),
                    end=(),
                    line=""
                )
            )
            continue
        
        if(j.string == "false"):
            newTokens.append(
                TokenInfo(
                    type=1,
                    string="False",
                    start=(),
                    end=(),
                    line=""
                )
            )
            continue

        newTokens.append(j)
    return newTokens
