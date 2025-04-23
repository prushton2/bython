import re
import os
from tokenize import tokenize, tok_name, INDENT, DEDENT, NAME, TokenInfo
from tokenize import open as topen;
import logging

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

    newTokens = clean_whitespace(newTokens)

    for(i, j) in enumerate(newTokens):
        if(i >= 1 and j.type == 1 and newTokens[i-1].type == 1):
            outfile.write(" ")
        outfile.write(j.string)

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
    logger = logging.getLogger()
    newTokens = []
    indentationLevel = 0
    mapdepth = 0
    fstringdepth = 0

    for i, j in enumerate(tokens):
        
        # We find the start of a map. We need to set depth to 1, add the { token, and done
        if( i >= 2 and tokens[i-2].type == 1 and tokens[i-1].string == "=" and j.string == "{"):
            mapdepth = 1
            newTokens.append(j)
            logger.debug("Entered map")
            continue

        # We're inside a map, so we add the token
        if(mapdepth >= 1):
            newTokens.append(j)

        # We update how deep we are in the map. If this changes, we're done 
        if( i >= 2 and mapdepth >= 1 and tokens[i].string == "{"):
            mapdepth += 1
            logger.debug(f"Map depth {mapdepth}")
            continue
        if( i >= 2 and mapdepth >= 1 and tokens[i].string == "}"):
            mapdepth -= 1
            logger.debug(f"Map depth {mapdepth}")
            continue

        # if we're inside a map, we've added the token and we have to ignore the curlies, so we're done
        if(mapdepth != 0):
            continue

        # Similar logic for fstrings: We check for entry, check if inside to push the token, and check for exit
        # Im not sure if this is the best way to do it, but it works

        if(j.type == 59):
            fstringdepth += 1
            logger.debug(f"fstring depth {fstringdepth}")
            
        
        if(fstringdepth >= 1):
            newTokens.append(j)
        
        if(j.type == 61):
            fstringdepth -= 1
            logger.debug(f"fstring depth {fstringdepth}")
            continue

        if(fstringdepth != 0):
            continue

        if (j.string == "{"):
            logger.debug(f"Indentation level now {indentationLevel+1} (was {indentationLevel})")
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
            continue

        if(j.string == "}"):
            logger.debug(f"Indentation level now {indentationLevel-1} (was {indentationLevel})")
            indentationLevel -= 1
            i = -1
            prevToken = newTokens[-1]
            
            while prevToken.type in [4,5,63]:
                i -= 1
                prevToken = newTokens[i]

            
            if(prevToken.string == ":"):
                logger.debug(f"Found empty block, inserted pass")
                newTokens.append(
                    TokenInfo(
                        type=1,
                        string="pass",
                        start=(),
                        end=(),
                        line=""
                    )
                )
            newTokens.append(
                TokenInfo(
                    type=4,
                    string="\n",
                    start=(),
                    end=(),
                    line=""
                )
            )
            newTokens.extend(gen_indent(indentationLevel))
            continue
        

        newTokens.append(j)

        if(newTokens[-1].string == "\n"):
            logger.debug(f"Newline")
            newTokens.extend(gen_indent(indentationLevel))
    
    return newTokens


def parse_and_or(tokens):
    logger = logging.getLogger()
    newTokens = []

    for i, j in enumerate(tokens):
        if(j.string == "&" and tokens[i+1].string == "&"):
            logger.debug(f"Converted && to and")
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
            logger.debug(f"Skipped &&")
            continue
        
        if(j.string == "|" and tokens[i+1].string == "|"):
            logger.debug(f"Converted || to or")
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
            logger.debug(f"Skipped ||")
            continue

        newTokens.append(j)
    return newTokens



def parse_true_false(tokens):
    logger = logging.getLogger()
    newTokens = []

    for i, j in enumerate(tokens):
        if(j.string == "true"):
            logger.debug(f"converted true to True")
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
            logger.debug(f"converted false to False")
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
        
        if(j.string == "null"):
            logger.debug(f"converted null to None")
            newTokens.append(
                TokenInfo(
                    type=1,
                    string="None",
                    start=(),
                    end=(),
                    line=""
                )
            )
            continue

        newTokens.append(j)
    return newTokens


def clean_whitespace(tokens):
    logger = logging.getLogger()

    current_line = []
    newTokens = []
    contains_real_tokens = False

    for i, j in enumerate(tokens):
        current_line.append(j)

        if(not (j.type in [4, 5, 63])):
            contains_real_tokens = True

        if(j.string == "\n"):
            logger.debug(f"Newline (append tokens: {contains_real_tokens}, token info: {[token.string for token in current_line]})")
            if(contains_real_tokens):
                newTokens.extend(current_line)
            current_line = []
            contains_real_tokens = False

    return newTokens