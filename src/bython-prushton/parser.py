import re
import os
from tokenize import tokenize, tok_name, INDENT, DEDENT, NAME, NUMBER, FSTRING_START, TokenInfo
from tokenize import open as topen;
import logging

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

    tokens.pop(0) #this is the encoding scheme which i dont care about (hopefully)


    newTokens = parse_indentation(tokens)

    newTokens = parse_and_or(newTokens)

    if(parsetruefalse):
        newTokens = parse_true_false(newTokens)

    newTokens = clean_whitespace(newTokens)

    for(i, j) in enumerate(newTokens):
        if(i >= 1 and j.type in [NAME, NUMBER, FSTRING_START] and newTokens[i-1].type in [NAME, NUMBER]):
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
    nonScopeCurlyDepth = 0
    lineStartsWithScope = None

    for i, j in enumerate(tokens):
        
        if(j.string == "\n"):
            lineStartsWithScope = None

        # We check if the token string is a string that starts a scope
        # This allows for indentation, curlies, etc to not get in the way
        if(j.string in ["if", "elif", "else", "for", "while", "try", "except", "finally", "with", "def", "class"] and lineStartsWithScope == None):
            lineStartsWithScope = True
        elif(j.type == NAME and lineStartsWithScope == None): # else it doesnt start a scope
            lineStartsWithScope = False


        # If we encounter a curly after a token that starts a scope, we start a scope aswell. Else, we are in a map or smth so mark that down
        if (j.string == "{"):
            if(lineStartsWithScope):
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
            else:
                nonScopeCurlyDepth += 1
                
        # Same idea here: If our close curly isnt inside something else (map, fstring) then we dedent
        if(j.string == "}"):
            if(nonScopeCurlyDepth == 0):
                logger.debug(f"Indentation level now {indentationLevel-1} (was {indentationLevel})")
                indentationLevel -= 1
                i = -1
                prevToken = newTokens[-1]
                
                # check if the token matches either newline, a comment, or an indent
                while prevToken.type in [4,5,62,63]:
                    i -= 1
                    prevToken = newTokens[i]

                
                if(prevToken.string == ":"): # ew
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
            else:
                nonScopeCurlyDepth -= 1
        

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