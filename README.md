# Bython
Python with braces. Because Python is awesome, but whitespace is awful.

Bython is a Python preprosessor which translates curly brackets into indentation.


## Content of README:
  * [Key features](#key-features)
  * [Code example](#code-example)
  * [Installation](#installation)
  * [Quick intro](#quick-intro)
  * [Structure of the repository](#structure-of-the-repository)


## Key features

* Write Python using braces instead of whitespace, and use the transpiler to convert it to valid Python code
* Allows for translation of `&&` and `||` to `and` and `or`
* Can optionally translate `true` and `false` to `True` and `False`

## Code example

```python
def print_message(num_of_times) {
    for i in range(num_of_times) {
        print("Bython is awesome!");
    }
}

if __name__ == "__main__" {
    print_message(10);
}
```


## Installation

Clone the repo with
`git clone https://github.com/prushton2/bython`

# Linux
Using the makefile, run
`sudo make install`


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

To transpile without running, use the `-c` argument to specify compile without running. Using this with the `-e` argument does not work. You can also include `-t` to translate lowercase booleans to uppercase

```
$ bython -o dist -c -t src
```
