# An introduction to Bython
This document gives a more thorough introduction to Bython.

## Table of contents

  * [0 - Installation](#0---installation)
  * [1 - The basics](#1---the-basics)
    * [1.1 - Running your program](#11---running-your-program)
    * [1.2 - Keeping generated Python files](#12---keeping-generated-python-files)
    * [1.3 - Different Python versions](#13---different-python-versions)
 * [2 - Additional Features](#2---additional-features)
    * [2.1 - and and or](#21---and-and-or)
    * [2.2 - true and false](#22---true-and-false)
  * [3 - Imports](#3---imports)
    * [3.1 - Importing Bython modules in Bython code](#31---importing-bython-modules-in-bython-code)
    * [3.2 - Importing Bython modules in Python code](#32---importing-bython-modules-in-python-code)
  * [4 - Python files](#4---python-files)
    * [4.1 - Formatting of resulting Python files](#41---formatting-of-resulting-python-files)
    * [4.2 - Translating Python to Bython](#42---translating-python-to-bython)


# 0 - Installation
Bython is available from PyPI, so a call to pip should do the trick:

``` bash
$ git clone https://github.com/prushton2/bython
$ sudo make install
```

Bython should now be available from the shell.

# 1 - The basics
Bython is pretty much Python, but instead of using colons and indentation to create blocks of code, we instead use curly braces. A simple example of some Bython code should make this clear:

``` python
import numpy as np
import matplotlib.pyplot as plt

def plot_sine_wave(xmin=0, xmax=2*np.pi, points=100, filename=None) {
    xs = np.linspace(xmin, xmax, points)
    ys = np.sin(xs)

    plt.plot(xs, ys)

    if (filename is not None) {
        plt.savefig(filename)
    }

    plt.show()
}

if (__name__ == "__main__") {
    plot_sine_wave()
}
```

Curly braces are used whenever colons and indentation would be used in regular Python, ie function/class definitions, loops, if-statements, ...

As you can see in the example above, importing modules from Python is no issue. All packages installed with your normal Python installation is available in Bython as well. 


## 1.1 - Running your program
Say we have written the above program, and saved it as `test.by`. To parse and run the program, use the `bython` command in the shell
``` bash
bython test.by
```
A plot containing one period of a sine wave should appear.


## 1.2 - Keeping generated Python files
Bython works by first translating your Bython files to regular Python, and then use Python to run it These files are stored in `build` by default. After running, the created Python files are deleted. If you want to keep the created files, use the `-c` (c for 'compile') flag:
``` bash
bython -c test.by
```
and then run the python file with
```bash
python build/main.py
```

When transpiling a single file, bython will rename it to `main.py` automatically

If you want more control on the resulting output directory, you can use the `-o` flag to specify the output file:
``` bash
bython -c -o out test.by
```

## 1.3 - Different Python versions
Bython is written in Python 3, so you need a working installation of Python 3.x to run Bython. Your Bython files, however, can be run in whatever Python version you prefer. The standard is Python 3 (ie, Bython will use the env command `python3` to run your program), but if you for legacy reasons want to run Python 2 instead, you can use the `-2` flag to do that:
``` bash
bython -2 test.by
```

# 2 - Additional Features
Bython is created to add braces to python, but gives some extra features aswell

## 2.1 - and and or
Bython will, by default, translate `&&` and `||` to `and` and `or`. This means that
```python
a = True
b = False
print(a and b)
print(a or b)
```
functions the same as

```python
a = True
b = False
print(a && b)
print(a || b)
```


## 2.2 - true and false
Bython will optionally translate `true`, `false`, and `null` to `True`, `False`, and `None`. Enable this with `-t`. 

For example:
```bash
bython test.by -t
```
will transpile true, false , and none.

# 3 - Imports
Bython handles imports quite well. In this section we will look at the different scenarios where imports might occur.

## 3.1 - Importing Bython modules in Bython code
Importing Bython is currently something to keep in mind. When importing, you need to remember that all imported files need to be in .py at runtime. This means you can import .py or .by files to bython, but remember to transpile all .by files before running.

src/main.by:
``` python
import test_module
import py_module

test_module.func()
py_module.func()
```

src/test_module.by:
``` python
def func() {
    print("hello from bython!")
}
```

src/py_module.py:
``` python
def func():
    print("hello from python!")
```

To run, transpile the entire directory:
```bash
bython -o dist src -e src/main.py
```

Since bython only transpiles .by files, this will work. The `-e` refers to the entry point, and should be specified as.py. This is the file bython will run after transpiling.

## 3.2 - Importing Bython modules in Python code
Importing Bython code into Python is quite simple really. You just reference the .by file as if it were python, and make sure the bython file is transpiled at runtime.


src/main.py:
``` python
import by_module

by_module.func()
```

src/by_module.by:
``` python
def func() {
    print("hello from bython!")
}
```

To run, transpile the entire directory as done before:
```bash
bython -o dist src -e src/main.py
```

# 4 - Python files

## 4.1 - Formatting of resulting Python files
Bython has some weird quirks when transpiling. It may insert random newlines or indents at the end of lines. This is something i am working on fixing, and I would like for the line numbers in file to match up.

## 4.2 - Translating Python to Bython
If you want to translate Python code to Bython, you can use the built-in `py2by` script. It's an experimental feature, but seems to work quite well. 