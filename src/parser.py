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


def parse_file(infilepath, outfilepath, add_true_line,  utputname=None, change_imports=None):
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

    #filename = os.path.basename(filepath)
    #filedir = os.path.dirname(filepath)
    
    infile = open(infilepath, 'r')
    outfile = open(outfilepath, 'w')
    
    indentation_level = 0
    indentation_sign = "    "
    current_line = ""
    
    if add_true_line:
        outfile.write("true=True; false=False; null=None\n")
    
    tokenfile = open(infilepath, 'rb')
    tokens = list(tokenize(tokenfile.readline))

    tokens.pop(0)

    newTokens = parse_indentation(tokens)
    
    newTokens = parse_and_or(newTokens)

    # some control variables to make sure we dont parse content in fstrings and dict definitions
     
    # inside_fstring = False
    # dict_layer = 0
    
    # for i, j in enumerate(tokens):
        #print(j) #61 and 63
        #write line with indentation
        
        # if(j.type == 61):
        #     inside_fstring = True
        # elif(j.type == 63):
        #     inside_fstring = False
        
        # if(i >= 2 and tokens[i-2].type == 1 and tokens[i-1].string == '=' and j.string == '{'):
        #     dict_layer = 1
        #     # current_line += j.string

        # elif(dict_layer >= 1 and tokens[i].string == '{'):
        #     dict_layer += 1
        #     # current_line += j.string


        # elif(dict_layer >= 1 and tokens[i].string == '}'):
        #     dict_layer -= 1
        #     if(dict_layer == 0):
        #         current_line += j.string

        
        # if(inside_fstring or dict_layer >= 1): # No processing should be done inside an fstring
        #     # print(j.string)
        #     current_line += j.string
        #     continue
    
        # if j.string == "{":
        #     indentation_level += 1
        #     current_line += ":"
        # elif j.string == "}":
        #     indentation_level -= 1
        #     outfile.write(current_line + "\n");
        #     current_line = indentation_level * indentation_sign
    
        #check for && and replace with and
        # elif j.string == "&" and tokens[i+1].string == "&":
        #     current_line += " and "
        
        # elif j.string == "&" and tokens[i-1].string == "&":
        #     continue
    
        # #check for || and replace with or
        # elif j.string == "|" and tokens[i+1].string == "|":
        #     current_line += " or "
        # elif j.string == "|" and tokens[i-1].string == "|":
        #     continue
    
        # else:
        #     current_line += j.string
    
    
        #adds a space after NAME tokens, so def main doesnt become defmain
        # if j.type == 1:
        #     current_line += " "
        # #on a newline, write the current line and restart
        # if j.string == "\n":
        #     outfile.write(current_line)
        #     current_line = indentation_level * indentation_sign
    for(i, j) in enumerate(newTokens):
        # print(j)
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
