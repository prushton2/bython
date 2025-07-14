import re
import os
from tokenize import tokenize, tok_name, TokenInfo, INDENT, DEDENT, NAME, NUMBER, FSTRING_START, FSTRING_END, NEWLINE, COMMENT, NL, OP

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
                type=INDENT,
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
    atLineStart = True
    state = "Searching"

    # States:
    # Searching: Find a statement that defines a block (if, else, ...) but only at the start of a line
    # Find Curly: Find the curly brace associated with the statement

    for i, j in enumerate(tokens):

        if(len(newTokens) >= 1 and newTokens[-1].string == "\n"):
            logger.debug(f"Newline")
            newTokens.extend(gen_indent(indentationLevel))
            # atLineStart = True
        
        if(j.type == FSTRING_START):
            nonScopeCurlyDepth += 1
            newTokens.append(j)
            continue

        elif(j.type == FSTRING_END):
            nonScopeCurlyDepth -= 1
            newTokens.append(j)
            continue


        if(state == "Searching"):

            # Do we meet conditions for the next state?
            if(j.string in ["if", "elif", "else", "for", "while", "try", "except", "finally", "with", "def", "class"] and 
               (len(newTokens) == 0 or newTokens[-1].type in [OP, INDENT, DEDENT, NEWLINE, NL])):
                state = "Find Curly"
                newTokens.append(j)
            
            # This is for curlies part of scopes. We pretty much just delete them.
            elif(j.string == "}" and nonScopeCurlyDepth == 0):
                indentationLevel -= 1

                # If the previous token is an indent, we delete it. This turns `\t\t} else {` into `\telse:` instead of `\t\telse:`, which wouldnt work.
                if(newTokens[-1].type in [INDENT, DEDENT]):
                    newTokens.pop()

                # This is for inserting pass. We just crawl back and find the first real token or :
                i = len(newTokens)-1
                prevToken = newTokens[i]
                while prevToken.type in [NEWLINE, INDENT, COMMENT, NL]:
                    i -= 1
                    prevToken = newTokens[i]

                # If we hit the colon, its an empty block so we insert a pass 
                if(prevToken.string == ":"):
                    logger.debug(f"Found empty block, inserted pass")
                    newTokens.insert(i+1,
                        TokenInfo(
                            type=NAME,
                            string="pass",
                            start=(),
                            end=(),
                            line=""
                        )
                    )
                # Append a newline for good measure (empty lines are removed later)
                newTokens.insert(i+2,
                    TokenInfo(
                        type=NEWLINE,
                        string="\n",
                        start=(),
                        end=(),
                        line=""
                    )
                )

            # This catches curlies present in maps/dicts because we arent in the find curly state, and we just increment/decrement NSCD to ignore them
            elif(j.string == "{"):
                nonScopeCurlyDepth += 1
                newTokens.append(j)

            elif(j.string == "}" and nonScopeCurlyDepth != 0):
                nonScopeCurlyDepth -= 1
                newTokens.append(j)

            else:
                newTokens.append(j)

        elif(state == "Find Curly"):
            if(j.string == "{" and nonScopeCurlyDepth == 0):

                # Backtrack and delete tokens up to the previous block so that `def main()\n\t{\n` becomes `def main():\n` instead of `def main()\n\t:\n`
                while(newTokens[-1].type in [INDENT, DEDENT, NL, NEWLINE]):
                    newTokens.pop()

                newTokens.append(
                    TokenInfo(
                        type=OP,
                        string=":",
                        start=j.start,
                        end=j.end,
                        line=j.line
                    )
                )
                indentationLevel += 1
                state = "Searching"
            else:
                newTokens.append(j)

    return newTokens



def parse_indentation2(tokens):
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
                        type=OP,
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

                # One case we have to watch for is empty scopes. These need a pass statement to parse in python, so we crawl backwards to check if we need a pass statement
                i = -1
                prevToken = newTokens[-1]
                
                # crawl backwards while token matches either newline, a comment, or an indent
                while prevToken.type in [NEWLINE, INDENT, COMMENT, NL]:
                    i -= 1
                    prevToken = newTokens[i]

                # If we hit the colon, its an empty block so we insert a pass 
                if(prevToken.string == ":"):
                    logger.debug(f"Found empty block, inserted pass")
                    newTokens.append(
                        TokenInfo(
                            type=NAME,
                            string="pass",
                            start=(),
                            end=(),
                            line=""
                        )
                    )
                # Append a newline for good measure (empty lines are removed later)
                newTokens.append(
                    TokenInfo(
                        type=NEWLINE,
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
                    type=NAME,
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
                    type=NAME,
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
                    type=NAME,
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
                    type=NAME,
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
                    type=NAME,
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