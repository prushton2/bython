#! /usr/bin/env python3
import argparse
import os
import sys
import shutil
import subprocess

from pathlib import Path

import parser
VERSION_NUMBER = "1.0"
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
        version="Bython v{}\nOriginally by Mathias Lohne and Tristan Pepin 2018\nForked by prushton2".format(VERSION_NUMBER))
    argparser.add_argument("-v", "--verbose", 
        help="print progress",
        action="store_true") 
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
    
    Path("./build").mkdir(parents=True,exist_ok=True)

    # Copy source dir to build dir
    subprocess.run(["cp", "-r", cmd_args.input[0]+"/", cmd_args.output[0]]+"/")

    # Iterate over all files, converting them to .py
    tld = Path(cmd_args.output[0])
    source_files = list(tld.glob("**/*.by"))

    #this happens when a file is given, rather than a directory
    if source_files == []: 
        parser.parse_file(str(tld),"./"+cmd_args.output[0]+"main.py", cmd_args.truefalse)
        shutil.rm("./"+cmd_args.output[0]+"main.by");

        if not cmd_args.compile:
            subprocess.run(["python", "./"+cmd_args.output[0]+"main.py"])
            shutil.rmtree(cmd_args.output[0])
        sys.exit(1) #exit when done
    
    #assuming the above guard clause didnt run, we have a directory.
    for i in source_files:
        dest_file = str(i)
        
        if str(i).startswith(str(tld)): # remove preceeding file path
            dest_file = str(i)[len(str(tld))+1:]
        dest_file = Path(cmd_args.output[0] + dest_file) #add output directory

        #mkdir -p equivalent so parser doesnt fail
        dest_file.mkdir(parents=True, exist_ok=True)
        
        dest_file.rmdir() # remove ending directory so file can be put there

        dest_file_string = str(dest_file)[0:-3] + ".py"

        parser.parse_file(str(i), dest_file_string, cmd_args.truefalse)

    if not cmd_args.compile:
        if not os.path.isfile("./"+cmd_args.output[0]+cmd_args.entry_point[0]):
            print("Entry point file not found ("+"./"+cmd_args.output[0]+cmd_args.entry_point[0]+")\n\nSet the entry point with --entry-point\n")
            sys.exit(1)
        subprocess.run(["python", "./"+cmd_args.output[0]+cmd_args.entry_point[0]])

if __name__ == '__main__':
    main()
