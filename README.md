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

Install from pip

```
$ python -m pip install bython-prushton
```

## Quick intro

Bython works by first translating Bython-files (required file ending: .by) into Python-files, and then using Python to run them. You therefore need a working installation of Python for Bython to work.


To run a Bython program, simply type

```
$ python -m bython-prushton source.by 
```

to run `source.by`. If you want more details on how to run Bython files (flags, etc), type

```
$ python -m bython-prushton -h
```

To transpile an entire directory, run bython with the `-o` to specify the output directory, and `-e` to specify the entry point. 

```
$ python -m bython-prushton -o dist -e main.py src
```

To transpile without running, omit the `-e` argument. You can also include `-t` to translate lowercase booleans to uppercase and null to None

```
$ python -m bython-prushton -o dist -t src
```

## Contributing

### Code

If you want to contribute, make sure to install
* Python
* Colorama

All source code is located in `src`
* `src/bython-prushton/bython.py` handles the command line arguments
* `src/bython-prushton/parser.py` handles tokenizing and parsing files
* `src/bython-prushton/py2by.py` parses python to bython and could use some help

testcases have two structures for testing the parser and the cli:

```
bython
|-<test name>
|  |-src                  Bython code to convert
|  |-expected_out.txt     Expected out when running the bython
|  |-info.json            Info on how to run the test
|  |-build/               Dir for transpiled python code
parser
|-<test name> 
|  |-main.by              Bython code to convert<br>
|  |-expected_out.txt     Expected out when running the bython
|  |-build/               Dir for transpiled python code
```

run `make test` to run bython tests
