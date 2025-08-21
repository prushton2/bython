# An introduction to Bython
This document gives a more thorough introduction to Bython.

## Table of contents

  * [0 - Installation](#0---installation)
  * [1 - The basics](#1---the-basics)
    * [1.1 - Running your program](#11---running-your-program)
    * [1.2 - Keeping generated Python files](#12---keeping-generated-python-files)
 * [2 - Additional Features](#2---additional-features)
    * [2.1 - and and or](#21---and-and-or)
    * [2.2 - true, false, and null](#22---true-false-and-null)
  * [3 - Imports](#3---imports)
  * [4 - Formatting of resulting Python files](#4---formatting-of-resulting-python-files)


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
python -m bython-prushton test.by
```
A plot containing one period of a sine wave should appear.


## 1.2 - Keeping generated Python files
Bython works by first translating your Bython files to regular Python, and then use Python to run it. These files are stored in `build` by default. After running, the created Python files are deleted. If you want to keep the created files when transpiling a single file, use the `-k` flag:
``` bash
python -m bython-prushton -k test.by
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


## 2.2 - true, false, and null
Bython will optionally translate `true`, `false`, and `null` to `True`, `False`, and `None`. Enable this with `-t`. 

For example:
```bash
python -m bython-prushton test.by -t
```
will transpile true, false, and none.

# 3 - Imports
Bython imports are cross compatible with Python files. Since the transpiler only modifies .by files, you can import .py files with no issue. Just remember that all bython files must be transpiled at runtime.

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
python -m bython-prushton -o dist src -e src/main.py
```

Note that the entry point must be specified as a .py file, regardless of if it is written in python or bython.

# 4 - Formatting of resulting Python files
Bython does not respect the line the source code is on when transpiling. It will remove empty lines and may compress some lines together when possible. This means that the line number for errors wont match up. I recommend checking the transpiled code for the error and fixing it in the main code.