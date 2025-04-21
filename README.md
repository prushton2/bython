# Bython
Python with braces. Because Python is awesome, but whitespace is awful.

Bython is a Python preprosessor which translates curly braces into indentation.

## Key features

* Write Python using braces instead of whitespace, and use the transpiler to convert it to valid Python code
  * Transpiles curly braces while keeping maps, fstrings, and curlies inside strings intact
* Allows for translation of `&&` and `||` to `and` and `or`
* Can optionally translate `true` and `false` to `True` and `False`

## Code example

```python
myMap = {
    "status": "awesome!"
}

def print_message(num_of_times) {
    for i in range(num_of_times) {
        print(f"Bython is {myMap["status"]}");
    }
}

if __name__ == "__main__" {
    print_message(10);
}
```


## Installation

### Linux
Prerequisites:
* Python
* Pyinstaller

Clone the repo with
```
$ git clone https://github.com/prushton2/bython
```

Using the makefile, run
```
$ sudo make install
```

This installs `/bin/bython` and `/bin/py2by`

To uninstall, run
```
sudo make uninstall
```
### Windows / Mac
I dont use these operating systems, if you want to write an install recipe for them please do!

## Quick intro

Bython works by first translating Bython-files (required file ending: .by) into Python-files, and then using Python to run them. You therefore need a working installation of Python for Bython to work.


To run a Bython program, simply type

```
$ bython source.by arg1 arg2 ...
```

to run `source.by` with arg1, arg2, ... as command line arguments. If you want more details on how to run Bython files (flags, etc), type

```
$ bython -h
```

To transpile an entire directory, run bython with the `-o` to specify the output directory, and `-e` to specify the entry point. 

```
$ bython -o dist -e main.py src
```

To transpile without running, use the `-c` argument to specify compile without running. Using this with the `-e` argument does not work. You can also include `-t` to translate lowercase booleans to uppercase and null to None

```
$ bython -o dist -c -t src
```

## Contributing

### Code

If you want to contribute, make sure to install
* Python
* Colorama

All source code is located in `src`
* `src/bython.py` handles the command line arguments
* `src/parser.py` handles tokenizing and parsing files
* `src/py2by.py` parses python to bython and could use some help

testcases only test bython conversions, and are structured as follows:

`<test name>` <br>
 |-`main.by`  Bython code to convert<br>
 |-`expected_out.txt` Expexted out when running the bython<br>
 |-`build/` Dir for transpiled python code

 run `make test` to run bython tests

### Installation
If you want to write an install recipe for windows or mac, please feel free. I cannot write these scripts myself as I have neither.