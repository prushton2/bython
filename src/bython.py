#! /usr/bin/env python3
import argparse
import os
import sys
import shutil
import subprocess
import logging

from pathlib import Path
import parser

VERSION_NUMBER = "1.1.1"
logging.basicConfig(format='%(funcName)s: %(message)s')
logger = logging.getLogger()

"""
Bython is Python with braces.

This is a command-line utility to translate and run bython files.

Flags and arguments:
    -V, --version:      Print version number
    -v, --verbose:      Print progress
    -c, --compile:      Translate to python file and store; do not run
    -k, --keep:         Keep generated python files
    -t, --lower_true:   Adds support for lower case true/false
    -2, --python2:      Use python2 instead of python3
    -o, --output:       Specify name of output file (if -c is present)
    input,              Bython files to process
    args,               Arguments to script
"""

def main():
    # Setup argument parser
    argparser = argparse.ArgumentParser("bython", 
        description="Bython is a python preprosessor that translates braces into indentation", 
        formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument("-V", "--version", 
        action="version", 
        version="Bython v{}\nRewritten by Peter Rushton\nOriginally by Mathias Lohne and Tristan Pepin 2018\n".format(VERSION_NUMBER))
    argparser.add_argument("-v", "--verbose", 
        type=str,
        help="Specify a verbosity level for debugging (debug, info, warning, error, critical)",
        nargs=1) 
    argparser.add_argument("-c", "--compile", 
        help="translate to python only (don't run files)",
        action="store_true")
    argparser.add_argument("-t", "--truefalse",
        help="adds support for lower case true/false, aswell as null for None",
        action="store_true")
    argparser.add_argument("-2", "--python2",
        help="use python2 instead of python3 (default)",
        action="store_true")
    argparser.add_argument("-e", "--entry-point",
        type=str, 
        help="Specify entry point. Default is ./main.by",
        nargs=1)
    argparser.add_argument("-o", "--output",
        type=str, 
        help="specify name of output directory",
        nargs=1)
    argparser.add_argument("input",
        type=str, 
        help="directory to parse",
        nargs=1)
   #argparser.add_argument("args",
   #    type=str,
   #    help="arguments to script",
   #    nargs=argparse.REMAINDER)

    # Parse arguments
    cmd_args = argparser.parse_args()

    if(cmd_args.verbose != None):
        if cmd_args.verbose[0].lower() == "debug":
            logger.setLevel(logging.DEBUG)
        elif cmd_args.verbose[0].lower() == "info":
            logger.setLevel(logging.INFO)
        elif cmd_args.verbose[0].lower() == "warning":
            logger.setLevel(logging.WARNING)
        elif cmd_args.verbose[0].lower() == "error":
            logger.setLevel(logging.ERROR)
        elif cmd_args.verbose[0].lower() == "critical":
            logger.setLevel(logging.CRITICAL)
        else:
            print("Invalid verbosity level. Using none.")


    # Ensure existence of a build directory
    if cmd_args.output == None:
        cmd_args.output = ["build/"]
    elif not cmd_args.output[0].endswith("/"):
        cmd_args.output[0] = cmd_args.output[0] + "/" #eehhh not great ill fix later

    # Delete Build Directory
    try:
        shutil.rmtree(cmd_args.output[0])
    except PermissionError:
        print("Permission denied. Unable to delete the directory.")
        sys.exit(1)
    except:
        pass

    # Ensure existence of entry point
    if cmd_args.entry_point == None:
        cmd_args.entry_point = ["main.py"]
    
    # We are parsing a single file
    if cmd_args.input[0].endswith(".by"):
        logger.info(f"Parsing {cmd_args.input[0]}")
        Path(cmd_args.output[0]).mkdir()
        parser.parse_file(cmd_args.input[0], cmd_args.output[0]+"main.py", cmd_args.truefalse)
        logger.info(f"Wrote {cmd_args.input[0]} to {cmd_args.output[0]+"main.py"}")
        if not cmd_args.compile:
            logger.info(f"Running `python build/main.py`")
            subprocess.run(["python", "build/main.py"])
        return

    # we are not parsing a single file, so do the whole directory thing
    tld = Path(cmd_args.input[0])
    files = list(tld.glob("**/*"))

    for i in files:
        source_file = str(i)
        dest_file = cmd_args.output[0]+"/".join(str(i).split("/")[1:])
        #print(source_file, "->", dest_file)
        # just copy it over
        subprocess.run(["mkdir", "-p", "/".join(dest_file.split("/")[0:-1]) ])
        if not str(i).endswith(".by"):
            # its ok if this fails. It only fails on directories, which are made in the previous line
            subprocess.run(["cp", source_file, dest_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Copied {source_file} to {dest_file}")
        else:
            dest_file = dest_file[0:-3] + ".py"
            parser.parse_file(source_file, dest_file, cmd_args.truefalse)
            logger.info(f"Parsed {source_file} to {dest_file}")
    
    if not cmd_args.compile:
        logger.info(f"Running `python {cmd_args.output[0]+cmd_args.entry_point[0]}`")
        subprocess.run(["python", cmd_args.output[0]+cmd_args.entry_point[0]])

if __name__ == '__main__':
    main()
