#! /usr/bin/env python3
import argparse
import os
import sys
import shutil
import subprocess
import logging

from pathlib import Path
from . import parser

VERSION_NUMBER = "1.1.6"
logging.basicConfig(format='%(funcName)s: %(message)s')
logger = logging.getLogger()

"""
Bython is Python with braces.

This is a command-line utility to translate and run bython files.

Flags and arguments:
    -v, --version:      Print version number
    -V, --verbose:      Print progress
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
    argparser.add_argument("-v", "--version", 
        action="version", 
        version="Bython v{}\nRewritten by Peter Rushton\nOriginally by Mathias Lohne and Tristan Pepin 2018\n".format(VERSION_NUMBER))
    argparser.add_argument("-V", "--verbose", 
        type=str,
        help="Specify a verbosity level for debugging (debug, info, warning, error, critical)",
        nargs=1) 
    argparser.add_argument("-k", "--keep", 
        help="Keeps the generated python file when transpiling one file",
        action="store_true")
    argparser.add_argument("-t", "--truefalse",
        help="adds support for lower case true/false, aswell as null for None",
        action="store_true")
    argparser.add_argument("-2", "--python2",
        help="use python2 instead of python3 (default)",
        action="store_true")
    argparser.add_argument("-e", "--entry-point",
        type=str, 
        help="Specify entry point for transpiling a directory, no entry point will only transpile the files",
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

    logger.setLevel(logging.ERROR)

    if(cmd_args.verbose != None):
        if cmd_args.verbose[0].lower() == "debug":
            logger.setLevel(logging.DEBUG)
        elif cmd_args.verbose[0].lower() == "info":
            logger.setLevel(logging.INFO)
        elif cmd_args.verbose[0].lower() == "warning":
            logger.setLevel(logging.WARNING)
        else:
            print("Invalid verbosity level. Using Error.")


    # Ensure existence of a build directory
    if cmd_args.output == None:
        cmd_args.output = ["build/"]

    # Delete Build Directory
    try:
        shutil.rmtree(cmd_args.output[0])
    except PermissionError:
        logger.critical("Permission denied. Unable to delete the directory.")
        sys.exit(1)
    except:
        pass
    
    # We are parsing a single file
    if cmd_args.input[0].endswith(".by"):
        logger.info(f"Parsing {cmd_args.input[0]}")
        os.makedirs(Path(cmd_args.output[0]))
        
        parser.parse_file(cmd_args.input[0], os.path.join(cmd_args.output[0], "main.py"), cmd_args.truefalse)
        logger.info(f"Wrote {cmd_args.input[0]} to {os.path.join(cmd_args.output[0], "main.py")}")
        
        logger.info(f"Running `python {os.path.join(cmd_args.output[0], "main.py")}`")
        subprocess.run(["python", os.path.join(cmd_args.output[0], "main.py")])

        if not cmd_args.keep:
            logger.info(f"Deleting {cmd_args.output[0]}")
            shutil.rmtree(cmd_args.output[0])
        
        return

    # we are not parsing a single file, so do the whole directory thing
    tld = Path(cmd_args.input[0])
    files = list(tld.glob("**/*"))

    for source_file in files:
        # We remove the part of the path specified in the command line, so we are left with the relative path to the source directory
        # ex: ../tests/bython/test1/src/liba/main.by -> liba/main.by
        source_file_name = str(source_file)[len(str(tld))+1:] 
        
        # This is the file we are going to write to
        # ex: liba/main.by -> ../tests/bython/test1/build/liba/main.py
        dest_file = os.path.join(cmd_args.output[0], source_file_name)
        
        # print(f"File Info:\n    source_file {source_file}\n    dest_file {dest_file}\n    source_file_name {source_file_name}")
        
        try:
            os.makedirs("/".join(dest_file.split("/")[0:-1]), exist_ok=True)
        except Exception as e:
            logger.critical(f"Failed to create directory {"/".join(dest_file.split("/")[0:-1])}: {e}")
            sys.exit(1)


        if not str(source_file).endswith(".by"):
            # its ok if this fails. It only fails on directories, which are made in the previous line
            subprocess.run(["cp", source_file, dest_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Copied {source_file} to {dest_file}")
        else:
            dest_file = dest_file[0:-3] + ".py"
            parser.parse_file(source_file, dest_file, cmd_args.truefalse)
            logger.info(f"Parsed {source_file} to {dest_file}")
    
    if cmd_args.entry_point:
        logger.info(f"Running `python {cmd_args.output[0]+cmd_args.entry_point[0]}`")
        subprocess.run(["python", cmd_args.output[0]+cmd_args.entry_point[0]])

if __name__ == '__main__':
    main()
